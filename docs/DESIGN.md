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
│   │       ├── project-intake/       # NEW: pre-planning; writes .constraint-kit/ + copilot-instructions
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
| `project-intake` | new; concepts from old bootstrap templates + roles | Replaces the bootstrap renderer: interviews the user (grilling style), explores the repo, then writes `.constraint-kit/PROJECT.md` and generates `.github/copilot-instructions.md`. |
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
project-intake ──> brainstorming ──> writing-specs ──> writing-plans
                                                            │
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
| `.constraint-kit/GLOSSARY.md` | brainstorming / project-intake (domain language) |
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

- **planner** (constraint-design) — read-mostly; drives intake →
  brainstorm → spec → plan; writes only `.constraint-kit/` and
  `.github/copilot-instructions.md`.
- **conductor** (constraint-dev) — orchestrates subagent-driven
  development; never edits code itself.
- **implementer** (constraint-dev) — executes one plan task at a time with
  strict TDD.
- **reviewer** (constraint-dev) — runs the code-reviewer template against a
  diff range; reports findings, changes nothing.

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
