# Upgrading Constraint-Kit Layout Skill — Spec

> Note: this constraint-kit repo (a plugin marketplace, not a typical
> consumer project) does not currently have its own `docs/PROJECT.md` or
> `docs/GLOSSARY.md`. Their absence is not a blocker for this spec; the
> Glossary Additions section below records the terms this feature
> introduces so a future `docs/GLOSSARY.md` (or a consuming repo's) can
> adopt them.

## Problem Statement

Several repos (`runbooks2`, `runbooks`, `itsi-service-observability`,
`zabbix-scanner`, and others outside this workspace) adopted
constraint-kit under an older on-disk convention:
`.constraint-kit/PROJECT.md`, `.constraint-kit/GLOSSARY.md`,
`.constraint-kit/ARCHAEOLOGY.md`, `.constraint-kit/plans/`,
`.constraint-kit/specs/`, `.constraint-kit/adr/`,
`.constraint-kit/agent*.yaml`, and root-level files like
`SESSION_PLAN.md` / `ARCHAEOLOGY_NOTES.md`.

The current convention has moved these files to `docs/PROJECT.md`,
`docs/GLOSSARY.md`, `docs/ARCHAEOLOGY.md`, and
`docs/constraint-kit/{specs,plans,adr}/`, with
`.github/copilot-instructions.md` generated separately.

There is no repeatable, disciplined way to move a repo from the legacy
layout to the current one. A raw migration script would silently move or
delete files without judgment — but legacy repos vary (not every repo has
every legacy file; some have stray, unrecognized files near the migrated
area), so blind, non-interactive automation risks clobbering content or
discarding something the user still needs. The migration needs to live
inside constraint-kit's skill discipline: mostly-silent for the
unambiguous parts, but interactive wherever real judgment is required.

## Solution

Add a new skill, `upgrading-constraint-kit-layout`, to the
`constraint-design` plugin. It scans a target repo for legacy-layout
artifacts, silently moves everything unambiguous, and stops to ask the
user — one item at a time — only where a decision requires judgment
(destination conflicts, `.constraint-kit/agent*.yaml` disposition, and
any stray/unrecognized item found near the legacy area). It reports one
final summary of what moved, what was left, what was deleted, and what
still needs manual attention.

The skill is reachable two ways: by explicit user request, and passively
— `project-intake` and `project-archaeology` each gain a small startup
check that detects legacy-layout markers and offers to run this skill
first before continuing their normal flow.

## User Stories

1. As a user who adopted constraint-kit early, I want to run a single
   skill that moves my repo from the legacy `.constraint-kit/` layout to
   the current `docs/` layout, so that my repo matches what every other
   constraint-kit skill now expects.
2. As a user with several legacy repos, I want the migration to handle
   whichever subset of legacy files each repo actually has, so that I
   don't need a different procedure per repo.
3. As a user running the migration, I want unambiguous moves (no
   destination conflict, clearly a known legacy file) to happen silently,
   so that I'm not asked to confirm things that have only one reasonable
   answer.
4. As a user running the migration, I want to be asked, one at a time,
   whenever there's a genuine conflict — e.g. both a legacy
   `.constraint-kit/ARCHAEOLOGY.md` and a root `ARCHAEOLOGY_NOTES.md`
   exist, or the `docs/` destination already has content — so that no
   content is silently overwritten or merged without my say-so.
5. As a user running the migration, I want to always be asked whether to
   delete or keep each `.constraint-kit/agent*.yaml` file, so that the
   skill never unilaterally decides the fate of agent configuration.
6. As a user running the migration, I want to be asked about any stray or
   unrecognized item near the legacy area (e.g. `pizza_tracker_todo.md`,
   `profile-baseline-*.md`, `plans/artifacts/`) with a leave/move/delete
   choice, so that nothing outside the known legacy-layout list is
   silently moved or discarded.
7. As a user running the migration in a git repository, I want moves done
   with `git mv`, so that file rename history is preserved.
8. As a user running the migration in a non-git repository, I want the
   skill to fall back to a plain filesystem move, so that the migration
   still works.
9. As a user with uncommitted changes in my working tree, I want the
   skill to stop immediately and tell me to commit or stash first, so
   that the migration never mixes with unrelated in-progress changes and
   never becomes hard to review or revert.
10. As a user, I want `.constraint-kit/sdd/` left completely untouched by
    this skill, so that my SDD scratch workspace isn't disturbed by a
    layout migration that has nothing to do with it.
11. As a user, I want `.github/copilot-instructions.md` left untouched by
    this skill, so that regenerating it stays the responsibility of
    `project-intake` / `project-archaeology`, not this migration.
12. As a user running the migration, I want one final summary — what
    moved, what was left in place, what was deleted, and what still needs
    my manual attention — so that I have a clear record of the outcome
    without having narrated every trivial step along the way.
13. As a user starting `project-intake` or `project-archaeology` on a
    repo that still has legacy-layout markers, I want to be offered the
    chance to run the migration first, so that I don't accidentally build
    new `docs/` content next to stale `.constraint-kit/` content.
14. As a user who declines the offered migration during `project-intake`
    or `project-archaeology`, I want those skills to proceed with their
    normal flow anyway, so that the offer is a courtesy, not a blocker.
15. As a maintainer of constraint-kit, I want this skill's frontmatter and
    structure to follow the same convention as `project-archaeology` and
    `project-intake`, so that it's discoverable and consistent with the
    rest of the `constraint-design` plugin.
16. As a maintainer of constraint-kit, I want the passive-detection
    addition to `project-intake` and `project-archaeology` to be a small,
    clearly-scoped addition to their existing SKILL.md files, not a
    rewrite of their flow, so that their existing behavior for
    already-current-layout repos is unaffected.

## Implementation Decisions

1. **Placement:** new skill at
   `plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md`,
   named `upgrading-constraint-kit-layout`, following the frontmatter
   (`name` + `description`) and section conventions used by
   `project-archaeology` and `project-intake` (announce-at-start line,
   Outputs/process sections, Red flags section).

2. **Legacy-layout inventory** the skill recognizes (any subset may be
   present per repo):
   - `.constraint-kit/PROJECT.md` → `docs/PROJECT.md`
   - `.constraint-kit/GLOSSARY.md` → `docs/GLOSSARY.md`
   - `.constraint-kit/ARCHAEOLOGY.md` → `docs/ARCHAEOLOGY.md`
   - `.constraint-kit/plans/` → `docs/constraint-kit/plans/`
   - `.constraint-kit/specs/` → `docs/constraint-kit/specs/`
   - `.constraint-kit/adr/` → `docs/constraint-kit/adr/`
   - `.constraint-kit/agent.yaml`, `agent-base.yaml`,
     `agent-supervisor.yaml`, `agent-implementer.yaml` → no automatic
     destination; disposition always asked (see decision 6)
   - root-level `SESSION_PLAN.md`, `ARCHAEOLOGY_NOTES.md` (or
     similarly-named variants) → candidate merge/replace targets for
     `docs/PROJECT.md` / `docs/ARCHAEOLOGY.md`; always a destination
     conflict, never silent (see decision 5)

   Explicitly out of scope for movement: `.constraint-kit/sdd/` (left
   exactly where it is) and `.github/copilot-instructions.md` (untouched,
   regenerated only by `project-intake`/`project-archaeology`).

3. **Execution model: single pass, no upfront full-plan confirmation
   gate.**
   1. Scan the repo and classify every legacy-area item into one of:
      (a) unambiguous move with no destination conflict, (b) a
      `.constraint-kit/agent*.yaml` file, or (c) unrecognized/stray item.
   2. Resolve every item in classes (b) and (c), and every destination
      conflict found in class (a), interactively — one at a time, as
      encountered during the scan, not batched into an upfront plan the
      user approves once.
   3. Execute the full batch of moves: the unambiguous ones from step 1
      plus the now-resolved ones from step 2.
   4. Report one final summary.

4. **Silence boundary:** unambiguous, conflict-free moves produce no
   per-item narration during execution — they appear only in the final
   summary. Interactive stops are reserved strictly for genuine ambiguity
   (destination conflicts, `agent*.yaml` files, stray items). This is a
   deliberate departure from other constraint-kit skills' step-by-step
   narration, justified because the moves in this class have exactly one
   reasonable outcome.

5. **Destination conflict handling:** a conflict exists when either (a)
   both a legacy source and a root-level variant point at the same
   `docs/` destination (e.g. `.constraint-kit/ARCHAEOLOGY.md` and root
   `ARCHAEOLOGY_NOTES.md` both map toward `docs/ARCHAEOLOGY.md`), or (b)
   the `docs/` destination already has content. In either case, the skill
   surfaces both sides to the user and asks how to reconcile them (which
   file wins, or the user merges manually outside the skill). The skill
   never auto-merges file content.

6. **`.constraint-kit/agent*.yaml` disposition:** always ask, per file,
   per repo, whether to delete or leave in place. This is never inferred
   or defaulted, even if every other legacy file in the repo was an
   unambiguous move.

7. **Stray/unrecognized items:** anything found in or near the legacy
   area (`.constraint-kit/`, and root-level files that look
   migration-adjacent) that does not match the known legacy-layout
   inventory in decision 2 is a stray item. There is no allowlist or
   denylist of specific stray filenames to special-case (e.g.
   `pizza_tracker_todo.md`, `profile-baseline-*.md`,
   `plans/artifacts/` are examples, not a fixed list) — the skill asks
   the user per item with a generic leave / move / delete choice, and if
   the user chooses move, asks where.

8. **Move mechanics:**
   - If the target repo is a git repository, use `git mv` for every move
     (preserves rename history).
   - If it is not a git repository, fall back to a plain filesystem move.
   - Directory creation for new `docs/` / `docs/constraint-kit/`
     subdirectories happens as needed during the move.

9. **Dirty working tree guard:** before doing anything else, check
   whether the target repo's working tree has uncommitted changes. If it
   does, stop immediately (no scanning, no moves) and tell the user to
   commit or stash first. Do not proceed until the tree is clean.

10. **Final summary contents:** one report at the end of the run, covering
    four buckets — what moved (unambiguous + resolved-ambiguous, with
    source → destination), what was left in place (e.g. an
    `agent*.yaml` the user chose to keep, or a stray item left alone),
    what was deleted (agent*.yaml or stray items the user chose to
    delete), and what still needs manual attention (e.g. a destination
    conflict where the user deferred to merge manually later).

11. **Passive detection addition to `project-intake` and
    `project-archaeology`:** each of those two existing SKILL.md files
    gets a small addition — a startup check, before their own normal
    process begins, for legacy-layout markers (e.g.
    `.constraint-kit/PROJECT.md` or any `.constraint-kit/agent*.yaml`
    present). If found, the skill offers to run
    `upgrading-constraint-kit-layout` first. If the user accepts, that
    skill runs to completion (including its own interactive stops), then
    control returns to the original skill's normal process. If the user
    declines, the original skill proceeds as it does today — this is an
    offer, not a gate. This addition should be scoped to a few lines in
    each file's existing "process" flow (e.g. a new first paragraph or
    step 0), not a restructuring of either skill.

