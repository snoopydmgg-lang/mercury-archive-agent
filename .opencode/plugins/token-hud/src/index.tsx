/**
 * token-hud — OpenCode TUI Plugin: Token HUD in sidebar_footer slot
 *
 * Mercury Archive style token usage display.
 * Data: OpenCode SQLite DB (~/.local/share/opencode/opencode.db)
 * Also writes token_hud.txt for external consumption.
 */

import type { TuiPlugin, TuiPluginApi } from "@opencode-ai/plugin"
import { Database } from "bun:sqlite"
import { join } from "path"
import { homedir } from "os"
import { writeFileSync, mkdirSync } from "fs"
import { createSignal, onMount, onCleanup } from "solid-js"

// ── Constants ──

const DB_PATH = join(homedir(), ".local", "share", "opencode", "opencode.db")
const HUD_FILE = join(homedir(), ".local", "share", "opencode", "token_hud.txt")
const USD_TO_RMB = 7.2
const DAILY_BUDGET = 10.0
const MONTHLY_BUDGET = 200.0
const SESSION_LARGE_THRESHOLD = 10_000_000
const PROGRESS_WIDTH = 16

// Mercury Archive palette
const MERCURY_ACCENT = "#D36B4D"
const MERCURY_MUTED = "#8A8580"
const MERCURY_SOFT = "#E6C8B5"

// ── Helpers ──

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${Math.round(n / 1_000)}K`
  return String(n)
}

function thinBar(value: number, max: number): string {
  const width = PROGRESS_WIDTH
  const ratio = max > 0 ? Math.min(value / max, 1) : 0
  const filled = Math.floor(ratio * width)
  const fill = "━"    // U+2501 filled
  const empty = "─"   // U+2500 unfilled
  const pointer = "╸" // U+2578
  if (filled >= width) return fill.repeat(width)
  if (filled === 0) return "╺" + empty.repeat(width - 1)
  return fill.repeat(filled) + pointer + empty.repeat(width - filled - 1)
}

function thresholdLabel(ratio: number): string {
  if (ratio > 0.8) return "CRIT"
  if (ratio > 0.5) return "WARN"
  return "OK"
}

function thresholdColor(ratio: number): string {
  if (ratio > 0.8) return MERCURY_ACCENT
  if (ratio > 0.5) return MERCURY_SOFT
  return MERCURY_MUTED
}

// ── Database queries ──

interface SessionRow {
  tokens_input: number
  tokens_output: number
  tokens_reasoning: number
  tokens_cache_read: number
  tokens_cache_write: number
  cost: number
  time_created: number
}

function querySessions(): SessionRow[] {
  try {
    const db = new Database(DB_PATH, { readonly: true })
    const stmt = db.prepare(`
      SELECT tokens_input, tokens_output, tokens_reasoning,
             tokens_cache_read, tokens_cache_write, cost, time_created
      FROM session
      ORDER BY time_created DESC
    `)
    const rows = stmt.all() as SessionRow[]
    db.close()
    return rows
  } catch {
    return []
  }
}

interface HudData {
  dailyRmb: number
  monthlyRmb: number
  eomRmb: number
  cacheRate: number
  sessionTokens: number
  todayCount: number
  monthCount: number
  dailyRatio: number
  monthlyRatio: number
  sessionRatio: number
}

function computeHudData(): HudData {
  const rows = querySessions()
  if (rows.length === 0) {
    return {
      dailyRmb: 0, monthlyRmb: 0, eomRmb: 0, cacheRate: 0,
      sessionTokens: 0, todayCount: 0, monthCount: 0,
      dailyRatio: 0, monthlyRatio: 0, sessionRatio: 0,
    }
  }

  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).getTime()

  const todayRows = rows.filter(r => r.time_created >= todayStart)
  const monthRows = rows.filter(r => r.time_created >= monthStart)

  const sum = (arr: SessionRow[], fn: (r: SessionRow) => number) =>
    arr.reduce((s, r) => s + fn(r), 0)

  const monthInput = sum(monthRows, r => r.tokens_input || 0)
  const monthCacheRead = sum(monthRows, r => r.tokens_cache_read || 0)
  const monthCacheWrite = sum(monthRows, r => r.tokens_cache_write || 0)

  const current = rows[0]
  const sessionTokens = (current.tokens_input || 0) + (current.tokens_output || 0) + (current.tokens_reasoning || 0)

  const dailyRmb = sum(todayRows, r => r.cost || 0) * USD_TO_RMB
  const monthlyRmb = sum(monthRows, r => r.cost || 0) * USD_TO_RMB
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
  const daysElapsed = now.getDate()
  const eomRmb = daysElapsed > 0 ? (monthlyRmb / daysElapsed) * daysInMonth : 0

  const cacheRate = monthInput + monthCacheWrite + monthCacheRead > 0
    ? monthCacheRead / (monthInput + monthCacheWrite + monthCacheRead) * 100
    : 0

  return {
    dailyRmb,
    monthlyRmb,
    eomRmb,
    cacheRate,
    sessionTokens,
    todayCount: todayRows.length,
    monthCount: monthRows.length,
    dailyRatio: dailyRmb / DAILY_BUDGET,
    monthlyRatio: monthlyRmb / MONTHLY_BUDGET,
    sessionRatio: sessionTokens / SESSION_LARGE_THRESHOLD,
  }
}

// ── Build HUD text (for file output) ──

function buildHudText(): string {
  const data = computeHudData()
  const now = new Date()
  const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
  const cacheLabel = data.cacheRate >= 90 ? "excellent" : data.cacheRate >= 70 ? "good" : "low"

  return [
    `MERCURY TOKEN ARCHIVE`,
    `USAGE LEDGER // ${ym}`,
    `──────────────────────────────`,
    `日预算  ${thinBar(data.dailyRmb, DAILY_BUDGET)}  ${Math.round(data.dailyRatio * 100)}%  ¥${data.dailyRmb.toFixed(1)}  ${thresholdLabel(data.dailyRatio)}`,
    `月预算  ${thinBar(data.monthlyRmb, MONTHLY_BUDGET)}  ${Math.round(data.monthlyRatio * 100)}%  ¥${data.monthlyRmb.toFixed(1)}  ${thresholdLabel(data.monthlyRatio)}`,
    `会话量  ${thinBar(data.sessionTokens, SESSION_LARGE_THRESHOLD)}  ${formatTokens(data.sessionTokens)}  ${thresholdLabel(data.sessionRatio)}`,
    `缓存率  ${thinBar(data.cacheRate, 100)}  ${data.cacheRate.toFixed(0)}%  ${cacheLabel}`,
    `──────────────────────────────`,
    `今日 ${data.todayCount} 次 · 本月 ¥${data.monthlyRmb.toFixed(1)} · 月末 ¥${data.eomRmb.toFixed(0)}`,
  ].join("\n")
}

