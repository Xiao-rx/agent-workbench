import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

test("documents the TypeScript CLI entry point", () => {
  const source = readFileSync(new URL("../src/index.ts", import.meta.url), "utf-8");

  assert.match(source, /export function main/);
  assert.match(source, /parseArgs/);
  assert.match(source, /console\.log/);
});
