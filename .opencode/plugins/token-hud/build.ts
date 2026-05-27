import { build } from "bun";
import solidPlugin from "@opentui/solid/bun-plugin";

const externals = [
  "@opencode-ai/plugin",
  "@opencode-ai/plugin/tui",
  "@opencode-ai/sdk",
  "@opencode-ai/sdk/v2",
  "@opentui/core",
  "@opentui/solid",
  "solid-js",
  "solid-js/web",
  "effect",
  "bun:sqlite",
];

// Build server plugin (no JSX)
await build({
  outdir: ".",
  target: "bun",
  format: "esm",
  external: externals,
  entrypoints: ["src/server.ts"],
  naming: "server.[ext]",
});

// Build TUI plugin (with SolidJS JSX)
await build({
  outdir: "tui",
  target: "bun",
  format: "esm",
  external: externals,
  plugins: [solidPlugin],
  entrypoints: ["src/index.tsx"],
  naming: "index.[ext]",
});

console.log("Build complete: server.js + tui/index.js");
