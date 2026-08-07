---
name: codegraph-setup
description: Use when CodeGraph code intelligence is needed but not installed or not wired to the current agent - installs the CLI, connects the MCP server (including the manual GitHub Copilot setup it lacks natively), indexes the project, and verifies the tools answer.
---

# CodeGraph Setup

[CodeGraph](https://github.com/colbymchenry/codegraph) is a local,
pre-indexed code knowledge graph. Constraint-kit agents use it for
structural code discovery — "how does X work", callers/callees, change
impact — instead of grep/read loops. This skill gets it from "not
installed" to "answering queries" on the current machine and project.

**Announce at start:** "I'm using the codegraph-setup skill to wire up
CodeGraph."

## Check before doing anything

Run the checks in order; skip every step already satisfied:

1. `codegraph version` succeeds → CLI installed (skip step 1).
2. A `codegraph_explore` MCP tool is available in this session → the
   current agent surface is wired (skip steps 2–3).
3. `.codegraph/` exists in the project (or `codegraph status` reports an
   index) → project indexed (skip step 4).

If all three pass, say so and stop — there is nothing to set up.

## 1. Install the CLI

**Confirm with the user before installing anything global.** Then:

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh

# Windows (PowerShell)
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex

# Or, with Node available
npm i -g @colbymchenry/codegraph
```

The installer puts `codegraph` on PATH but does not change the current
shell — a new terminal (or full path) may be needed before the next step.

## 2. Wire up auto-configurable agents

```bash
codegraph install
```

This detects and configures Claude Code, Cursor, Codex CLI, opencode,
Hermes Agent, Gemini CLI, Antigravity, and Kiro. It wires the MCP server
only — it does **not** index any code (that is step 4).

**It does not configure GitHub Copilot.** If Copilot is one of the
surfaces in use, continue to step 3; otherwise skip to step 4.

## 3. Manual GitHub Copilot setup

CodeGraph has no native Copilot support yet; this follows the setup
contributed upstream in
[colbymchenry/codegraph#718](https://github.com/colbymchenry/codegraph/pull/718).

### Copilot CLI / Copilot coding agent

Add the server to `~/.copilot/mcp-config.json` (create the file if
missing; `COPILOT_HOME` relocates the directory):

```json
{
  "mcpServers": {
    "codegraph": {
      "type": "stdio",
      "command": "codegraph",
      "args": ["serve", "--mcp"],
      "tools": ["*"]
    }
  }
}
```

Unlike Claude Code, **Copilot requires the `tools` key** — without it no
CodeGraph tools are enabled. `["*"]` enables all; to allowlist instead,
name them (`codegraph_explore`, `codegraph_node`, `codegraph_search`,
`codegraph_callers`, `codegraph_callees`, `codegraph_impact`,
`codegraph_files`, `codegraph_status`). Then reload with `/mcp` (or
restart the session) and confirm the server connected.

### Copilot in VS Code

Add the server to the workspace's `.vscode/mcp.json` (or via
**MCP: Add Server** in the command palette) using VS Code's `servers`
key:

```json
{
  "servers": {
    "codegraph": {
      "type": "stdio",
      "command": "codegraph",
      "args": ["serve", "--mcp"]
    }
  }
}
```

Then start the server from the MCP view and confirm the tools appear in
Copilot Chat's tool picker.

## 4. Index the project

```bash
cd <project>
codegraph init
```

One command creates `.codegraph/` and builds the graph. Auto-sync then
keeps it fresh on every file change — never run manual re-syncs. Ensure
`.codegraph/` is git-ignored in the project (add it if the init didn't).

## 5. Verify

`codegraph status` should report the index, and a probe query should
return real symbols:

```bash
codegraph explore "entry points"
```

If the MCP tool is wired, prefer probing via `codegraph_explore` instead
so the whole path is exercised.

## Usage rules (all constraint-kit agents)

- **One tool answers most questions**: `codegraph_explore` (MCP) or
  `codegraph explore` (CLI) returns relevant symbols' verbatim source,
  call paths, and blast radius in one call. Reach for it for "how does X
  work", flows, or surveying an area.
- **Trust results — don't re-verify with grep.** The graph *is* the
  pre-read index; treat returned source as already read.
- Subagents without MCP access use the CLI equivalents (`codegraph
  explore` / `node` / `callers` / `callees` / `impact` / `affected`).
- Other projects can be queried by passing `projectPath`; a path with no
  index returns guidance, not an error.
- If the user declines installation, fall back to built-in search tools
  and say the analysis will take more calls and carry lower confidence
  for caller/impact claims.

## Red flags

- Installing globally without asking the user first
- Running `codegraph install` and assuming Copilot got configured
- A Copilot MCP config missing the `tools` key
- Re-running `codegraph sync` by hand when auto-sync is active
- Committing `.codegraph/` to version control
