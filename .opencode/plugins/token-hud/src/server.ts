/**
 * token-hud — Server plugin entry (no-op, required by OpenCode loader)
 * Actual TUI rendering is in tui/index.js
 */

import type { Plugin } from "@opencode-ai/plugin"
import { Database } from "bun:sqlite"
import { join } from "path"
import { homedir } from "os"
import { writeFileSync, mkdirSync } from "fs"

const DB_PATH = join(homedir(), ".local", "share", "opencode", "opencode.db")
const HUD_FILE = join(homedir(), ".local", "share", "opencode", "token_hud.txt")
const USD_TO_RMB = 7.2
const DAILY_BUDGET = 10.0
const MONTHLY_BUDGET = 200.0
const SESSION_LARGE_THRESHOLD = 10_000_000
const PROGRESS_WIDTH = 16

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
  if (ratio > 0.8) return "CRITICAL"
  if (ratio > 0.5) return "WARNING"
  return "OK"
}

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

function buildHudText(): string {
  const rows = querySessions()
  if (rows.length === 0) return "MERCURY TOKEN ARCHIVE\nNo sessions found."

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

  const dailyRatio = dailyRmb / DAILY_BUDGET
  const monthlyRatio = monthlyRmb / MONTHLY_BUDGET
  const sessionRatio = sessionTokens / SESSION_LARGE_THRESHOLD
  const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
  const cacheLabel = cacheRate >= 90 ? "excellent" : cacheRate >= 70 ? "good" : "low"

  return [
    `MERCURY TOKEN ARCHIVE`,
    `USAGE LEDGER // ${ym}`,
    `──────────────────────────────`,
    `日预算  ${thinBar(dailyRmb, DAILY_BUDGET)}  ${Math.round(dailyRatio * 100)}%  ¥${dailyRmb.toFixed(1)}  ${thresholdLabel(dailyRatio)}`,
    `月预算  ${thinBar(monthlyRmb, MONTHLY_BUDGET)}  ${Math.round(monthlyRatio * 100)}%  ¥${monthlyRmb.toFixed(1)}  ${thresholdLabel(monthlyRatio)}`,
    `会话量  ${thinBar(sessionTokens, SESSION_LARGE_THRESHOLD)}  ${formatTokens(sessionTokens)}  ${thresholdLabel(sessionRatio)}`,
    `缓存率  ${thinBar(cacheRate, 100)}  ${cacheRate.toFixed(0)}%  ${cacheLabel}`,
    `──────────────────────────────`,
    `今日 ${todayRows.length} 次 · 本月 ¥${monthlyRmb.toFixed(1)} · 月末 ¥${eomRmb.toFixed(0)}`,
  ].join("\n")
}

function writeHudFile() {
  try {
    mkdirSync(join(homedir(), ".local", "share", "opencode"), { recursive: true })
    writeFileSync(HUD_FILE, buildHudText(), "utf-8")
  } catch {}
}

export default (async () => {
  writeHudFile()

  return {
    event: async ({ event }) => {
      if (event.type === "session.created" || event.type === "session.idle") {
        setTimeout(() => writeHudFile(), 1000)
      }
    },
  }
}) satisfies Plugin
