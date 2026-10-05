---
description: JS/TS package manager — respect existing lockfiles; Bun for new projects
globs: "**/*.{ts,tsx,js,jsx,mjs,cjs,vue,svelte,astro}"
always: false
---

# JavaScript / TypeScript package manager

Applies when working with JS/TS trees (including Vue, Svelte, Astro, and similar frameworks in the same repo).

## Existing projects (default)

If the repository already declares a package manager, **respect it**. Infer from lockfiles and config at the project root (or the package root you are editing):

| Signal | Use |
| --- | --- |
| `package-lock.json` | npm |
| `pnpm-lock.yaml` | pnpm |
| `yarn.lock` | yarn |
| `bun.lock` / `bun.lockb` | Bun |

Also honor `packageManager` in `package.json`, `.npmrc`, `pnpm-workspace.yaml`, or documented team conventions. Do **not** switch package manager or rewrite lockfiles unless the user explicitly asks.

## New projects

When **starting a new** JS/TS project (no established lockfile from another tool) and the user has not specified a preference, prefer **Bun** for installs, scripts, and the lockfile (`bun install`, `bun run`, `bun.lock` / `bun.lockb`).

## Mixed / monorepos

In a monorepo, follow the tool configured for the **package you are changing**, not a global default from another workspace member.
