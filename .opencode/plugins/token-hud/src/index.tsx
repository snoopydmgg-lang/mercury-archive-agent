/**
 * token-hud — OpenCode TUI Plugin: Mercury Archive Dashboard
 *
 * Full card-style dashboard in sidebar_footer slot:
 *   SESSION → CONTEXT → LSP → MODIFIED FILES → TOKEN ARCHIVE
 *
 * Mercury Archive palette: #D36B4D accent / #8A8580 muted / #E6C8B5 soft
 * Visual: neoclassical humanism, archival card feel, thin borders,
 *         no heavy shadows, no neon, no emoji overload.
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
const PROGRESS_WIDTH = 14
const MAX_FILES = 6

// Mercury Archive palette
const ACCENT = "#D36B4D"
const MUTED = "#8A8580"
const SOFT = "#E6C8B5"

// ── Helpers ──

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${Math.round(n / 1_000).toLocaleString()}K`
  return n.toLocaleString()
}

function thinBar(value: number, max: number): string {
  const width = PROGRESS_WIDTH
  const ratio = max > 0 ? Math.min(value / max, 1) : 0
  const filled = Math.floor(ratio * width)
  const fill = "━"     // ━
  const empty = "─"    // ─
  const pointer = "╸"  // ╸
  const pointerL = "╺" // ╺
  if (filled >= width) return fill.repeat(width)
  if (filled === 0) return pointerL + empty.repeat(width - 1)
  return fill.repeat(filled) + pointer + empty.repeat(width - filled - 1)
}

function thresholdColor(ratio: number): string {
  if (ratio > 0.8) return ACCENT
  if (ratio > 0.5) return SOFT
  return MUTED
}

function thresholdLabel(ratio: number): string {
  if (ratio > 0.8) return "CRIT"
  if (ratio > 0.5) return "WARN"
  return "OK"
}

function truncatePath(path: string, maxLen: number): string {
  if (path.length <= maxLen) return path
  const parts = path.split("/")
  if (parts.length <= 2) return path.slice(0, maxLen - 3) + "..."
  const file = parts[parts.length - 1]
  if (file.length >= maxLen - 4) return "..." + file.slice(-(maxLen - 3))
  const prefix = parts[0]
  return prefix + "/.../" + file
}

function padRight(str: string, len: number): string {
  const visible = str.replace(/[─-╿▀-▟]/g, "?").length
  return str + " ".repeat(Math.max(0, len - visible))
}

function formatTime(ts: number): string {
  const d = new Date(ts)
  const h = String(d.getHours()).padStart(2, "0")
  const m = String(d.getMinutes()).padStart(2, "0")
  return `${h}:${m}`
}

// ── Database queries (fallback for aggregate data) ──

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

// ── Build HUD text (for file output, no-color) ──

function buildHudText(): string {
  const data = computeHudData()
  const now = new Date()
  const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
  const cacheLabel = data.cacheRate >= 90 ? "excellent" : data.cacheRate >= 70 ? "good" : "low"

  return [
    `MERCURY TOKEN ARCHIVE`,
    `USAGE LEDGER // ${ym}`,
    `─`.repeat(30),
    `日预算  ${thinBar(data.dailyRmb, DAILY_BUDGET)}  ${Math.round(data.dailyRatio * 100)}%  \xA5${data.dailyRmb.toFixed(1)}  ${thresholdLabel(data.dailyRatio)}`,
    `月预算  ${thinBar(data.monthlyRmb, MONTHLY_BUDGET)}  ${Math.round(data.monthlyRatio * 100)}%  \xA5${data.monthlyRmb.toFixed(1)}  ${thresholdLabel(data.monthlyRatio)}`,
    `会话量  ${thinBar(data.sessionTokens, SESSION_LARGE_THRESHOLD)}  ${formatTokens(data.sessionTokens)}  ${thresholdLabel(data.sessionRatio)}`,
    `缓存率  ${thinBar(data.cacheRate, 100)}  ${data.cacheRate.toFixed(0)}%  ${cacheLabel}`,
    `─`.repeat(30),
    `今日 ${data.todayCount} 次 \xB7 本月 \xA5${data.monthlyRmb.toFixed(1)}`,
    `月末预测 \xA5${data.eomRmb.toFixed(0)}`,
  ].join("\n")
}

function writeHudFile(text: string) {
  try {
    mkdirSync(join(homedir(), ".local", "share", "opencode"), { recursive: true })
    writeFileSync(HUD_FILE, text, "utf-8")
  } catch {}
}

// ── Card component ──

function Card(props: { title: string; children: any }) {
  return (
    <box
      flexDirection="column"
      border
      borderStyle="single"
      borderColor={MUTED}
      paddingX={1}
      marginBottom={1}
    >
      <box flexShrink={0}>
        <text bold fg={ACCENT}>{props.title}</text>
      </box>
      {props.children}
    </box>
  )
}

// ── TUI Plugin ──

export default {
  id: "token-hud",
  tui: async (api: TuiPluginApi) => {
    console.error("[token-hud] TUI plugin mounting...")

    writeHudFile(buildHudText())

    api.slots.register({
      slots: {
        sidebar_footer(props: { session_id: string }) {
          // ── Reactive data ──
          const [hudData, setHudData] = createSignal(computeHudData())
          const [tick, setTick] = createSignal(0)

          onMount(() => {
            console.error("[token-hud] sidebar_footer mounted")
            const id = setInterval(() => {
              setHudData(computeHudData())
              setTick(t => t + 1)
              writeHudFile(buildHudText())
            }, 30_000)
            onCleanup(() => clearInterval(id))
          })

          const d = () => hudData()

          // ── Session info (from api.state) ──
          const session = () => {
            try {
              return api.state.session.get(props.session_id)
            } catch {
              return undefined
            }
          }

          const sessionTitle = () => {
            const s = session()
            if (!s) return null
            return s.title || null
          }

          const sessionTime = () => {
            const s = session()
            if (!s?.time?.created) return null
            return formatTime(s.time.created)
          }

          // ── Context tokens (from session.tokens) ──
          const tokens = () => {
            const s = session()
            return s?.tokens ?? null
          }

          const sessionCost = () => {
            const s = session()
            return s?.cost ? s.cost * USD_TO_RMB : 0
          }

          const totalTokens = () => {
            const t = tokens()
            if (!t) return 0
            return t.input + t.output + t.reasoning
          }

          // ── LSP status ──
          const lspItems = () => {
            try {
              return api.state.lsp()
            } catch {
              return []
            }
          }

          const lspStatus = () => {
            const items = lspItems()
            if (items.length === 0) return "Disabled"
            const active = items.filter(i =>
              i.status === "ready" || i.status === "connected"
            ).length
            if (active === items.length)
              return `Active \xB7 ${items.length} server${items.length > 1 ? "s" : ""}`
            return `${active}/${items.length} active`
          }

          // ── Modified files ──
          const files = () => {
            try {
              return api.state.session.diff(props.session_id)
            } catch {
              return []
            }
          }

          // ── Render ──
          const now = new Date()
          const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`

          return (
            <box
              flexDirection="column"
              paddingX={1}
              flexShrink={0}
              borderTop
              borderColor={MUTED}
            >
              {/* ── 1. SESSION card ── */}
              <Card title="MERCURY SESSION">
                <box flexShrink={0}>
                  {sessionTitle() ? (
                    <text fg={SOFT}>{sessionTitle()}</text>
                  ) : sessionTime() ? (
                    <text fg={MUTED}>Active \xB7 {sessionTime()}</text>
                  ) : (
                    <text fg={MUTED}>Awaiting session</text>
                  )}
                </box>
              </Card>

              {/* ── 2. CONTEXT card ── */}
              <Card title="CONTEXT">
                {tokens() ? (
                  <>
                    <box flexDirection="row" flexShrink={0}>
                      <text fg={SOFT}>{formatTokens(totalTokens())}</text>
                      <text fg={MUTED}> tokens</text>
                    </box>
                    <box flexDirection="row" flexShrink={0}>
                      <text fg={ACCENT}>{"\xA5"}{sessionCost().toFixed(2)}</text>
                      <text fg={MUTED}> spent</text>
                    </box>
                  </>
                ) : (
                  <box flexShrink={0}>
                    <text fg={MUTED}>Awaiting token data</text>
                  </box>
                )}
              </Card>

              {/* ── 3. LSP card ── */}
              <Card title="LSP">
                <box flexShrink={0}>
                  <text fg={lspItems().length > 0 ? SOFT : MUTED}>{lspStatus()}</text>
                </box>
              </Card>

              {/* ── 4. MODIFIED FILES card ── */}
              <Card title="MODIFIED FILES">
                {files().length > 0 ? (
                  <>
                    {files().slice(0, MAX_FILES).map((f) => {
                      const maxPathLen = 24
                      const displayPath = truncatePath(f.file, maxPathLen)
                      const changes = f.deletions > 0
                        ? `+${f.additions} -${f.deletions}`
                        : `+${f.additions}`
                      return (
                        <box flexDirection="row" flexShrink={0}>
                          <text fg={MUTED}>{displayPath}</text>
                          <text fg={SOFT}>{" ".repeat(Math.max(1, maxPathLen - displayPath.length))}{changes}</text>
                        </box>
                      )
                    })}
                    {files().length > MAX_FILES && (
                      <box flexShrink={0}>
                        <text fg={MUTED}>... {files().length - MAX_FILES} more files</text>
                      </box>
                    )}
                  </>
                ) : (
                  <box flexShrink={0}>
                    <text fg={MUTED}>Clean workspace</text>
                  </box>
                )}
              </Card>

              {/* ── 5. TOKEN ARCHIVE card ── */}
              <Card title="MERCURY TOKEN ARCHIVE">
                <box flexShrink={0}>
                  <text fg={MUTED} dimColor>USAGE LEDGER // {ym}</text>
                </box>

                {/* Daily */}
                <box flexDirection="row" flexShrink={0}>
                  <text fg={MUTED}>{"日预算 "}</text>
                  <text fg={thresholdColor(d().dailyRatio)}>
                    {thinBar(d().dailyRmb, DAILY_BUDGET)} {Math.round(d().dailyRatio * 100)}%
                  </text>
                  <text fg={SOFT}> {"\xA5"}{d().dailyRmb.toFixed(1)}</text>
                </box>

                {/* Monthly */}
                <box flexDirection="row" flexShrink={0}>
                  <text fg={MUTED}>{"月预算 "}</text>
                  <text fg={thresholdColor(d().monthlyRatio)}>
                    {thinBar(d().monthlyRmb, MONTHLY_BUDGET)} {Math.round(d().monthlyRatio * 100)}%
                  </text>
                  <text fg={SOFT}> {"\xA5"}{d().monthlyRmb.toFixed(1)}</text>
                </box>

                {/* Session */}
                <box flexDirection="row" flexShrink={0}>
                  <text fg={MUTED}>{"会话量 "}</text>
                  <text fg={thresholdColor(d().sessionRatio)}>
                    {thinBar(d().sessionTokens, SESSION_LARGE_THRESHOLD)} {formatTokens(d().sessionTokens)}
                  </text>
                </box>

                {/* Cache */}
                <box flexDirection="row" flexShrink={0}>
                  <text fg={MUTED}>{"缓存率 "}</text>
                  <text fg={d().cacheRate >= 70 ? SOFT : ACCENT}>
                    {thinBar(d().cacheRate, 100)} {d().cacheRate.toFixed(0)}%
                  </text>
                </box>

                {/* Summary — two lines to avoid wrapping */}
                <box flexDirection="row" flexShrink={0}>
                  <text fg={MUTED} dimColor>
                    {"今日"} {d().todayCount} {"次 \xB7 本月 \xA5"}{d().monthlyRmb.toFixed(1)}
                  </text>
                </box>
                <box flexDirection="row" flexShrink={0}>
                  <text fg={MUTED} dimColor>
                    {"月末预测 \xA5"}{d().eomRmb.toFixed(0)}
                  </text>
                </box>
              </Card>
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
