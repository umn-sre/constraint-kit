# constraint-kit

Constraint-driven planning and implementation plugins for **GitHub
Copilot** (CLI, VS Code, coding agent) and **Claude Code**.

AI assistants drift: rules given at the start of a session are forgotten
by the middle. constraint-kit keeps the rules on disk instead — skills
write every planning artifact into your repo's `.constraint-kit/` folder
and generate `.github/copilot-instructions.md`, so every session starts
from the same constraints without any bootstrap step.

This repo is a **plugin marketplace** with two plugins that mirror the
two halves of disciplined development:

| Plugin | What it enforces |
|---|---|
| [`constraint-design`](plugins/constraint-design/) | Plan before code: project intake, relentless brainstorming, specs, deep-module implementation plans |
| [`constraint-dev`](plugins/constraint-dev/) | Implement with discipline: strict TDD, subagent-driven execution with per-task reviews, code review rigor, clean branch finishing |

## Install

### Copilot CLI

```text
/plugin marketplace add umn-sre/constraint-kit
/plugin install constraint-design@constraint-kit
/plugin install constraint-dev@constraint-kit
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
```

## The workflow

```text
project-intake ──> brainstorming ──> writing-specs ──> writing-plans
   (planner agent, constraint-design plugin)                │
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

1. **`project-intake`** (once per project) interviews you, explores the
   repo, writes `.constraint-kit/PROJECT.md` + `GLOSSARY.md`, and
   generates `.github/copilot-instructions.md`.
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
├── PROJECT.md        # goals, stack, conventions, working agreement
├── GLOSSARY.md       # domain language, one precise term at a time
├── adr/              # decision records (sparingly)
├── specs/            # design docs and specs
├── plans/            # implementation plans
└── sdd/              # execution scratch (git-ignore this one)
```

## Agents

| Agent | Plugin | Role |
|---|---|---|
| `planner` | constraint-design | Intake → design → spec → plan; never touches source code |
| `conductor` | constraint-dev | Orchestrates plan execution via subagents; never edits code itself |
| `implementer` | constraint-dev | One task at a time, strict TDD |
| `reviewer` | constraint-dev | Spec compliance + quality findings; changes nothing |

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

See [docs/DESIGN.md](docs/DESIGN.md) for the merge map and architecture.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `python3 scripts/validate.py`
before opening a PR.

## License

[MIT](LICENSE)
