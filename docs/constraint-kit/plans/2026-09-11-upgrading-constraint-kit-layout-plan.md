# Upgrading Constraint-Kit Layout Implementation Plan

> **For agentic workers:** REQUIRED: Use the `subagent-driven-development` agent (recommended) or `executing-plans` agent to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `upgrading-constraint-kit-layout` skill to the `constraint-design` plugin, plus small passive-detection additions to `project-intake` and `project-archaeology`, so repos on the legacy `.constraint-kit/` layout can be migrated to the current `docs/` layout under constraint-kit's interactive discipline.

**Architecture:** This is a documentation/prose deliverable — three markdown files change (one new, two edited), no application code. "Testing" is `scripts/validate.py` structural validation, manual convention checks against `project-archaeology`/`project-intake`, and a dry-run read-through of the new skill's procedure against four real legacy repos. No standalone script is produced (explicitly rejected in brainstorming).

**Tech Stack:** Markdown (skill frontmatter + prose), `scripts/validate.py` (stdlib Python, already exists, not modified).

---

## Glossary (for this plan)

Recorded here because this repo has no `docs/GLOSSARY.md` yet (see spec note). Add these to `docs/GLOSSARY.md` in any repo that gets one later, including this one.

- **Legacy layout** — the pre-migration constraint-kit file arrangement: `.constraint-kit/{PROJECT.md,GLOSSARY.md,ARCHAEOLOGY.md,plans/,specs/,adr/,agent*.yaml}` plus root-level files like `SESSION_PLAN.md` / `ARCHAEOLOGY_NOTES.md`.
- **Current layout** — the present constraint-kit arrangement: `docs/{PROJECT.md,GLOSSARY.md,ARCHAEOLOGY.md}` plus `docs/constraint-kit/{specs,plans,adr}/` and `.github/copilot-instructions.md`.
- **Stray item** — a file or directory found near the migrated area that is not recognized as belonging to either the legacy layout or the current layout.

## Decision records referenced by this plan

These are Implementation Decisions from `docs/constraint-kit/specs/2026-09-11-upgrading-constraint-kit-layout-spec.md` — this plan does not re-litigate them, only implements them:

- Decision 1: placement and frontmatter/section convention (mirrors `project-archaeology`/`project-intake`).
- Decision 2: legacy-layout inventory table.
- Decision 3: single-pass execution model (scan+classify, resolve ambiguity as encountered, execute batch, one final summary).
- Decision 4: silence boundary (no per-item narration for unambiguous moves).
- Decision 5: destination conflict handling (never auto-merge).
- Decision 6: `agent*.yaml` disposition always asked.
- Decision 7: stray items always asked, no allowlist/denylist.
- Decision 8: `git mv` in git repos, plain move otherwise.
- Decision 9: dirty working tree guard, stop immediately.
- Decision 10: final summary's four buckets.
- Decision 11: passive-detection addition to `project-intake`/`project-archaeology`.
- Decision 12: non-goals (no copilot-instructions regen, no PROJECT.md/GLOSSARY.md content authoring, no touching `.constraint-kit/sdd/`).

---

## File Structure

| File | Responsibility |
|---|---|
| `plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md` (new) | The migration skill itself: frontmatter, Outputs, legacy-layout inventory, Process (dirty-tree guard → scan/classify → resolve ambiguity → execute → summarize), Red flags. |
| `plugins/constraint-design/skills/project-intake/SKILL.md` (modify) | Add a "step 0" passive-detection paragraph before its existing "1. Explore before asking" step. No other change. |
| `plugins/constraint-design/skills/project-archaeology/SKILL.md` (modify) | Add a "step 0" passive-detection paragraph before its existing "1. Set up code intelligence" step. No other change. |
| `plugins/constraint-design/plugin.json` | Not modified — its `"skills": ["skills/"]` entry auto-discovers every subdirectory under `skills/`, confirmed in Task 9 below. Listed here only so the engineer doesn't go looking for a manifest edit that isn't needed. |

No other files change. No script, CLI, or test file is created (spec explicitly rejects a standalone script).

---

### Task 1: Scaffold the new skill's frontmatter and shell

**Files:**
- Create: `plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md`

- [ ] **Step 1: Create the file with frontmatter, title, and announce line**

```markdown
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
```

