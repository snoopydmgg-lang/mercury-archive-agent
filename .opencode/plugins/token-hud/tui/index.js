// @bun
// src/index.tsx
import { effect as _$effect } from "@opentui/solid";
import { insert as _$insert } from "@opentui/solid";
import { createTextNode as _$createTextNode } from "@opentui/solid";
import { insertNode as _$insertNode } from "@opentui/solid";
import { setProp as _$setProp } from "@opentui/solid";
import { createElement as _$createElement } from "@opentui/solid";
import { Database } from "bun:sqlite";
import { join } from "path";
import { homedir } from "os";
import { writeFileSync, mkdirSync } from "fs";
import { createSignal, onMount, onCleanup } from "solid-js";
var DB_PATH = join(homedir(), ".local", "share", "opencode", "opencode.db");
var HUD_FILE = join(homedir(), ".local", "share", "opencode", "token_hud.txt");
var USD_TO_RMB = 7.2;
var DAILY_BUDGET = 10;
var MONTHLY_BUDGET = 200;
var SESSION_LARGE_THRESHOLD = 1e7;
var PROGRESS_WIDTH = 16;
var MERCURY_ACCENT = "#D36B4D";
var MERCURY_MUTED = "#8A8580";
var MERCURY_SOFT = "#E6C8B5";
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
    return "CRIT";
  if (ratio > 0.5)
    return "WARN";
  return "OK";
}
function thresholdColor(ratio) {
  if (ratio > 0.8)
    return MERCURY_ACCENT;
  if (ratio > 0.5)
    return MERCURY_SOFT;
  return MERCURY_MUTED;
}
function querySessions() {
  try {
    const db = new Database(DB_PATH, {
      readonly: true
    });
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
function computeHudData() {
  const rows = querySessions();
  if (rows.length === 0) {
    return {
      dailyRmb: 0,
      monthlyRmb: 0,
      eomRmb: 0,
      cacheRate: 0,
      sessionTokens: 0,
      todayCount: 0,
      monthCount: 0,
      dailyRatio: 0,
      monthlyRatio: 0,
      sessionRatio: 0
    };
  }
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
    sessionRatio: sessionTokens / SESSION_LARGE_THRESHOLD
  };
}
function buildHudText() {
  const data = computeHudData();
  const now = new Date;
  const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  const cacheLabel = data.cacheRate >= 90 ? "excellent" : data.cacheRate >= 70 ? "good" : "low";
  return [`MERCURY TOKEN ARCHIVE`, `USAGE LEDGER // ${ym}`, `\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500`, `\u65E5\u9884\u7B97  ${thinBar(data.dailyRmb, DAILY_BUDGET)}  ${Math.round(data.dailyRatio * 100)}%  \xA5${data.dailyRmb.toFixed(1)}  ${thresholdLabel(data.dailyRatio)}`, `\u6708\u9884\u7B97  ${thinBar(data.monthlyRmb, MONTHLY_BUDGET)}  ${Math.round(data.monthlyRatio * 100)}%  \xA5${data.monthlyRmb.toFixed(1)}  ${thresholdLabel(data.monthlyRatio)}`, `\u4F1A\u8BDD\u91CF  ${thinBar(data.sessionTokens, SESSION_LARGE_THRESHOLD)}  ${formatTokens(data.sessionTokens)}  ${thresholdLabel(data.sessionRatio)}`, `\u7F13\u5B58\u7387  ${thinBar(data.cacheRate, 100)}  ${data.cacheRate.toFixed(0)}%  ${cacheLabel}`, `\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500`, `\u4ECA\u65E5 ${data.todayCount} \u6B21 \xB7 \u672C\u6708 \xA5${data.monthlyRmb.toFixed(1)} \xB7 \u6708\u672B \xA5${data.eomRmb.toFixed(0)}`].join(`
`);
}
function writeHudFile(text) {
  try {
    mkdirSync(join(homedir(), ".local", "share", "opencode"), {
      recursive: true
    });
    writeFileSync(HUD_FILE, text, "utf-8");
  } catch {}
}
var src_default = {
  id: "token-hud",
  tui: async (api) => {
    console.error("[token-hud] TUI plugin mounting...");
    writeHudFile(buildHudText());
    api.slots.register({
      slots: {
        sidebar_footer() {
          const [data, setData] = createSignal(computeHudData());
          onMount(() => {
            console.error("[token-hud] sidebar_footer mounted");
            const id = setInterval(() => {
              setData(computeHudData());
              writeHudFile(buildHudText());
            }, 30000);
            onCleanup(() => clearInterval(id));
          });
          const d = () => data();
          const now = new Date;
          const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
          return (() => {
            var _el$ = _$createElement("box"), _el$2 = _$createElement("box"), _el$3 = _$createElement("text"), _el$5 = _$createElement("box"), _el$6 = _$createElement("text"), _el$7 = _$createTextNode(`USAGE LEDGER // `), _el$8 = _$createElement("box"), _el$9 = _$createElement("text"), _el$1 = _$createElement("text"), _el$10 = _$createTextNode(` `), _el$11 = _$createTextNode(`%`), _el$12 = _$createElement("text"), _el$13 = _$createTextNode(` \xA5`), _el$14 = _$createElement("box"), _el$15 = _$createElement("text"), _el$17 = _$createElement("text"), _el$18 = _$createTextNode(` `), _el$19 = _$createTextNode(`%`), _el$20 = _$createElement("text"), _el$21 = _$createTextNode(` \xA5`), _el$22 = _$createElement("box"), _el$23 = _$createElement("text"), _el$25 = _$createElement("text"), _el$26 = _$createTextNode(` `), _el$27 = _$createElement("box"), _el$28 = _$createElement("text"), _el$30 = _$createElement("text"), _el$31 = _$createTextNode(` `), _el$32 = _$createTextNode(`%`), _el$33 = _$createElement("box"), _el$34 = _$createElement("text"), _el$35 = _$createTextNode(`\u4ECA\u65E5 `), _el$36 = _$createTextNode(` \u6B21 \xB7 \u672C\u6708 \xA5`), _el$37 = _$createTextNode(` \xB7 \u6708\u672B \xA5`);
            _$insertNode(_el$, _el$2);
            _$insertNode(_el$, _el$5);
            _$insertNode(_el$, _el$8);
            _$insertNode(_el$, _el$14);
            _$insertNode(_el$, _el$22);
            _$insertNode(_el$, _el$27);
            _$insertNode(_el$, _el$33);
            _$setProp(_el$, "flexDirection", "column");
            _$setProp(_el$, "paddingX", 1);
            _$setProp(_el$, "flexShrink", 0);
            _$setProp(_el$, "borderTop", true);
            _$setProp(_el$, "borderColor", "#8A8580");
            _$insertNode(_el$2, _el$3);
            _$setProp(_el$2, "flexShrink", 0);
            _$insertNode(_el$3, _$createTextNode(`MERCURY TOKEN ARCHIVE`));
            _$setProp(_el$3, "bold", true);
            _$setProp(_el$3, "fg", "#D36B4D");
            _$insertNode(_el$5, _el$6);
            _$setProp(_el$5, "flexShrink", 0);
            _$insertNode(_el$6, _el$7);
            _$setProp(_el$6, "fg", "#8A8580");
            _$setProp(_el$6, "dimColor", true);
            _$insert(_el$6, ym, null);
            _$insertNode(_el$8, _el$9);
            _$insertNode(_el$8, _el$1);
            _$insertNode(_el$8, _el$12);
            _$setProp(_el$8, "flexDirection", "row");
            _$setProp(_el$8, "flexShrink", 0);
            _$insertNode(_el$9, _$createTextNode(`\u65E5\u9884\u7B97 `));
            _$setProp(_el$9, "fg", "#8A8580");
            _$insertNode(_el$1, _el$10);
            _$insertNode(_el$1, _el$11);
            _$insert(_el$1, () => thinBar(d().dailyRmb, DAILY_BUDGET), _el$10);
            _$insert(_el$1, () => Math.round(d().dailyRatio * 100), _el$11);
            _$insertNode(_el$12, _el$13);
            _$setProp(_el$12, "fg", "#E6C8B5");
            _$insert(_el$12, () => d().dailyRmb.toFixed(1), null);
            _$insertNode(_el$14, _el$15);
            _$insertNode(_el$14, _el$17);
            _$insertNode(_el$14, _el$20);
            _$setProp(_el$14, "flexDirection", "row");
            _$setProp(_el$14, "flexShrink", 0);
            _$insertNode(_el$15, _$createTextNode(`\u6708\u9884\u7B97 `));
            _$setProp(_el$15, "fg", "#8A8580");
            _$insertNode(_el$17, _el$18);
            _$insertNode(_el$17, _el$19);
            _$insert(_el$17, () => thinBar(d().monthlyRmb, MONTHLY_BUDGET), _el$18);
            _$insert(_el$17, () => Math.round(d().monthlyRatio * 100), _el$19);
            _$insertNode(_el$20, _el$21);
            _$setProp(_el$20, "fg", "#E6C8B5");
            _$insert(_el$20, () => d().monthlyRmb.toFixed(1), null);
            _$insertNode(_el$22, _el$23);
            _$insertNode(_el$22, _el$25);
            _$setProp(_el$22, "flexDirection", "row");
            _$setProp(_el$22, "flexShrink", 0);
            _$insertNode(_el$23, _$createTextNode(`\u4F1A\u8BDD\u91CF `));
            _$setProp(_el$23, "fg", "#8A8580");
            _$insertNode(_el$25, _el$26);
            _$insert(_el$25, () => thinBar(d().sessionTokens, SESSION_LARGE_THRESHOLD), _el$26);
            _$insert(_el$25, () => formatTokens(d().sessionTokens), null);
            _$insertNode(_el$27, _el$28);
            _$insertNode(_el$27, _el$30);
            _$setProp(_el$27, "flexDirection", "row");
            _$setProp(_el$27, "flexShrink", 0);
            _$insertNode(_el$28, _$createTextNode(`\u7F13\u5B58\u7387 `));
            _$setProp(_el$28, "fg", "#8A8580");
            _$insertNode(_el$30, _el$31);
            _$insertNode(_el$30, _el$32);
            _$insert(_el$30, () => thinBar(d().cacheRate, 100), _el$31);
            _$insert(_el$30, () => d().cacheRate.toFixed(0), _el$32);
            _$insertNode(_el$33, _el$34);
            _$setProp(_el$33, "flexDirection", "row");
            _$setProp(_el$33, "flexShrink", 0);
            _$insertNode(_el$34, _el$35);
            _$insertNode(_el$34, _el$36);
            _$insertNode(_el$34, _el$37);
            _$setProp(_el$34, "fg", "#8A8580");
            _$setProp(_el$34, "dimColor", true);
            _$insert(_el$34, () => d().todayCount, _el$36);
            _$insert(_el$34, () => d().monthlyRmb.toFixed(1), _el$37);
            _$insert(_el$34, () => d().eomRmb.toFixed(0), null);
            _$effect((_p$) => {
              var _v$ = thresholdColor(d().dailyRatio), _v$2 = thresholdColor(d().monthlyRatio), _v$3 = thresholdColor(d().sessionRatio), _v$4 = d().cacheRate >= 70 ? MERCURY_SOFT : MERCURY_ACCENT;
              _v$ !== _p$.e && (_p$.e = _$setProp(_el$1, "fg", _v$, _p$.e));
              _v$2 !== _p$.t && (_p$.t = _$setProp(_el$17, "fg", _v$2, _p$.t));
              _v$3 !== _p$.a && (_p$.a = _$setProp(_el$25, "fg", _v$3, _p$.a));
              _v$4 !== _p$.o && (_p$.o = _$setProp(_el$30, "fg", _v$4, _p$.o));
              return _p$;
            }, {
              e: undefined,
              t: undefined,
              a: undefined,
              o: undefined
            });
            return _el$;
          })();
        }
      }
    });
    api.event.on("session.created", () => {
      console.error("[token-hud] session.created");
      writeHudFile(buildHudText());
      api.slots.refresh("sidebar_footer");
    });
    api.event.on("session.idle", () => {
      console.error("[token-hud] session.idle");
      writeHudFile(buildHudText());
      api.slots.refresh("sidebar_footer");
    });
    console.error("[token-hud] TUI plugin mounted OK");
  }
};
export {
  src_default as default
};
