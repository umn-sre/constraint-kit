---
name: upgrading-constraint-kit-layout
description: Use when a repo still has the legacy constraint-kit layout (.constraint-kit/PROJECT.md, GLOSSARY.md, ARCHAEOLOGY.md, plans/, specs/, adr/, agent*.yaml, or root-level SESSION_PLAN.md/ARCHAEOLOGY_NOTES.md) and needs migrating to the current docs/ layout - scans the repo, silently moves unambiguous files, and asks one at a time about destination conflicts, agent*.yaml disposition, and stray items, then reports a final summary. Also invoked passively by project-intake and project-archaeology when they detect legacy markers. Don't use on a repo already on the current docs/ layout, and don't use to author or edit the content of PROJECT.md/GLOSSARY.md/ARCHAEOLOGY.md themselves.
---

# Upgrading Constraint-Kit Layout

One-time-per-repo structural migration from the legacy
`.constraint-kit/` layout to the current `docs/` layout, so that
`project-intake`, `project-archaeology`, and every other constraint-kit
skill finds project context where they now expect it.

**Announce at start:** "I'm using the upgrading-constraint-kit-layout
skill to migrate this repo's layout."

## Outputs

This skill does not author content — it relocates files that already
exist under the legacy layout, plus one report:

| File / action | Content |
|---|---|
| `docs/PROJECT.md`, `docs/GLOSSARY.md`, `docs/ARCHAEOLOGY.md` | Legacy `.constraint-kit/{PROJECT,GLOSSARY,ARCHAEOLOGY}.md`, moved as-is (or the user's chosen side of a conflict) |
| `docs/constraint-kit/{plans,specs,adr}/` | Legacy `.constraint-kit/{plans,specs,adr}/`, moved as-is |
| Final summary (chat output, not a file) | What moved, what was left in place, what was deleted, what still needs manual attention |

Never touched: `.constraint-kit/sdd/`, `.github/copilot-instructions.md`.

## Legacy-layout inventory

| Legacy path | Destination | Classification |
|---|---|---|
| `.constraint-kit/PROJECT.md` | `docs/PROJECT.md` | Unambiguous, unless a destination conflict exists (see below) |
| `.constraint-kit/GLOSSARY.md` | `docs/GLOSSARY.md` | Unambiguous, unless a destination conflict exists |
| `.constraint-kit/ARCHAEOLOGY.md` | `docs/ARCHAEOLOGY.md` | Unambiguous, unless a destination conflict exists |
| `.constraint-kit/plans/` | `docs/constraint-kit/plans/` | Unambiguous, unless a destination conflict exists |
| `.constraint-kit/specs/` | `docs/constraint-kit/specs/` | Unambiguous, unless a destination conflict exists |
| `.constraint-kit/adr/` | `docs/constraint-kit/adr/` | Unambiguous, unless a destination conflict exists |
| `.constraint-kit/agent.yaml`, `agent-base.yaml`, `agent-supervisor.yaml`, `agent-implementer.yaml` | none | Always ask (delete or leave) |
| root `SESSION_PLAN.md`, `ARCHAEOLOGY_NOTES.md` (or similarly named variants) | `docs/PROJECT.md` / `docs/ARCHAEOLOGY.md` | Always a destination conflict |

Never in scope for movement: `.constraint-kit/sdd/` (leave exactly where
it is), `.github/copilot-instructions.md` (untouched).

Anything else found in or near `.constraint-kit/`, or a root-level file
that looks migration-adjacent, and does not match a row above, is a
**stray item** — always ask (see Process step 3).