- [ ] **Step 2: Run the structural validator**

Run from the constraint-kit repo root:

```bash
cd /Users/peiffer/constraint-kit-all/constraint-kit
python3 scripts/validate.py
```

Expected: `OK — marketplace and plugin structure valid` (frontmatter
`name`/`description` present and `name` matches the directory name;
`plugin.json`'s `"skills/"` entry auto-discovers the new directory, so
no manifest edit is needed yet).

- [ ] **Step 3: Commit**

```bash
git add plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md
git commit -m "docs: scaffold upgrading-constraint-kit-layout skill frontmatter"
```

---

### Task 2: Add Outputs and legacy-layout inventory sections

**Files:**
- Modify: `plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md`

- [ ] **Step 1: Append the Outputs section**

Add after the "Announce at start" line from Task 1:

```markdown
## Outputs

This skill does not author content — it relocates files that already
exist under the legacy layout, plus one report:

| File / action | Content |
|---|---|
| `docs/PROJECT.md`, `docs/GLOSSARY.md`, `docs/ARCHAEOLOGY.md` | Legacy `.constraint-kit/{PROJECT,GLOSSARY,ARCHAEOLOGY}.md`, moved as-is (or the user's chosen side of a conflict) |
| `docs/constraint-kit/{plans,specs,adr}/` | Legacy `.constraint-kit/{plans,specs,adr}/`, moved as-is |
| Final summary (chat output, not a file) | What moved, what was left in place, what was deleted, what still needs manual attention |

Never touched: `.constraint-kit/sdd/`, `.github/copilot-instructions.md`.
```

- [ ] **Step 2: Append the legacy-layout inventory section**

Add immediately after Outputs:

```markdown
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
```

- [ ] **Step 3: Run the structural validator**

```bash
cd /Users/peiffer/constraint-kit-all/constraint-kit
python3 scripts/validate.py
```

Expected: `OK — marketplace and plugin structure valid`.

- [ ] **Step 4: Commit**

```bash
git add plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md
git commit -m "docs: add outputs and legacy-layout inventory to upgrading-constraint-kit-layout"
```

---

### Task 3: Add Process steps 1–2 (dirty-tree guard, scan and classify)

**Files:**
- Modify: `plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md`

- [ ] **Step 1: Append the Process heading and steps 1–2**

Add after the legacy-layout inventory section from Task 2:

```markdown
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
```

- [ ] **Step 2: Run the structural validator**

```bash
cd /Users/peiffer/constraint-kit-all/constraint-kit
python3 scripts/validate.py
```

Expected: `OK — marketplace and plugin structure valid`.

- [ ] **Step 3: Commit**

```bash
git add plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md
git commit -m "docs: add dirty-tree guard and scan/classify steps to upgrading-constraint-kit-layout"
```

---

### Task 4: Add Process steps 3–4 (resolve ambiguity, execute the batch)

**Files:**
- Modify: `plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md`

- [ ] **Step 1: Append Process steps 3–4**

Add after step 2 from Task 3:

```markdown
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
```

- [ ] **Step 2: Run the structural validator**

```bash
cd /Users/peiffer/constraint-kit-all/constraint-kit
python3 scripts/validate.py
```

Expected: `OK — marketplace and plugin structure valid`.

- [ ] **Step 3: Commit**

```bash
git add plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md
git commit -m "docs: add ambiguity-resolution and batch-execution steps to upgrading-constraint-kit-layout"
```

---

### Task 5: Add Process step 5 (final summary) and Red flags; complete the skill file

**Files:**
- Modify: `plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md`

- [ ] **Step 1: Append Process step 5**

Add after step 4 from Task 4:

```markdown
### 5. Report the final summary

One report, covering four buckets:

1. **Moved** — source → destination, for every file actually moved
   (unambiguous and resolved-ambiguous together).
2. **Left in place** — e.g. an `agent*.yaml` the user chose to keep, or
   a stray item the user chose to leave.
3. **Deleted** — `agent*.yaml` or stray items the user chose to delete.
4. **Needs manual attention** — e.g. a destination conflict the user
   deferred to merge manually later.
```

- [ ] **Step 2: Append the Red flags section**