function writeHudFile(text: string) {
  try {
    mkdirSync(join(homedir(), ".local", "share", "opencode"), { recursive: true })
    writeFileSync(HUD_FILE, text, "utf-8")
  } catch {}
}

// ── TUI Plugin ──

export default {
  id: "token-hud",
  tui: async (api: TuiPluginApi) => {
    // Debug: confirm plugin loaded
    console.error("[token-hud] TUI plugin mounting...")

    writeHudFile(buildHudText())

    api.slots.register({
      slots: {
        sidebar_footer() {
          const [data, setData] = createSignal(computeHudData())

          onMount(() => {
            console.error("[token-hud] sidebar_footer mounted")
            const id = setInterval(() => {
              setData(computeHudData())
              writeHudFile(buildHudText())
            }, 30_000)
            onCleanup(() => clearInterval(id))
          })

          const d = () => data()

          const now = new Date()
          const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`

          return (
            <box
              flexDirection="column"
              paddingX={1}
              flexShrink={0}
              borderTop
              borderColor={MERCURY_MUTED}
            >
              {/* Header */}
              <box flexShrink={0}>
                <text bold fg={MERCURY_ACCENT}>MERCURY TOKEN ARCHIVE</text>
              </box>
              <box flexShrink={0}>
                <text fg={MERCURY_MUTED} dimColor>USAGE LEDGER // {ym}</text>
              </box>

              {/* Daily */}
              <box flexDirection="row" flexShrink={0}>
                <text fg={MERCURY_MUTED}>{"日预算 "}</text>
                <text fg={thresholdColor(d().dailyRatio)}>
                  {thinBar(d().dailyRmb, DAILY_BUDGET)} {Math.round(d().dailyRatio * 100)}%
                </text>
                <text fg={MERCURY_SOFT}> ¥{d().dailyRmb.toFixed(1)}</text>
              </box>

              {/* Monthly */}
              <box flexDirection="row" flexShrink={0}>
                <text fg={MERCURY_MUTED}>{"月预算 "}</text>
                <text fg={thresholdColor(d().monthlyRatio)}>
                  {thinBar(d().monthlyRmb, MONTHLY_BUDGET)} {Math.round(d().monthlyRatio * 100)}%
                </text>
                <text fg={MERCURY_SOFT}> ¥{d().monthlyRmb.toFixed(1)}</text>
              </box>

              {/* Session */}
              <box flexDirection="row" flexShrink={0}>
                <text fg={MERCURY_MUTED}>{"会话量 "}</text>
                <text fg={thresholdColor(d().sessionRatio)}>
                  {thinBar(d().sessionTokens, SESSION_LARGE_THRESHOLD)} {formatTokens(d().sessionTokens)}
                </text>
              </box>

              {/* Cache */}
              <box flexDirection="row" flexShrink={0}>
                <text fg={MERCURY_MUTED}>{"缓存率 "}</text>
                <text fg={d().cacheRate >= 70 ? MERCURY_SOFT : MERCURY_ACCENT}>
                  {thinBar(d().cacheRate, 100)} {d().cacheRate.toFixed(0)}%
                </text>
              </box>

              {/* Summary */}
              <box flexDirection="row" flexShrink={0}>
                <text fg={MERCURY_MUTED} dimColor>
                  今日 {d().todayCount} 次 · 本月 ¥{d().monthlyRmb.toFixed(1)} · 月末 ¥{d().eomRmb.toFixed(0)}
                </text>
              </box>
            </box>
          )
        },
      },
    })

    // Refresh on events
    api.event.on("session.created", () => {
      console.error("[token-hud] session.created")
      writeHudFile(buildHudText())
      api.slots.refresh("sidebar_footer")
    })
    api.event.on("session.idle", () => {
      console.error("[token-hud] session.idle")
      writeHudFile(buildHudText())
      api.slots.refresh("sidebar_footer")
    })

    console.error("[token-hud] TUI plugin mounted OK")
  },
} satisfies TuiPlugin
