# constraint-kit 2.0 — Design

Date: 2026-08-04
Status: Implemented by this restructure

## Goal

Convert constraint-kit from a bespoke skills/roles/bundles framework with a
Python bootstrap pipeline into a standard **GitHub Copilot plugin
marketplace**. Users install plugins (the successor to bundles) and switch
between agents; skills write per-project state into the target repo's
`.constraint-kit/` folder instead of a renderer generating session prompts.

## What is removed

- `bootstrap/` — rendering, validation, and compliance scripts. Replaced by
  plugins that Copilot loads natively.
- `schema/` — custom YAML schemas for skills/roles/bundles/agents. Replaced
  by standard SKILL.md frontmatter, `*.agent.md` frontmatter, `plugin.json`,
  and `marketplace.json`.
- `bundles/`, `registries/`, `registry.yaml`, `contrib/` — replaced by
  `plugins/` and the marketplace manifest.
- `skills/*` (old constraint-kit skills) — superseded by curated, merged
  skills from mattpocock/skills and obra/superpowers.
- `.constraint-kit/*` tracked files — `.constraint-kit/` is now a
  *generated per-project workspace convention*, never content shipped by
  this repo.
- Drive/multisurface docs, scenario docs, and pipeline diagrams that
  documented the old engine.

## New repository layout

```text
constraint-kit/
├── .claude-plugin/
│   └── marketplace.json          # marketplace manifest (Copilot CLI / cloud agent / Claude Code)
├── plugins/
│   ├── constraint-design/        # plan-before-code bundle
│   │   ├── plugin.json
│   │   ├── agents/
│   │   │   └── planner.agent.md
│   │   └── skills/
│   │       ├── project-intake/       # NEW: pre-planning for new projects; writes .constraint-kit/ + copilot-instructions
│   │       ├── session-archaeology/  # pre-planning for existing codebases; old skill modernized, CodeGraph-assisted
│   │       ├── codegraph-setup/      # NEW: installs/wires CodeGraph (incl. manual Copilot MCP setup)
│   │       ├── brainstorming/        # obra brainstorming + mattpocock grilling/grill-with-docs + domain-model capture
│   │       ├── writing-specs/        # mattpocock to-spec, retargeted to .constraint-kit/specs/
│   │       └── writing-plans/        # obra writing-plans + mattpocock codebase-design (merged)
│   └── constraint-dev/           # disciplined implementation bundle
│       ├── plugin.json
│       ├── agents/
│       │   ├── conductor.agent.md    # SDD orchestrator (old "supervisor" concept)
│       │   ├── implementer.agent.md  # task executor (old "implementer" concept)
│       │   └── reviewer.agent.md     # code review specialist
│       └── skills/
│           ├── test-driven-development/   # obra TDD + mattpocock tdd (merged)
│           ├── subagent-driven-development/
│           ├── executing-plans/
│           ├── requesting-code-review/
│           ├── receiving-code-review/
│           └── finishing-a-development-branch/
├── docs/
│   └── DESIGN.md
├── scripts/
│   └── validate.py               # stdlib-only structure validation for CI
└── README.md, CONTRIBUTING.md, CHANGELOG.md, AGENTS.md, LICENSE
```

## Skill merge map