12. **Non-goals for this skill:** it does not regenerate
    `.github/copilot-instructions.md`, does not write or update
    `docs/PROJECT.md` / `docs/GLOSSARY.md` content (only relocates
    existing files, subject to conflict resolution), and does not touch
    `.constraint-kit/sdd/`.

## Testing Decisions

`upgrading-constraint-kit-layout` is a markdown skill definition, not
executable code — there is no test suite to write against it directly.
Verification follows the same pattern already established for skills in
this repo:

- Run `python3 scripts/validate.py` after adding the new skill directory
  and after editing `project-intake`/`project-archaeology`, and fix every
  reported problem. This checks the structural contract (frontmatter
  `name` matches directory name, required sections present, etc.) per
  [AGENTS.md](../../../AGENTS.md).
- Manually verify the new skill's frontmatter `name` field
  (`upgrading-constraint-kit-layout`) matches its directory name exactly,
  per the same convention `project-archaeology` and `project-intake`
  follow.
- Manually verify the marketplace/plugin manifest picks up the new skill
  if `scripts/validate.py` doesn't already enforce that (check
  `plugins/constraint-design/plugin.json` and
  `.claude-plugin/marketplace.json` for whether skills are
  individually listed or auto-discovered).
- Dry-run review: read through the new skill's process section against
  each of the four legacy repos named in the Problem Statement
  (`runbooks2`, `runbooks`, `itsi-service-observability`,
  `zabbix-scanner`) and confirm the described classification (unambiguous
  / agent*.yaml / stray) would produce a sensible outcome for each one's
  actual current contents, without executing any moves — this is a
  documentation/design skill, so "testing" here means confirming the
  written procedure holds up against real target repos, not running
  automated assertions.

