# constraint-design

Plan-before-code bundle for GitHub Copilot (CLI, VS Code, coding agent)
and Claude Code.

Everything this plugin produces lands in the target repo's
`.constraint-kit/` folder, so constraints live on disk — not in
conversation memory — and every future session can pick them up.

## Skills

| Skill | Stage | Output |
|---|---|---|
| `project-intake` | Pre-planning | `.constraint-kit/PROJECT.md`, `GLOSSARY.md`, generated `.github/copilot-instructions.md` |
| `brainstorming` | Design | Approved design doc in `.constraint-kit/specs/`, glossary + ADR updates |
| `writing-specs` | Spec | PRD-style spec in `.constraint-kit/specs/` |
| `writing-plans` | Plan | Bite-sized, test-first plan in `.constraint-kit/plans/` |

Flow: `project-intake` → `brainstorming` → `writing-specs` →
`writing-plans` → hand off to the **constraint-dev** plugin for execution.

## Agents

- **planner** — drives the four stages above; writes only to
  `.constraint-kit/` and `.github/copilot-instructions.md`, never source
  code.

## Credits

Skills adapted and merged from
[obra/superpowers](https://github.com/obra/superpowers)
(`brainstorming`, `writing-plans`) and
[mattpocock/skills](https://github.com/mattpocock/skills)
(`grilling`, `grill-with-docs`, `domain-modeling`, `to-spec`,
`codebase-design`). See each SKILL.md for details.
