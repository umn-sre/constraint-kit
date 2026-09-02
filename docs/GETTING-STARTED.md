# Getting Started with constraint-kit

A first run for teammates and anyone new to the skill set. If you have
not read it yet, [README.md](../README.md) covers what constraint-kit is
and why it exists, and [DESIGN.md](DESIGN.md) covers how it is put
together; this page walks you from "just installed" through one complete
design-to-merge pass on a real project.

## The idea in 60 seconds

AI assistants drift: the rules you give at the start of a session are
gone by the middle. constraint-kit's answer is to keep the rules on
disk. Skills write your project's context into `docs/`, planning
artifacts into `docs/constraint-kit/`, and execution scratch into
`.constraint-kit/sdd/`, so every new session — yours or a teammate's —
starts from the same constraints with no bootstrap step.

Two plugins mirror the two halves of the work:

| Plugin | Phase | You drive it through the... |
|---|---|---|
| `constraint-design` | Plan before code | **planner** agent |
| `constraint-dev` | Implement with discipline | **conductor** agent (or inline) |

`umn-compliance` is a third, UMN-only plugin — install it only for
University of Minnesota projects.

You move through the workflow by **switching agents** and letting the
skills fire. You do not need to memorise skill names; each skill's
description tells the assistant when to load it, and you can always
invoke one explicitly (`/brainstorming`, `/writing-plans`, ...).

## Install