| New skill | Sources | Merge rationale |
|---|---|---|
| `project-intake` | new; concepts from old bootstrap templates + roles | Replaces the bootstrap renderer: interviews the user (grilling style), explores the repo, then writes `.constraint-kit/PROJECT.md` and generates `.github/copilot-instructions.md`. For new/early-stage projects and constraint updates. |
| `session-archaeology` | pre-2.0 constraint-kit `session-archaeology`, `project-intake` output conventions | Existing-codebase counterpart to intake. Keeps the old skill's gems — provenance modes (KNOWN/UNKNOWN), V/I/U confidence tags, five discovery passes, flaw taxonomy, open gaps — drops the dead session-preflight/SESSION_PLAN architecture, retargets output to `.constraint-kit/ARCHAEOLOGY.md`, and ends by producing the same PROJECT.md/GLOSSARY.md/copilot-instructions as `project-intake` (steps 3–5, facts pre-filled). Discovery passes are CodeGraph-assisted. |
| `codegraph-setup` | new; [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) docs + [PR #718](https://github.com/colbymchenry/codegraph/pull/718) | CodeGraph has no native Copilot support; this skill wraps CLI install, `codegraph install` for auto-configured agents, the manual Copilot MCP config (Copilot CLI `~/.copilot/mcp-config.json` with required `tools` key; VS Code `.vscode/mcp.json`), and per-project `codegraph init`. |
| `brainstorming` | obra `brainstorming`, mattpocock `grilling` + `grill-with-docs` + `domain-modeling` capture rules | All three are "interview the user until the design is solid." Merged: one-question-at-a-time grilling discipline + design presentation/approval + glossary/ADR capture as terms crystallise. |
| `writing-specs` | mattpocock `to-spec` | Kept solo; issue-tracker publishing replaced by `.constraint-kit/specs/`. |
| `writing-plans` | obra `writing-plans`, mattpocock `codebase-design` (+ `DEEPENING.md`, `DESIGN-IT-TWICE.md`) | Both govern "decide the shape of the code before writing it." The deep-module vocabulary becomes the File Structure / interface-design step of plan writing. |
| `test-driven-development` | obra `test-driven-development` (+ `writing-good-tests.md`), mattpocock `tdd` (+ `tests.md`, `mocking.md`) | Same loop, complementary strengths: obra brings the iron law, verification gates, and anti-rationalization tables; mattpocock brings seams, tautological-test and horizontal-slicing anti-patterns. |
| `subagent-driven-development` | obra (incl. prompts + scripts) | Workspace moved `.superpowers/sdd/` → `.constraint-kit/sdd/`. |
| `executing-plans` | obra | Inline fallback when subagents are unavailable. |
| `requesting-code-review` | obra (+ `code-reviewer.md`) | Unchanged in substance. |
| `receiving-code-review` | obra | Unchanged in substance. |
| `finishing-a-development-branch` | obra | Pulled in because both execution skills terminate in it. |

## Skill flow

```text
project-intake ────────┐
  (new project)        ├──> brainstorming ──> writing-specs ──> writing-plans
session-archaeology ───┘
  (existing code; uses codegraph-setup)                     │
                                          ┌─────────────────┴───────────────┐
                                          v                                 v
                            subagent-driven-development             executing-plans
                                          │   (uses TDD, requesting/         │
                                          │    receiving-code-review)        │
                                          └─────────────────┬───────────────┘
                                                            v
                                            finishing-a-development-branch
```

Cross-skill references use plain skill names (no `superpowers:` prefix);
flows that cross the plugin boundary (writing-plans → SDD) note that the
`constraint-dev` plugin provides the target skill.

## The `.constraint-kit/` workspace convention

Skills write all planning and process artifacts into the **target
project's** `.constraint-kit/` folder:

| Path | Written by |
|---|---|
| `.constraint-kit/PROJECT.md` | project-intake (goals, stack, conventions, constraints) |
| `.constraint-kit/GLOSSARY.md` | brainstorming / project-intake / session-archaeology (domain language) |
| `.constraint-kit/ARCHAEOLOGY.md` | session-archaeology (confidence-tagged evidence from an existing codebase) |
| `.constraint-kit/adr/NNNN-*.md` | brainstorming (decision records) |
| `.constraint-kit/specs/YYYY-MM-DD-<topic>-spec.md` | writing-specs (and design docs from brainstorming) |
| `.constraint-kit/plans/YYYY-MM-DD-<feature>.md` | writing-plans |
| `.constraint-kit/sdd/<plan>/` | subagent-driven-development (git-ignored scratch) |

`project-intake` additionally generates `.github/copilot-instructions.md`
in the target repo so the constraints persist across every Copilot session
— the original constraint-kit thesis ("rules on disk, not in memory")
implemented with native Copilot machinery.

## Agents

Copilot custom agents (`*.agent.md`, frontmatter `name`/`description`),
shipped inside plugins:

- **planner** (constraint-design) — read-mostly; routes intake
  (`project-intake` for new projects, `session-archaeology` for existing
  codebases — one agent, two skills, same workspace output) then drives
  brainstorm → spec → plan; writes only `.constraint-kit/` and
  `.github/copilot-instructions.md` (plus running `codegraph init`).
- **conductor** (constraint-dev) — orchestrates subagent-driven
  development; never edits code itself.
- **implementer** (constraint-dev) — executes one plan task at a time with
  strict TDD.
- **reviewer** (constraint-dev) — runs the code-reviewer template against a
  diff range; reports findings, changes nothing.

**One planner, not two.** New-vs-existing project intake stays one agent
because agents are the user's switching surface and both paths converge
immediately: the same workspace files, then the same
brainstorm→spec→plan pipeline. The difference lives in the skills
(`project-intake` vs `session-archaeology`); the planner just routes.
Two planner agents would double maintenance and force the user to
pre-classify a repo ("mostly new? partly existing?") that the routing
table in either skill classifies for them.

## CodeGraph integration

All four agents carry a "Code discovery" rule: structural questions go
to [CodeGraph](https://github.com/colbymchenry/codegraph)
(`codegraph_explore` MCP tool, or the CLI for subagents without MCP),
results are trusted without grep re-verification. Per-agent emphasis:
planner/brainstorming — explore flows while designing;
session-archaeology — all five discovery passes; implementer —
`explore` before touching unfamiliar code, `affected` for test
selection; reviewer — `impact`/`affected` to verify blast radius;
conductor — adjudication without polluting context.

CodeGraph auto-configures Claude Code and others via `codegraph
install` but has no native Copilot support; `codegraph-setup` encodes
the manual Copilot wiring from upstream PR #718 (Copilot CLI
`~/.copilot/mcp-config.json`, which requires the `tools` key) plus the
VS Code `.vscode/mcp.json` variant. Every skill/agent degrades to
built-in search when CodeGraph is absent, with an explicit
lower-confidence disclaimer.

## Manifests

`plugin.json` (per plugin root, per official github/copilot-plugins
examples): `name`, `description`, `version`, `author`, `homepage`,
`repository`, `license`, `keywords`, `skills: ["skills/"]`,
`agents: ["agents/"]`.

`.claude-plugin/marketplace.json`: `name`, `metadata`, `owner`, `plugins[]`
with relative `source` paths (`./plugins/<name>`), consumable by Copilot
CLI, the Copilot cloud agent, and Claude Code.

## CI

`scripts/validate.py` (stdlib only): manifests parse, marketplace entries
match plugin dirs, every skill has `SKILL.md` with `name` + `description`
frontmatter, every agent file has frontmatter, no dangling relative links
inside skills. Run by `.github/workflows/validate.yml`.