```markdown
## Red flags

- Moving or deleting anything before confirming the working tree is
  clean
- Batching ambiguous items into an upfront plan the user approves once,
  instead of resolving each as it's found
- Narrating or asking about an unambiguous move
- Inferring or defaulting an `agent*.yaml` disposition instead of asking
- Auto-merging two sides of a destination conflict
- Moving or deleting `.constraint-kit/sdd/` or
  `.github/copilot-instructions.md`
- Special-casing a specific stray filename instead of asking generically
```

- [ ] **Step 3: Run the structural validator**

```bash
cd /Users/peiffer/constraint-kit-all/constraint-kit
python3 scripts/validate.py
```

Expected: `OK — marketplace and plugin structure valid`.

- [ ] **Step 4: Manually re-read the complete file top to bottom**

Confirm the file now has, in order: frontmatter (`name`, `description`),
title, Announce-at-start line, Outputs, Legacy-layout inventory,
Process (steps 1–5), Red flags. This is the same section shape as
`project-archaeology`'s and `project-intake`'s SKILL.md files.

- [ ] **Step 5: Commit**

```bash
git add plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md
git commit -m "docs: complete upgrading-constraint-kit-layout skill with summary and red flags"
```

---

### Task 6: Add passive-detection addition to `project-intake`

**Files:**
- Modify: `plugins/constraint-design/skills/project-intake/SKILL.md`

- [ ] **Step 1: Read the current Process section**

Open the file and find the existing `### 1. Explore before asking`
heading under `## Process`. The new step goes immediately before it.

- [ ] **Step 2: Insert step 0**

Use `replace_string_in_file`-style insertion: find this exact existing
text —

```markdown
## Process

### 1. Explore before asking
```

— and replace it with:

```markdown
## Process

### 0. Check for a legacy constraint-kit layout

Before exploring, check whether this repo still has legacy-layout
markers: `.constraint-kit/PROJECT.md`, `.constraint-kit/GLOSSARY.md`,
or any `.constraint-kit/agent*.yaml`. If any are present, offer to run
the `upgrading-constraint-kit-layout` skill first. If the user accepts,
run it to completion, then continue below. If they decline, continue
below as normal — this is an offer, not a gate.

### 1. Explore before asking
```

- [ ] **Step 3: Run the structural validator**

```bash
cd /Users/peiffer/constraint-kit-all/constraint-kit
python3 scripts/validate.py
```

Expected: `OK — marketplace and plugin structure valid`.

- [ ] **Step 4: Commit**

```bash
git add plugins/constraint-design/skills/project-intake/SKILL.md
git commit -m "docs: offer upgrading-constraint-kit-layout from project-intake on legacy markers"
```

---

### Task 7: Add passive-detection addition to `project-archaeology`

**Files:**
- Modify: `plugins/constraint-design/skills/project-archaeology/SKILL.md`

- [ ] **Step 1: Read the current Process section**

Find the existing `### 1. Set up code intelligence` heading under
`## Process`. The new step goes immediately before it.

- [ ] **Step 2: Insert step 0**

Find this exact existing text —

```markdown
## Process

### 1. Set up code intelligence
```

— and replace it with:

```markdown
## Process

### 0. Check for a legacy constraint-kit layout

Before setting up code intelligence, check whether this repo still has
legacy-layout markers: `.constraint-kit/PROJECT.md`,
`.constraint-kit/GLOSSARY.md`, or any `.constraint-kit/agent*.yaml`. If
any are present, offer to run the `upgrading-constraint-kit-layout`
skill first. If the user accepts, run it to completion, then continue
below. If they decline, continue below as normal — this is an offer,
not a gate.

### 1. Set up code intelligence
```

- [ ] **Step 3: Run the structural validator**

```bash
cd /Users/peiffer/constraint-kit-all/constraint-kit
python3 scripts/validate.py
```

Expected: `OK — marketplace and plugin structure valid`.

- [ ] **Step 4: Commit**

```bash
git add plugins/constraint-design/skills/project-archaeology/SKILL.md
git commit -m "docs: offer upgrading-constraint-kit-layout from project-archaeology on legacy markers"
```

---

### Task 8: Manual frontmatter/structure convention review

**Files:** none changed — this is a checklist-only verification task against files from Tasks 1–7.

- [ ] **Step 1: Confirm frontmatter contract**

Open `plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md`
and confirm by eye:
- `name: upgrading-constraint-kit-layout` matches the directory name
  `upgrading-constraint-kit-layout` exactly.
