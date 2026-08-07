# constraint-design

Plan-before-code bundle for GitHub Copilot (CLI, VS Code, coding agent)
and Claude Code.

Everything this plugin produces lands in the target repo's
`.constraint-kit/` folder, so constraints live on disk — not in
conversation memory — and every future session can pick them up.

## Skills

| Skill | Stage | Output |
|---|---|---|
| `project-intake` | Pre-planning (new/early-stage project) | `.constraint-kit/PROJECT.md`, `GLOSSARY.md`, generated `.github/copilot-instructions.md` |
| `session-archaeology` | Pre-planning (existing codebase) | `.constraint-kit/ARCHAEOLOGY.md` plus the same three files as `project-intake`, grounded in code evidence |
| `codegraph-setup` | Tooling | CodeGraph installed, wired to the current agent surface (incl. manual Copilot MCP config), project indexed |
| `brainstorming` | Design | Approved design doc in `.constraint-kit/specs/`, glossary + ADR updates |
| `writing-specs` | Spec | PRD-style spec in `.constraint-kit/specs/` |
| `writing-plans` | Plan | Bite-sized, test-first plan in `.constraint-kit/plans/` |

Flow: `project-intake` *or* `session-archaeology` (which uses
`codegraph-setup`) → `brainstorming` → `writing-specs` →
`writing-plans` → hand off to the **constraint-dev** plugin for execution.

## Agents

- **planner** — routes intake (`project-intake` for new projects,
  `session-archaeology` for existing codebases) and drives the design
  stages; writes only to `.constraint-kit/` and
  `.github/copilot-instructions.md`, never source code. Uses CodeGraph
  for structural code questions.

## Credits

Skills adapted and merged from
[obra/superpowers](https://github.com/obra/superpowers)
(`brainstorming`, `writing-plans`) and
[mattpocock/skills](https://github.com/mattpocock/skills)
(`grilling`, `grill-with-docs`, `domain-modeling`, `to-spec`,
`codebase-design`). `session-archaeology` is modernized from
constraint-kit's own pre-2.0 skill; code discovery uses
[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)
(Copilot setup per
[codegraph#718](https://github.com/colbymchenry/codegraph/pull/718)).
See each SKILL.md for details.
