// @bun
// src/server.ts
import { Database } from "bun:sqlite";
import { join } from "path";
import { homedir } from "os";
import { writeFileSync, mkdirSync } from "fs";
var DB_PATH = join(homedir(), ".local", "share", "opencode", "opencode.db");
var HUD_FILE = join(homedir(), ".local", "share", "opencode", "token_hud.txt");
var USD_TO_RMB = 7.2;
var DAILY_BUDGET = 10;
var MONTHLY_BUDGET = 200;
var SESSION_LARGE_THRESHOLD = 1e7;
var PROGRESS_WIDTH = 16;
function formatTokens(n) {
  if (n >= 1e6)
    return `${(n / 1e6).toFixed(1)}M`;
  if (n >= 1000)
    return `${Math.round(n / 1000)}K`;
  return String(n);
}
function thinBar(value, max) {
  const width = PROGRESS_WIDTH;
  const ratio = max > 0 ? Math.min(value / max, 1) : 0;
  const filled = Math.floor(ratio * width);
  const fill = "\u2501";
  const empty = "\u2500";
  const pointer = "\u2578";
  if (filled >= width)
    return fill.repeat(width);
  if (filled === 0)
    return "\u257A" + empty.repeat(width - 1);
  return fill.repeat(filled) + pointer + empty.repeat(width - filled - 1);
}
function thresholdLabel(ratio) {
  if (ratio > 0.8)
    return "CRITICAL";
  if (ratio > 0.5)
    return "WARNING";
  return "OK";
}
function querySessions() {
  try {
    const db = new Database(DB_PATH, { readonly: true });
    const stmt = db.prepare(`
      SELECT tokens_input, tokens_output, tokens_reasoning,
             tokens_cache_read, tokens_cache_write, cost, time_created
      FROM session
      ORDER BY time_created DESC
    `);
    const rows = stmt.all();
    db.close();
    return rows;
  } catch {
    return [];
  }
}
function buildHudText() {
  const rows = querySessions();
  if (rows.length === 0)
    return `MERCURY TOKEN ARCHIVE
No sessions found.`;
  const now = new Date;
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).getTime();
  const todayRows = rows.filter((r) => r.time_created >= todayStart);
  const monthRows = rows.filter((r) => r.time_created >= monthStart);
  const sum = (arr, fn) => arr.reduce((s, r) => s + fn(r), 0);
  const monthInput = sum(monthRows, (r) => r.tokens_input || 0);
  const monthCacheRead = sum(monthRows, (r) => r.tokens_cache_read || 0);
  const monthCacheWrite = sum(monthRows, (r) => r.tokens_cache_write || 0);
  const current = rows[0];
  const sessionTokens = (current.tokens_input || 0) + (current.tokens_output || 0) + (current.tokens_reasoning || 0);
  const dailyRmb = sum(todayRows, (r) => r.cost || 0) * USD_TO_RMB;
  const monthlyRmb = sum(monthRows, (r) => r.cost || 0) * USD_TO_RMB;
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
  const daysElapsed = now.getDate();
  const eomRmb = daysElapsed > 0 ? monthlyRmb / daysElapsed * daysInMonth : 0;
  const cacheRate = monthInput + monthCacheWrite + monthCacheRead > 0 ? monthCacheRead / (monthInput + monthCacheWrite + monthCacheRead) * 100 : 0;
  const dailyRatio = dailyRmb / DAILY_BUDGET;
  const monthlyRatio = monthlyRmb / MONTHLY_BUDGET;
  const sessionRatio = sessionTokens / SESSION_LARGE_THRESHOLD;
  const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  const cacheLabel = cacheRate >= 90 ? "excellent" : cacheRate >= 70 ? "good" : "low";
  return [
    `MERCURY TOKEN ARCHIVE`,
    `USAGE LEDGER // ${ym}`,
    `\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500`,
    `\u65E5\u9884\u7B97  ${thinBar(dailyRmb, DAILY_BUDGET)}  ${Math.round(dailyRatio * 100)}%  \xA5${dailyRmb.toFixed(1)}  ${thresholdLabel(dailyRatio)}`,
    `\u6708\u9884\u7B97  ${thinBar(monthlyRmb, MONTHLY_BUDGET)}  ${Math.round(monthlyRatio * 100)}%  \xA5${monthlyRmb.toFixed(1)}  ${thresholdLabel(monthlyRatio)}`,
    `\u4F1A\u8BDD\u91CF  ${thinBar(sessionTokens, SESSION_LARGE_THRESHOLD)}  ${formatTokens(sessionTokens)}  ${thresholdLabel(sessionRatio)}`,
    `\u7F13\u5B58\u7387  ${thinBar(cacheRate, 100)}  ${cacheRate.toFixed(0)}%  ${cacheLabel}`,
    `\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500`,
    `\u4ECA\u65E5 ${todayRows.length} \u6B21 \xB7 \u672C\u6708 \xA5${monthlyRmb.toFixed(1)} \xB7 \u6708\u672B \xA5${eomRmb.toFixed(0)}`
  ].join(`
`);
}
function writeHudFile() {
  try {
    mkdirSync(join(homedir(), ".local", "share", "opencode"), { recursive: true });
    writeFileSync(HUD_FILE, buildHudText(), "utf-8");
  } catch {}
}
var server_default = async () => {
  writeHudFile();
  return {
    event: async ({ event }) => {
      if (event.type === "session.created" || event.type === "session.idle") {
        setTimeout(() => writeHudFile(), 1000);
      }
    }
  };
};
export {
  server_default as default
};