- `description` is present and states when to use the skill (this
  duplicates what `validate.py` already checks — do it manually too,
  since `validate.py` doesn't check description *quality*, only
  presence).

- [ ] **Step 2: Confirm section-shape parity with `project-archaeology`/`project-intake`**

Side-by-side check — the new skill should have the same section shape:
- `# <Title>` immediately after frontmatter — present.
- A one-paragraph explanation of what the skill does and why —
  present.
- `**Announce at start:** "..."` line — present, matches the style
  `"I'm using the <skill-name> skill to <verb phrase>."` used by both
  reference skills.
- `## Outputs` section (table format) — present.
- `## Process` section with numbered `###` sub-steps — present.
- `## Red flags` section (bulleted list) — present.

- [ ] **Step 3: Confirm the two edited files kept their existing content intact**

Open `plugins/constraint-design/skills/project-intake/SKILL.md` and
`plugins/constraint-design/skills/project-archaeology/SKILL.md`. Confirm
each file's only change from before Task 6 / Task 7 is the new `### 0.`
step — no existing heading, paragraph, or list was reworded, reordered,
or removed.

- [ ] **Step 4: Record the outcome**

No commit needed for this task (no files changed) — this step is a
sign-off before Task 9.

---

### Task 9: Manual marketplace/plugin manifest check

**Files:** none changed — read-only verification.

- [ ] **Step 1: Inspect the plugin manifest**

```bash
cat /Users/peiffer/constraint-kit-all/constraint-kit/plugins/constraint-design/plugin.json
```

Confirm the `"skills"` field is `["skills/"]` — a directory reference,
not a list of individual skill paths.

- [ ] **Step 2: Confirm auto-discovery in `scripts/validate.py`**

Read `check_plugin()` in `scripts/validate.py`: it iterates every
subdirectory of `plugin_dir / "skills"` and calls `check_skill()` on
each one, regardless of what `plugin.json`'s `"skills"` list contains.
The `"skills": ["skills/"]` entry in `plugin.json` is checked only for
existence (`(plugin_dir / listed).exists()`), not enumerated
individually.

- [ ] **Step 3: Confirm Task 1's validator run already proved this**

Task 1 Step 2 already ran `scripts/validate.py` after creating the new
skill directory and got `OK`, without any edit to `plugin.json` or
`.claude-plugin/marketplace.json`. That is the empirical confirmation:
no manifest edit is needed for the new skill to be picked up.

- [ ] **Step 4: Record the outcome**

No commit needed for this task (no files changed). Conclusion:
`plugins/constraint-design/plugin.json` and
`.claude-plugin/marketplace.json` require no changes for this feature.

---

### Task 10: Dry-run review against the four real legacy repos

**Files:** none changed — this task reads the four repos listed in the spec's Problem Statement and confirms the finished skill's classification rules produce a sensible outcome for each one's actual current contents. No moves are executed (explicitly out of scope per the spec).

- [ ] **Step 1: Walk `runbooks2` against the finished Process section**

```bash
ls -la /Users/peiffer/runbooks2
ls -la /Users/peiffer/runbooks2/.constraint-kit
ls -la /Users/peiffer/runbooks2/docs
```

Confirm the classification the skill's Process section would produce
matches this expected read:
- `.constraint-kit/{PROJECT.md,GLOSSARY.md,ARCHAEOLOGY.md,plans/,specs/}`
  → unambiguous moves, **except** `ARCHAEOLOGY.md`, which is a
  **destination conflict** because root `ARCHAEOLOGY_NOTES.md` also
  exists and targets `docs/ARCHAEOLOGY.md`.
- Root `SESSION_PLAN.md` → destination conflict against
  `docs/PROJECT.md` (no legacy `.constraint-kit/PROJECT.md` conflict in
  this repo's case beyond the plain move, but `SESSION_PLAN.md` itself
  is always a conflict per the inventory table — surface it and ask).
- `.constraint-kit/agent-base.yaml`, `agent-implementer.yaml` → ask
  delete-or-leave for each.
- `.constraint-kit/profile-baseline-2026-08-20.md` → stray item, ask
  leave/move/delete.
