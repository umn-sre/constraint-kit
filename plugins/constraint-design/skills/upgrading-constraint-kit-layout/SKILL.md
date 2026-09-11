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

## Process

### 1. Check for a clean working tree

Before anything else, check whether the target repo has uncommitted
changes (`git status --porcelain`, or the non-git equivalent judgment
if there's no `.git`). If the tree is dirty, stop immediately — no
scanning, no moves — and tell the user to commit or stash first. Do not
proceed until it reports clean.

### 2. Scan and classify

Walk `.constraint-kit/` (if present) and the repo root for anything
matching the legacy-layout inventory above. Classify every item found
into exactly one of:

- **(a) Unambiguous move** — matches a legacy-layout row, and the
  `docs/` destination does not already have conflicting content, and no
  root-level variant also targets the same destination.
- **(b) `agent*.yaml`** — any `.constraint-kit/agent*.yaml` file.
- **(c) Stray item** — doesn't match any legacy-layout row.

A destination conflict (which promotes an otherwise-(a) item into an
interactive resolution) exists when either:
- both a legacy source and a root-level variant point at the same
  `docs/` destination (e.g. `.constraint-kit/ARCHAEOLOGY.md` and root
  `ARCHAEOLOGY_NOTES.md` both target `docs/ARCHAEOLOGY.md`), or
- the `docs/` destination already has content.

### 3. Resolve ambiguity as encountered

Resolve every (b), (c), and destination-conflict item one at a time, as
it's found during the scan — not batched into an upfront plan the user
approves once. Do not narrate or ask about class (a) items; they appear
only in the final summary.

- **Destination conflict:** show the user both sides (paths and a short
  description of each, e.g. size/last-modified or a one-line content
  summary) and ask which one wins, or whether they'd rather merge
  manually outside this skill (in which case: leave both files in place
  and record it under "needs manual attention" in the final summary).
  Never auto-merge content.
- **`agent*.yaml`:** ask, per file, whether to delete or leave in place.
  Never infer or default this, even if every other item in the repo was
  an unambiguous move.
- **Stray item:** ask with a generic leave / move / delete choice. If
  the user chooses move, ask where.

### 4. Execute the batch

Once every ambiguous item has a resolution:

- If the target repo is a git repository, move every file with `git mv`
  (source, then destination), creating any needed `docs/` or
  `docs/constraint-kit/` subdirectories first.
- If it is not a git repository, use a plain filesystem move instead.
- Execute unambiguous moves from step 2 and the now-resolved items from
  step 3 together, in one batch.