## Out of Scope

- Any change to the actual content of `docs/PROJECT.md`,
  `docs/GLOSSARY.md`, or `docs/ARCHAEOLOGY.md` beyond relocating
  existing files (content authoring is `project-intake` /
  `project-archaeology`'s job).
- Regenerating or modifying `.github/copilot-instructions.md`.
- Any change to `.constraint-kit/sdd/`.
- A standalone script or CLI tool that performs the migration outside the
  skill/agent conversational flow — the design explicitly rejects a "raw
  script" so migration stays inside constraint-kit's interactive
  discipline.
- Building or maintaining a fixed allowlist/denylist of known stray
  filenames — the fallback is always "ask the user," not a growing
  special-case list.
- Running the migration against any of the four named example repos as
  part of this spec/plan — those are illustrative targets for design and
  dry-run review, not something this piece of work executes.
- Creating `docs/PROJECT.md` / `docs/GLOSSARY.md` for the constraint-kit
  repo itself (noted as absent during spec-writing; out of scope here).

## Further Notes

### Glossary additions

This constraint-kit repo has no `docs/GLOSSARY.md` of its own today. The
following terms are introduced by this feature and should be added to
`docs/GLOSSARY.md` in any consuming repo (or this repo's own, if one is
created later):

- **Legacy layout** — the pre-migration constraint-kit file arrangement:
  `.constraint-kit/{PROJECT.md,GLOSSARY.md,ARCHAEOLOGY.md,plans/,specs/,
  adr/,agent*.yaml}` plus root-level files like `SESSION_PLAN.md` /
  `ARCHAEOLOGY_NOTES.md`.
- **Current layout** — the present constraint-kit arrangement:
  `docs/{PROJECT.md,GLOSSARY.md,ARCHAEOLOGY.md}` plus
  `docs/constraint-kit/{specs,plans,adr}/` and
  `.github/copilot-instructions.md`.
- **Stray item** — a file or directory found near the migrated area that
  is not recognized as belonging to either the legacy layout or the
  current layout.

### Relationship to existing skills

`upgrading-constraint-kit-layout` is a one-time (per repo) structural
migration step. It hands off to, but is distinct from, both
`project-intake` and `project-archaeology`: those two skills author or
extract `docs/` *content*; this skill only relocates files that already
exist under the legacy layout so that content-authoring skills find
what they expect where they expect it.