- `.constraint-kit/sdd/` → left untouched.
- `docs/` has no existing `PROJECT.md`/`GLOSSARY.md`/`ARCHAEOLOGY.md` of
  its own today, so the "destination already has content" trigger does
  not apply here — the conflicts in this repo come from the
  root-level-variant trigger only.

If the written Process section doesn't clearly produce this reading,
fix the skill file now and re-run `scripts/validate.py`.

- [ ] **Step 2: Walk `runbooks` against the finished Process section**

```bash
ls -la /Users/peiffer/runbooks
ls -la /Users/peiffer/runbooks/.constraint-kit
```

Confirm the expected read: this repo's `.constraint-kit/` has no
`PROJECT.md`, `GLOSSARY.md`, or `ARCHAEOLOGY.md` at all — only
`plans/`, `specs/`, four `agent*.yaml` files
(`agent.yaml`, `agent-base.yaml`, `agent-supervisor.yaml`,
`agent-implementer.yaml`), and `pizza_tracker_todo.md`. Expected
classification:
- `.constraint-kit/plans/`, `.constraint-kit/specs/` → unambiguous
  moves (no root-level `SESSION_PLAN.md`/`ARCHAEOLOGY_NOTES.md` exist
  in this repo, so no conflict).
- All four `agent*.yaml` files → ask delete-or-leave individually.
- `pizza_tracker_todo.md` → stray item, ask leave/move/delete.

- [ ] **Step 3: Walk `itsi-service-observability` against the finished Process section**

```bash
ls -la /Users/peiffer/itsi-service-observability
ls -la /Users/peiffer/itsi-service-observability/.constraint-kit
```

Confirm the expected read: `.constraint-kit/{ARCHAEOLOGY.md,GLOSSARY.md,
PROJECT.md,plans/,specs/}` only — no `agent*.yaml`, no root-level
`SESSION_PLAN.md`/`ARCHAEOLOGY_NOTES.md`, no stray items, no existing
`docs/PROJECT.md` etc. Expected classification: every item is an
unambiguous move, no interactive stops at all — this repo is the
"clean" case that should produce a final summary with only a "Moved"
bucket populated.

- [ ] **Step 4: Walk `zabbix-scanner` against the finished Process section**

```bash
ls -la /Users/peiffer/zabbix-scanner
ls -la /Users/peiffer/zabbix-scanner/.constraint-kit
```

Confirm the expected read: `.constraint-kit/{GLOSSARY.md,PROJECT.md,
adr/,plans/,specs/,sdd/}` — no `ARCHAEOLOGY.md`, no `agent*.yaml`, no
root-level variants, no stray items. Expected classification: every
item except `sdd/` is an unambiguous move (`adr/` exercises the
`docs/constraint-kit/adr/` destination, which the other three repos
don't); `sdd/` is left untouched per the never-in-scope rule.

- [ ] **Step 5: Record any procedure gaps found**

If any of the four walkthroughs surfaced a scenario the written
Process section doesn't clearly handle (for example, ambiguity about
what counts as "near" `.constraint-kit/` for stray-item purposes), fix
the skill file now, re-run `scripts/validate.py`, and note the fix in
the commit message.

- [ ] **Step 6: Commit only if Step 5 produced a fix**

```bash
git add plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md
git commit -m "docs: tighten upgrading-constraint-kit-layout after dry-run review against 4 repos"
```

If no fix was needed, skip this step — there is nothing to commit.

---

### Task 11: Final wrap-up

**Files:** none changed — confirms the branch is ready to hand off.

- [ ] **Step 1: Run the full validator one more time**

```bash
cd /Users/peiffer/constraint-kit-all/constraint-kit
python3 scripts/validate.py
```

Expected: `OK — marketplace and plugin structure valid`.

- [ ] **Step 2: Review the full diff against `main`**

```bash
git diff main --stat
```

Expected: exactly three files changed —
`plugins/constraint-design/skills/upgrading-constraint-kit-layout/SKILL.md`
(new), `plugins/constraint-design/skills/project-intake/SKILL.md`
(modified), `plugins/constraint-design/skills/project-archaeology/SKILL.md`
(modified). No script, test, or manifest file appears in the diff.

- [ ] **Step 3: Confirm log matches the task history**

```bash
git log --oneline main..HEAD
```

Expected: one commit per task above that produced a change (Tasks 1–7,
plus Task 10 only if it required a fix).