Full instructions per surface are in
[README.md → Install](../README.md#install). The short version:

**Copilot CLI / Claude Code**

```text
/plugin marketplace add umn-sre/constraint-kit
/plugin install constraint-design@constraint-kit
/plugin install constraint-dev@constraint-kit
/plugin install umn-compliance@constraint-kit   # UMN projects only
```

**Copilot in VS Code** discovers skills and agents from the repo, not
from plugins — either use the Copilot CLI install above, or vendor
`plugins/*/skills/<name>/` into `.github/skills/` and
`plugins/*/agents/*.agent.md` into `.github/agents/`. See the README.

## Your first pass

The pipeline is:

```text
intake --> brainstorming --> writing-specs --> writing-plans
  (planner agent)                                   |
                                                    v
                    subagent-driven-development / executing-plans
                          (conductor agent)         |
                                                    v
                            finishing-a-development-branch
```

Never skip ahead: no spec before an approved design, no plan before a
spec. (Small, fully understood changes may go brainstorming --> plan.)

### 0. (Optional) Wire up CodeGraph

All four agents use [CodeGraph](https://github.com/colbymchenry/codegraph)
— a local code knowledge graph — for structural questions ("how does X
work", callers, blast radius). It is optional: without it the skills
fall back to built-in search and say confidence is lower.

To set it up, ask the assistant to run the `codegraph-setup` skill. It
installs the CLI (with your OK), wires the MCP server to your agent
surface — including the manual GitHub Copilot config that CodeGraph
lacks natively — and runs `codegraph init` in your project.
`project-archaeology` (below) will invoke it for you if it is missing.

### 1. Onboard the project — once

Switch to the **planner** agent. It reads any existing
`docs/PROJECT.md`, `docs/GLOSSARY.md`, and `docs/ARCHAEOLOGY.md` before
asking you anything, then routes to one of two intake skills:

| Your project | Skill | What happens |
|---|---|---|
| New or early-stage; you can describe it | `project-intake` | One-question-at-a-time interview: purpose, success criteria, scope, conventions, process, domain terms. |
| Substantial existing code; docs missing or stale | `project-archaeology` | Reads the code first — confidence-tagged discovery passes (CodeGraph-assisted), recorded in `docs/ARCHAEOLOGY.md` — then a short interview for what the code can't answer. |

Both end at the same place:

- `docs/PROJECT.md` — goals, stack, conventions, constraints, working
  agreement, and a Session log appended by later sessions
- `docs/GLOSSARY.md` — domain language, one precise term at a time
- `docs/ARCHAEOLOGY.md` — evidence (archaeology only)
- `.github/copilot-instructions.md` — generated, so the constraints
  reach every future Copilot session automatically

Review the files the planner shows you and correct anything wrong. This
step runs once per project; re-run `project-intake` in update mode when
constraints change.

### 2. Design a change — `brainstorming`

Still in the **planner** agent. Describe the feature or change. The
skill grills you one question at a time — with a recommended answer
each time — until the design is solid, capturing glossary terms and
decision records (`docs/constraint-kit/adr/`) as they crystallise. It
proposes 2–3 approaches, presents a design in sections you approve one
by one, and writes it to
`docs/constraint-kit/specs/YYYY-MM-DD-<topic>-design.md`.

**Hard gate:** no code, no scaffolding, no implementation skill until
you have approved a written design — every project, however simple. The
"this is too small to need a design" reflex is exactly where unexamined
assumptions cost the most.

### 3. Synthesize the spec — `writing-specs`

No new interview — this just crystallises the approved design into a
PRD-style spec (problem, solution, an extensive user-story list,
implementation and testing decisions, out-of-scope) at
`docs/constraint-kit/specs/YYYY-MM-DD-<topic>-spec.md`. The one thing it
checks with you: the test seams.

### 4. Write the plan — `writing-plans`

Designs the modules first (deep interfaces at clean seams), maps the
file structure, then produces a bite-sized, test-first plan —
2–5-minute steps, real test code, no placeholders — at
`docs/constraint-kit/plans/YYYY-MM-DD-<feature>.md`. It ends by asking
how you want to execute.

### 5. Implement — switch to `constraint-dev`

Switch to the **conductor** agent. It executes the plan with a fresh
**implementer** subagent per task and a **reviewer** after each
(spec compliance + quality), tracking progress in a ledger at
`.constraint-kit/sdd/<plan>/progress.md` — the ledger, not memory, is
the source of truth. Strict TDD throughout: red, green, refactor, at
the pre-agreed seams.

If your environment can't dispatch subagents, the conductor falls back
to the `executing-plans` skill — same plan, inline, with checkpoints.

`session-ledger` runs the whole time (edit verification, loop halting,
budget watch) and `security-principles` activates whenever the work
touches credentials, auth, or sensitive data.

### 6. Finish — `finishing-a-development-branch`

Runs the full test suite, then offers exactly three choices: merge to
the base branch locally, push and open a PR, or keep the branch as-is.
The integration decision is yours. Worktrees this workflow created get
cleaned up; anything else is left in place.

## Where everything lands

Everything is written into **your** repo:

```text
docs/
├── PROJECT.md              # constraints + session log
├── GLOSSARY.md             # domain language
├── ARCHAEOLOGY.md          # evidence (existing-codebase onboarding)
└── constraint-kit/
    ├── adr/                # decision records (sparingly)
    ├── specs/              # design docs and specs
    └── plans/              # implementation plans

.constraint-kit/sdd/        # execution scratch — git-ignore this
```

Add `.constraint-kit/` (and `.codegraph/`, if you use CodeGraph) to
your `.gitignore`. Commit `docs/` — that is the point.

## Picking up someone else's work

Because the constraints are on disk, you don't need the original
session:

1. Read `docs/PROJECT.md` and `docs/GLOSSARY.md` — the working
   agreement and vocabulary.
2. Check `docs/constraint-kit/plans/` for an in-flight plan and
   `.constraint-kit/sdd/<plan>/progress.md` for how far it got. Tasks
   with a `complete` line are done; resume at the first without one.
3. Read the relevant `docs/constraint-kit/specs/` and any
   `docs/constraint-kit/adr/` for the area you're touching before
   changing anything.

## Working without CodeGraph

Every skill and agent degrades gracefully: they fall back to built-in
search, take more calls, and explicitly lower their confidence on
caller/impact claims. `project-archaeology` will offer to install
CodeGraph because it leans on it most; you can decline.

## UMN projects: compliance

Install `umn-compliance` and switch to the **compliance-analyst** agent
to run `umn-security-compliance` — an initial or annual analysis
mapping the project against the 16 UMN Information Security Policy
Standards, producing an evidence-based compliance document plus a
design-gap list that feeds back into the brainstorming → spec → plan
pipeline. Data classification and security level are recorded in
`docs/PROJECT.md` Constraints.

## Gotchas

- **Don't skip stages.** The pipeline order is enforced for a reason;
  the planner will refuse to jump ahead.
- **One planner agent**, not two — it routes new vs. existing projects
  itself. Don't look for a separate "existing codebase" agent.
- **The ledger is truth.** After a compaction, trust
  `.constraint-kit/sdd/<plan>/progress.md` and `git log` over
  recollection.
- **Never start implementation on `main`/`master`** without saying so
  explicitly — the execution skills expect a feature branch or
  worktree.
- **Consumer artifacts stay in the consumer repo.** If you are working
  inside the constraint-kit repo itself, see
  [AGENTS.md](../AGENTS.md) and [CONTRIBUTING.md](../CONTRIBUTING.md)
  instead — this page is for using the plugins on your own projects.
