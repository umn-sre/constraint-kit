# constraint-design

Plan-before-code bundle for GitHub Copilot (CLI, VS Code, coding agent)
and Claude Code.

Approved artifacts land in the target repo's `docs/` and
`docs/constraint-kit/` folders. Active workflow state lives in the
git-ignored `.constraint-kit/discipline.md`, so constraints survive phase
and session boundaries instead of depending on conversation memory.

## Skills

| Skill | Stage | Output |
|---|---|---|
| `project-intake` | Pre-planning (new/early-stage project) | `docs/PROJECT.md`, `docs/GLOSSARY.md`, generated `.github/copilot-instructions.md` |
| `project-archaeology` | Pre-planning (existing codebase) | `docs/ARCHAEOLOGY.md` plus the same three files as `project-intake`, grounded in code evidence |
| `codegraph-setup` | Tooling | CodeGraph installed, wired to the current agent surface (incl. manual Copilot MCP config), project indexed |
| `discipline-protocol` | Cross-lifecycle | Active checkpoint, action guard, detour routing, exceptions, and recovery in `.constraint-kit/discipline.md` |
| `brainstorming` | Design | Approved design doc in `docs/constraint-kit/specs/`, glossary + ADR updates |
| `writing-specs` | Spec | PRD-style spec in `docs/constraint-kit/specs/` |
| `writing-plans` | Plan | Bite-sized, test-first plan in `docs/constraint-kit/plans/` |
| `splunk-itsi-metrics` | Observability | Metric names, HEC emitter, and verified ingestion into SRE's Splunk ITSI |
| `onboarding-azure-metrics-to-splunk` | Observability (customer-side) | Terraform role assignments in the customer's repo, registered metric subscriptions, verified data in Splunk |

Flow: `project-intake` *or* `project-archaeology` (which uses
`codegraph-setup`) → `brainstorming` → `writing-specs` →
`writing-plans` → hand off to the **constraint-dev** plugin for execution.
`discipline-protocol` spans that flow and remains active until explicit
completion, abandonment, or reset.

The two observability skills sit outside that flow and are used on
demand. `splunk-itsi-metrics` covers a service emitting its *own* metrics;
`onboarding-azure-metrics-to-splunk` covers a customer team getting their
*existing Azure* metrics pulled into Splunk by SRE's Azure Splunk Metric
Service.

## Agents

- **planner** — routes intake (`project-intake` for new projects,
  `project-archaeology` for existing codebases) and drives the design
  stages; writes only to `docs/`, `docs/constraint-kit/`, and
    `.github/copilot-instructions.md`, plus the git-ignored active discipline
    ledger and its exact `.gitignore` rule; never source code. Uses CodeGraph
    for structural code questions.

## Credits

Skills adapted and merged from
[obra/superpowers](https://github.com/obra/superpowers)
(`brainstorming`, `writing-plans`) and
[mattpocock/skills](https://github.com/mattpocock/skills)
(`grilling`, `grill-with-docs`, `domain-modeling`, `to-spec`,
`codebase-design`). `project-archaeology` is modernized from
constraint-kit's own pre-2.0 `session-archaeology` skill; code
discovery uses
[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)
(Copilot setup per
[codegraph#718](https://github.com/colbymchenry/codegraph/pull/718)).
See each SKILL.md for details.
