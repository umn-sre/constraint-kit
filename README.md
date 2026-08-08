# constraint-kit

Constraint-driven planning and implementation plugins for **GitHub
Copilot** (CLI, VS Code, coding agent) and **Claude Code**.

AI assistants drift: rules given at the start of a session are forgotten
by the middle. constraint-kit keeps the rules on disk instead — skills
write every planning artifact into your repo's `.constraint-kit/` folder
and generate `.github/copilot-instructions.md`, so every session starts
from the same constraints without any bootstrap step.

This repo is a **plugin marketplace**: two plugins that mirror the two
halves of disciplined development, plus an org-specific compliance
plugin:

| Plugin | What it enforces |
|---|---|
| [`constraint-design`](plugins/constraint-design/) | Plan before code: project intake (new projects) or project archaeology (existing codebases), relentless brainstorming, specs, deep-module implementation plans |
| [`constraint-dev`](plugins/constraint-dev/) | Implement with discipline: strict TDD, subagent-driven execution with per-task reviews, session ledger (verified edits, loop halts, lessons logged), security principles, code review rigor, clean branch finishing |
| [`umn-compliance`](plugins/umn-compliance/) | UMN-only: security compliance analysis and annual reviews against the 16 UMN Information Security Policy Standards. Install only for University of Minnesota projects |

## Install

### Copilot CLI

```text
/plugin marketplace add umn-sre/constraint-kit
/plugin install constraint-design@constraint-kit
/plugin install constraint-dev@constraint-kit
/plugin install umn-compliance@constraint-kit   # UMN projects only
```

Or declaratively, in `~/.copilot/settings.json` (personal) or your repo's
`.github/copilot/settings.json` (shared, also used by the Copilot coding
agent):

```json
{
  "extraKnownMarketplaces": {
    "constraint-kit": {
      "source": { "source": "github", "repo": "umn-sre/constraint-kit" }
    }
  },
  "enabledPlugins": [
    "constraint-design@constraint-kit",
    "constraint-dev@constraint-kit"
  ]
}
```

### VS Code

Copilot in VS Code discovers skills and custom agents from your
repository rather than from plugins. Two options:

- Use the Copilot CLI install above — CLI-installed plugins are available
  to VS Code's Copilot CLI integration.
- Or vendor the pieces you want into the repo Copilot reads natively:
  copy `plugins/*/skills/<name>/` into `.github/skills/<name>/` and
  `plugins/*/agents/*.agent.md` into `.github/agents/`.

### Claude Code

```text
/plugin marketplace add umn-sre/constraint-kit
/plugin install constraint-design@constraint-kit
/plugin install constraint-dev@constraint-kit
/plugin install umn-compliance@constraint-kit   # UMN projects only
```

## The workflow

```text
project-intake ────────┐
  (new project)        ├──> brainstorming ──> writing-specs ──> writing-plans
project-archaeology ───┘   (planner agent, constraint-design plugin)
  (existing code, CodeGraph-assisted)                       │
                                          ┌─────────────────┴───────────────┐
                                          v                                 v
                            subagent-driven-development             executing-plans
                               (conductor agent)                     (inline mode)
                                          │  uses: test-driven-development, │
                                          │  requesting/receiving-code-review│
                                          └─────────────────┬───────────────┘
                                                            v
                                            finishing-a-development-branch
```

1. Intake, once per project. **`project-intake`** (new or early-stage
   repo) interviews you and writes `.constraint-kit/PROJECT.md` +
   `GLOSSARY.md`, generating `.github/copilot-instructions.md`.
   **`project-archaeology`** (existing codebase without trustworthy
   docs) instead reads the code first — confidence-tagged discovery
   passes recorded in `.constraint-kit/ARCHAEOLOGY.md` — and then
   produces the same three files, grounded in evidence.
2. **`brainstorming`** grills you one question at a time until a design
   is approved, capturing glossary terms and decision records as they
   crystallise.
3. **`writing-specs`** synthesizes the conversation into a PRD-style
   spec; **`writing-plans`** turns it into a bite-sized, test-first plan.
4. Switch to the **conductor** agent (constraint-dev): it executes the
   plan with a fresh **implementer** subagent per task, a **reviewer**
   after each, and strict TDD throughout.

Everything lands in `.constraint-kit/` in *your* repo:

```text
.constraint-kit/
├── PROJECT.md        # goals, stack, conventions, working agreement, session log
├── GLOSSARY.md       # domain language, one precise term at a time
├── ARCHAEOLOGY.md    # evidence from onboarding an existing codebase
├── adr/              # decision records (sparingly)
├── specs/            # design docs and specs
├── plans/            # implementation plans
└── sdd/              # execution scratch (git-ignore this one)
```

## CodeGraph integration

All four agents use [CodeGraph](https://github.com/colbymchenry/codegraph)
— a local, auto-syncing code knowledge graph — for structural code
questions: one `codegraph_explore` call returns the relevant symbols'
source, call paths, and blast radius, replacing grep/read loops.
`project-archaeology` depends on it most heavily; the `implementer` and
`reviewer` agents use it for change impact and affected-test discovery.

The `codegraph-setup` skill (constraint-design plugin) handles
installation: CLI install, `codegraph install` for the agents it
auto-configures, and — since CodeGraph has no native GitHub Copilot
support yet — the manual Copilot MCP config from upstream
[PR #718](https://github.com/colbymchenry/codegraph/pull/718)
(`~/.copilot/mcp-config.json` with the required `tools` key for Copilot
CLI, `.vscode/mcp.json` for VS Code), then `codegraph init` per project.
Everything degrades gracefully: without CodeGraph the skills fall back
to built-in search and say so.

## Agents

| Agent | Plugin | Role |
|---|---|---|
| `planner` | constraint-design | Intake (new or existing codebase) → design → spec → plan; never touches source code |
| `conductor` | constraint-dev | Orchestrates plan execution via subagents; never edits code itself |
| `implementer` | constraint-dev | One task at a time, strict TDD |
| `reviewer` | constraint-dev | Spec compliance + quality findings; changes nothing |
| `compliance-analyst` | umn-compliance | UMN policy compliance analysis and annual reviews; writes only the compliance document |

## Credits

The skills are adapted — and where they overlapped, merged — from two
excellent open-source skill collections:

- [obra/superpowers](https://github.com/obra/superpowers): brainstorming,
  writing-plans, test-driven-development, subagent-driven-development,
  executing-plans, requesting/receiving-code-review,
  finishing-a-development-branch
- [mattpocock/skills](https://github.com/mattpocock/skills):
  codebase-design, tdd, grilling / grill-with-docs, domain-modeling,
  to-spec

`project-archaeology`, `session-ledger`, and `security-principles`
are modernized from constraint-kit's own pre-2.0 skills
(`session-archaeology`, `session-hygiene`, and `security-compliance`;
`security-principles` additionally merges the core principles of
[davila7/claude-code-templates](https://github.com/davila7/claude-code-templates)'
`security-compliance` skill); code discovery is powered by
[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph).

See [docs/DESIGN.md](docs/DESIGN.md) for the merge map and architecture.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `python3 scripts/validate.py`
before opening a PR.

## License

[MIT](LICENSE)
