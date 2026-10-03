---
description: Temp/debug output files — store under .tmp/<tool-name>/ at project root
alwaysApply: false
---

# Temp files — ephemeral output location

When running or debugging tests (Playwright e2e, Playwright MCP, Cursor @Browser, manual agent exploration, or similar), put **temporary** files only under:

```
<project root>/.tmp/<tool-name>/
```

`<project root>` is the **git root of the repository under test** (e.g. `my-app/`, `packages/web/` if that is the app root). In a multi-root workspace, use the root that owns the app under test — not a parent folder shared across unrelated repos.

## Tool subdirectories

| Tool / workflow | Directory |
|-----------------|-------------|
| Playwright MCP (interactive agent) | `.tmp/playwright-mcp/` |
| Playwright test runner (`@playwright/test`, CI e2e) | `.tmp/playwright-e2e/` |
| Cursor IDE Browser (`@Browser`) | `.tmp/cursor-browser/` |
| Other tools | `.tmp/<short-tool-id>/` (kebab-case, stable name) |

Create the subdirectory if it does not exist. Do not commit contents — `.tmp/` is gitignored.

## Do not use

- Repository root (no loose `*.png`, `.playwright-mcp/`, etc.)
- `.local/` (project notes and plans, not scratch output)

## Agents and tools

- **Screenshots / snapshots:** pass filenames relative to the tool output dir (e.g. `operator-nav.png`), or paths under `.tmp/<tool-name>/`.
- **Playwright config:** prefer `outputDir`, trace, and report paths under `.tmp/playwright-e2e/` when changing project config.
- **Cleanup:** safe to delete entire `.tmp/` or a tool subdirectory anytime.
