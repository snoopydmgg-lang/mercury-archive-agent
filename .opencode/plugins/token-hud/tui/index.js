// @bun
// src/index.tsx
import { createTextNode as _$createTextNode } from "@opentui/solid";
import { effect as _$effect } from "@opentui/solid";
import { createComponent as _$createComponent } from "@opentui/solid";
import { memo as _$memo } from "@opentui/solid";
import { insertNode as _$insertNode } from "@opentui/solid";
import { insert as _$insert } from "@opentui/solid";
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
var PROGRESS_WIDTH = 14;
var MAX_FILES = 6;
var ACCENT = "#D36B4D";
var MUTED = "#8A8580";
var SOFT = "#E6C8B5";
function formatTokens(n) {
  if (n >= 1e6)
    return `${(n / 1e6).toFixed(1)}M`;
  if (n >= 1000)
    return `${Math.round(n / 1000).toLocaleString()}K`;
  return n.toLocaleString();
}
function thinBar(value, max) {
  const width = PROGRESS_WIDTH;
  const ratio = max > 0 ? Math.min(value / max, 1) : 0;
  const filled = Math.floor(ratio * width);
  const fill = "\u2501";
  const empty = "\u2500";
  const pointer = "\u2578";
  const pointerL = "\u257A";
  if (filled >= width)
    return fill.repeat(width);
  if (filled === 0)
    return pointerL + empty.repeat(width - 1);
  return fill.repeat(filled) + pointer + empty.repeat(width - filled - 1);
}
function thresholdColor(ratio) {
  if (ratio > 0.8)
    return ACCENT;
  if (ratio > 0.5)
    return SOFT;
  return MUTED;
}
function thresholdLabel(ratio) {
  if (ratio > 0.8)
    return "CRIT";
  if (ratio > 0.5)
    return "WARN";
  return "OK";
}
function truncatePath(path, maxLen) {
  if (path.length <= maxLen)
    return path;
  const parts = path.split("/");
  if (parts.length <= 2)
    return path.slice(0, maxLen - 3) + "...";
  const file = parts[parts.length - 1];
  if (file.length >= maxLen - 4)
    return "..." + file.slice(-(maxLen - 3));
  const prefix = parts[0];
  return prefix + "/.../" + file;
}
function formatTime(ts) {
  const d = new Date(ts);
  const h = String(d.getHours()).padStart(2, "0");
  const m = String(d.getMinutes()).padStart(2, "0");
  return `${h}:${m}`;
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
  return [`MERCURY TOKEN ARCHIVE`, `USAGE LEDGER // ${ym}`, `\u2500`.repeat(30), `\u65E5\u9884\u7B97  ${thinBar(data.dailyRmb, DAILY_BUDGET)}  ${Math.round(data.dailyRatio * 100)}%  \xA5${data.dailyRmb.toFixed(1)}  ${thresholdLabel(data.dailyRatio)}`, `\u6708\u9884\u7B97  ${thinBar(data.monthlyRmb, MONTHLY_BUDGET)}  ${Math.round(data.monthlyRatio * 100)}%  \xA5${data.monthlyRmb.toFixed(1)}  ${thresholdLabel(data.monthlyRatio)}`, `\u4F1A\u8BDD\u91CF  ${thinBar(data.sessionTokens, SESSION_LARGE_THRESHOLD)}  ${formatTokens(data.sessionTokens)}  ${thresholdLabel(data.sessionRatio)}`, `\u7F13\u5B58\u7387  ${thinBar(data.cacheRate, 100)}  ${data.cacheRate.toFixed(0)}%  ${cacheLabel}`, `\u2500`.repeat(30), `\u4ECA\u65E5 ${data.todayCount} \u6B21 \xB7 \u672C\u6708 \xA5${data.monthlyRmb.toFixed(1)}`, `\u6708\u672B\u9884\u6D4B \xA5${data.eomRmb.toFixed(0)}`].join(`
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
function Card(props) {
  return (() => {
    var _el$ = _$createElement("box"), _el$2 = _$createElement("box"), _el$3 = _$createElement("text");
    _$insertNode(_el$, _el$2);
    _$setProp(_el$, "flexDirection", "column");
    _$setProp(_el$, "border", true);
    _$setProp(_el$, "borderStyle", "single");
    _$setProp(_el$, "borderColor", "#8A8580");
    _$setProp(_el$, "paddingX", 1);
    _$setProp(_el$, "marginBottom", 1);
    _$insertNode(_el$2, _el$3);
    _$setProp(_el$2, "flexShrink", 0);
    _$setProp(_el$3, "bold", true);
    _$setProp(_el$3, "fg", "#D36B4D");
    _$insert(_el$3, () => props.title);
    _$insert(_el$, () => props.children, null);
    return _el$;
  })();
}
var src_default = {
  id: "token-hud",
  tui: async (api) => {
    console.error("[token-hud] TUI plugin mounting...");
    writeHudFile(buildHudText());
    api.slots.register({
      slots: {
        sidebar_footer(props) {
          const [hudData, setHudData] = createSignal(computeHudData());
          const [tick, setTick] = createSignal(0);
          onMount(() => {
            console.error("[token-hud] sidebar_footer mounted");
            const id = setInterval(() => {
              setHudData(computeHudData());
              setTick((t) => t + 1);
              writeHudFile(buildHudText());
            }, 30000);
            onCleanup(() => clearInterval(id));
          });
          const d = () => hudData();
          const session = () => {
            try {
              return api.state.session.get(props.session_id);
            } catch {
              return;
            }
          };
          const sessionTitle = () => {
            const s = session();
            if (!s)
              return null;
            return s.title || null;
          };
          const sessionTime = () => {
            const s = session();
            if (!s?.time?.created)
              return null;
            return formatTime(s.time.created);
          };
          const tokens = () => {
            const s = session();
            return s?.tokens ?? null;
          };
          const sessionCost = () => {
            const s = session();
            return s?.cost ? s.cost * USD_TO_RMB : 0;
          };
          const totalTokens = () => {
            const t = tokens();
            if (!t)
              return 0;
            return t.input + t.output + t.reasoning;
          };
          const lspItems = () => {
            try {
              return api.state.lsp();
            } catch {
              return [];
            }
          };
          const lspStatus = () => {
            const items = lspItems();
            if (items.length === 0)
              return "Disabled";
            const active = items.filter((i) => i.status === "ready" || i.status === "connected").length;
            if (active === items.length)
              return `Active \xB7 ${items.length} server${items.length > 1 ? "s" : ""}`;
            return `${active}/${items.length} active`;
          };
          const files = () => {
            try {
              return api.state.session.diff(props.session_id);
            } catch {
              return [];
            }
          };
          const now = new Date;
          const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
          return (() => {
            var _el$4 = _$createElement("box");
            _$setProp(_el$4, "flexDirection", "column");
            _$setProp(_el$4, "paddingX", 1);
            _$setProp(_el$4, "flexShrink", 0);
            _$setProp(_el$4, "borderTop", true);
            _$setProp(_el$4, "borderColor", "#8A8580");
            _$insert(_el$4, _$createComponent(Card, {
              title: "MERCURY SESSION",
              get children() {
                var _el$5 = _$createElement("box");
                _$setProp(_el$5, "flexShrink", 0);
                _$insert(_el$5, (() => {
                  var _c$ = _$memo(() => !!sessionTitle());
                  return () => _c$() ? (() => {
                    var _el$47 = _$createElement("text");
                    _$setProp(_el$47, "fg", "#E6C8B5");
                    _$insert(_el$47, sessionTitle);
                    return _el$47;
                  })() : _$memo(() => !!sessionTime())() ? (() => {
                    var _el$48 = _$createElement("text"), _el$49 = _$createTextNode(`Active \\xB7 `);
                    _$insertNode(_el$48, _el$49);
                    _$setProp(_el$48, "fg", "#8A8580");
                    _$insert(_el$48, sessionTime, null);
                    return _el$48;
                  })() : (() => {
                    var _el$50 = _$createElement("text");
                    _$insertNode(_el$50, _$createTextNode(`Awaiting session`));
                    _$setProp(_el$50, "fg", "#8A8580");
                    return _el$50;
                  })();
                })());
                return _el$5;
              }
            }), null);
            _$insert(_el$4, _$createComponent(Card, {
              title: "CONTEXT",
              get children() {
                return _$memo(() => !!tokens())() ? [(() => {
                  var _el$52 = _$createElement("box"), _el$53 = _$createElement("text"), _el$54 = _$createElement("text");
                  _$insertNode(_el$52, _el$53);
                  _$insertNode(_el$52, _el$54);
                  _$setProp(_el$52, "flexDirection", "row");
                  _$setProp(_el$52, "flexShrink", 0);
                  _$setProp(_el$53, "fg", "#E6C8B5");
                  _$insert(_el$53, () => formatTokens(totalTokens()));
                  _$insertNode(_el$54, _$createTextNode(` tokens`));
                  _$setProp(_el$54, "fg", "#8A8580");
                  return _el$52;
                })(), (() => {
                  var _el$56 = _$createElement("box"), _el$57 = _$createElement("text"), _el$58 = _$createTextNode(`\xA5`), _el$59 = _$createElement("text");
                  _$insertNode(_el$56, _el$57);
                  _$insertNode(_el$56, _el$59);
                  _$setProp(_el$56, "flexDirection", "row");
                  _$setProp(_el$56, "flexShrink", 0);
                  _$insertNode(_el$57, _el$58);
                  _$setProp(_el$57, "fg", "#D36B4D");
                  _$insert(_el$57, () => sessionCost().toFixed(2), null);
                  _$insertNode(_el$59, _$createTextNode(` spent`));
                  _$setProp(_el$59, "fg", "#8A8580");
                  return _el$56;
                })()] : (() => {
                  var _el$61 = _$createElement("box"), _el$62 = _$createElement("text");
                  _$insertNode(_el$61, _el$62);
                  _$setProp(_el$61, "flexShrink", 0);
                  _$insertNode(_el$62, _$createTextNode(`Awaiting token data`));
                  _$setProp(_el$62, "fg", "#8A8580");
                  return _el$61;
                })();
              }
            }), null);
            _$insert(_el$4, _$createComponent(Card, {
              title: "LSP",
              get children() {
                var _el$6 = _$createElement("box"), _el$7 = _$createElement("text");
                _$insertNode(_el$6, _el$7);
                _$setProp(_el$6, "flexShrink", 0);
                _$insert(_el$7, lspStatus);
                _$effect((_$p) => _$setProp(_el$7, "fg", lspItems().length > 0 ? SOFT : MUTED, _$p));
                return _el$6;
              }
            }), null);
            _$insert(_el$4, _$createComponent(Card, {
              title: "MODIFIED FILES",
              get children() {
                return _$memo(() => files().length > 0)() ? [_$memo(() => files().slice(0, MAX_FILES).map((f) => {
                  const maxPathLen = 24;
                  const displayPath = truncatePath(f.file, maxPathLen);
                  const changes = f.deletions > 0 ? `+${f.additions} -${f.deletions}` : `+${f.additions}`;
                  return (() => {
                    var _el$64 = _$createElement("box"), _el$65 = _$createElement("text"), _el$66 = _$createElement("text");
                    _$insertNode(_el$64, _el$65);
                    _$insertNode(_el$64, _el$66);
                    _$setProp(_el$64, "flexDirection", "row");
                    _$setProp(_el$64, "flexShrink", 0);
                    _$setProp(_el$65, "fg", "#8A8580");
                    _$insert(_el$65, displayPath);
                    _$setProp(_el$66, "fg", "#E6C8B5");
                    _$insert(_el$66, () => " ".repeat(Math.max(1, maxPathLen - displayPath.length)), null);
                    _$insert(_el$66, changes, null);
                    return _el$64;
                  })();
                })), _$memo(() => _$memo(() => files().length > MAX_FILES)() && (() => {
                  var _el$67 = _$createElement("box"), _el$68 = _$createElement("text"), _el$69 = _$createTextNode(`... `), _el$70 = _$createTextNode(` more files`);
                  _$insertNode(_el$67, _el$68);
                  _$setProp(_el$67, "flexShrink", 0);
                  _$insertNode(_el$68, _el$69);
                  _$insertNode(_el$68, _el$70);
                  _$setProp(_el$68, "fg", "#8A8580");
                  _$insert(_el$68, () => files().length - MAX_FILES, _el$70);
                  return _el$67;
                })())] : (() => {
                  var _el$71 = _$createElement("box"), _el$72 = _$createElement("text");
                  _$insertNode(_el$71, _el$72);
                  _$setProp(_el$71, "flexShrink", 0);
                  _$insertNode(_el$72, _$createTextNode(`Clean workspace`));
                  _$setProp(_el$72, "fg", "#8A8580");
                  return _el$71;
                })();
              }
            }), null);
            _$insert(_el$4, _$createComponent(Card, {
              title: "MERCURY TOKEN ARCHIVE",
              get children() {
                return [(() => {
                  var _el$8 = _$createElement("box"), _el$9 = _$createElement("text"), _el$0 = _$createTextNode(`USAGE LEDGER // `);
                  _$insertNode(_el$8, _el$9);
                  _$setProp(_el$8, "flexShrink", 0);
                  _$insertNode(_el$9, _el$0);
                  _$setProp(_el$9, "fg", "#8A8580");
                  _$setProp(_el$9, "dimColor", true);
                  _$insert(_el$9, ym, null);
                  return _el$8;
                })(), (() => {
                  var _el$1 = _$createElement("box"), _el$10 = _$createElement("text"), _el$12 = _$createElement("text"), _el$13 = _$createTextNode(` `), _el$14 = _$createTextNode(`%`), _el$15 = _$createElement("text"), _el$16 = _$createTextNode(` \xA5`);
                  _$insertNode(_el$1, _el$10);
                  _$insertNode(_el$1, _el$12);
                  _$insertNode(_el$1, _el$15);
                  _$setProp(_el$1, "flexDirection", "row");
                  _$setProp(_el$1, "flexShrink", 0);
                  _$insertNode(_el$10, _$createTextNode(`\u65E5\u9884\u7B97 `));
                  _$setProp(_el$10, "fg", "#8A8580");
                  _$insertNode(_el$12, _el$13);
                  _$insertNode(_el$12, _el$14);
                  _$insert(_el$12, () => thinBar(d().dailyRmb, DAILY_BUDGET), _el$13);
                  _$insert(_el$12, () => Math.round(d().dailyRatio * 100), _el$14);
                  _$insertNode(_el$15, _el$16);
                  _$setProp(_el$15, "fg", "#E6C8B5");
                  _$insert(_el$15, () => d().dailyRmb.toFixed(1), null);
                  _$effect((_$p) => _$setProp(_el$12, "fg", thresholdColor(d().dailyRatio), _$p));
                  return _el$1;
                })(), (() => {
                  var _el$18 = _$createElement("box"), _el$19 = _$createElement("text"), _el$21 = _$createElement("text"), _el$22 = _$createTextNode(` `), _el$23 = _$createTextNode(`%`), _el$24 = _$createElement("text"), _el$25 = _$createTextNode(` \xA5`);
                  _$insertNode(_el$18, _el$19);
                  _$insertNode(_el$18, _el$21);
                  _$insertNode(_el$18, _el$24);
                  _$setProp(_el$18, "flexDirection", "row");
                  _$setProp(_el$18, "flexShrink", 0);
                  _$insertNode(_el$19, _$createTextNode(`\u6708\u9884\u7B97 `));
                  _$setProp(_el$19, "fg", "#8A8580");
                  _$insertNode(_el$21, _el$22);
                  _$insertNode(_el$21, _el$23);
                  _$insert(_el$21, () => thinBar(d().monthlyRmb, MONTHLY_BUDGET), _el$22);
                  _$insert(_el$21, () => Math.round(d().monthlyRatio * 100), _el$23);
                  _$insertNode(_el$24, _el$25);
                  _$setProp(_el$24, "fg", "#E6C8B5");
                  _$insert(_el$24, () => d().monthlyRmb.toFixed(1), null);
                  _$effect((_$p) => _$setProp(_el$21, "fg", thresholdColor(d().monthlyRatio), _$p));
                  return _el$18;
                })(), (() => {
                  var _el$27 = _$createElement("box"), _el$28 = _$createElement("text"), _el$30 = _$createElement("text"), _el$31 = _$createTextNode(` `);
                  _$insertNode(_el$27, _el$28);
                  _$insertNode(_el$27, _el$30);
                  _$setProp(_el$27, "flexDirection", "row");
                  _$setProp(_el$27, "flexShrink", 0);
                  _$insertNode(_el$28, _$createTextNode(`\u4F1A\u8BDD\u91CF `));
                  _$setProp(_el$28, "fg", "#8A8580");
                  _$insertNode(_el$30, _el$31);
                  _$insert(_el$30, () => thinBar(d().sessionTokens, SESSION_LARGE_THRESHOLD), _el$31);
                  _$insert(_el$30, () => formatTokens(d().sessionTokens), null);
                  _$effect((_$p) => _$setProp(_el$30, "fg", thresholdColor(d().sessionRatio), _$p));
                  return _el$27;
                })(), (() => {
                  var _el$32 = _$createElement("box"), _el$33 = _$createElement("text"), _el$35 = _$createElement("text"), _el$36 = _$createTextNode(` `), _el$37 = _$createTextNode(`%`);
                  _$insertNode(_el$32, _el$33);
                  _$insertNode(_el$32, _el$35);
                  _$setProp(_el$32, "flexDirection", "row");
                  _$setProp(_el$32, "flexShrink", 0);
                  _$insertNode(_el$33, _$createTextNode(`\u7F13\u5B58\u7387 `));
                  _$setProp(_el$33, "fg", "#8A8580");
                  _$insertNode(_el$35, _el$36);
                  _$insertNode(_el$35, _el$37);
                  _$insert(_el$35, () => thinBar(d().cacheRate, 100), _el$36);
                  _$insert(_el$35, () => d().cacheRate.toFixed(0), _el$37);
                  _$effect((_$p) => _$setProp(_el$35, "fg", d().cacheRate >= 70 ? SOFT : ACCENT, _$p));
                  return _el$32;
                })(), (() => {
                  var _el$38 = _$createElement("box"), _el$39 = _$createElement("text"), _el$40 = _$createTextNode(`\u4ECA\u65E5 `), _el$42 = _$createTextNode(` \u6B21 \xB7 \u672C\u6708 \xA5`);
                  _$insertNode(_el$38, _el$39);
                  _$setProp(_el$38, "flexDirection", "row");
                  _$setProp(_el$38, "flexShrink", 0);
                  _$insertNode(_el$39, _el$40);
                  _$insertNode(_el$39, _el$42);
                  _$setProp(_el$39, "fg", "#8A8580");
                  _$setProp(_el$39, "dimColor", true);
                  _$insert(_el$39, () => d().todayCount, _el$42);
                  _$insert(_el$39, () => d().monthlyRmb.toFixed(1), null);
                  return _el$38;
                })(), (() => {
                  var _el$44 = _$createElement("box"), _el$45 = _$createElement("text"), _el$46 = _$createTextNode(`\u6708\u672B\u9884\u6D4B \xA5`);
                  _$insertNode(_el$44, _el$45);
                  _$setProp(_el$44, "flexDirection", "row");
                  _$setProp(_el$44, "flexShrink", 0);
                  _$insertNode(_el$45, _el$46);
                  _$setProp(_el$45, "fg", "#8A8580");
                  _$setProp(_el$45, "dimColor", true);
                  _$insert(_el$45, () => d().eomRmb.toFixed(0), null);
                  return _el$44;
                })()];
              }
            }), null);
            return _el$4;
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
