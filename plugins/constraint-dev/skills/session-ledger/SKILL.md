---
name: session-ledger
description: Use during any implementation session - tracks progress in a session ledger, verifies every file edit actually applied, halts loops before they burn context, watches the token budget, and wraps up by updating the plan and appending a lessons-learned/budget entry to .constraint-kit/PROJECT.md so the next session starts in a known state.
---

# Session Ledger

Maintain session integrity from first turn to last: track progress
against the plan, detect and surface loops before they consume context,
monitor budget, verify file changes were actually applied, and execute
a clean wrap-up that leaves the project in a known state for the next
session.

Active in every implementation session — the `implementer` agent and
the `executing-plans` skill follow it directly. Under
`subagent-driven-development`, the workspace ledger at
`.constraint-kit/sdd/<plan-basename>/progress.md` **is** the session
ledger; the verification, loop, budget, and wrap-up rules here still
apply to every dispatched subagent and to the conductor.

## 1. Session open

On the first turn, read `.constraint-kit/PROJECT.md` (Constraints and
Working agreement, plus the Session log's recent entries) and the
active plan in `.constraint-kit/plans/`. State the task list and done
condition, then initialize the ledger — in the SDD workspace when one
exists, otherwise as a running block in the conversation:

```markdown
## Session Ledger — <date> <plan/topic>
### Tasks
- [ ] <task>
### Files touched
| file | action | verified |
|---|---|---|
### Attempts log
| turn | file/operation | outcome |
|---|---|---|
### Budget
consumed: ~0% · warn: 70% · stop: 85%
```

Do not begin task work until the ledger is initialized. The thresholds
are defaults; a project may override them in PROJECT.md's Working
agreement.

## 2. Per-turn discipline

Before producing output each turn:

- **Attempts check** — if the current operation (same file + same
  intent) already appears in the attempts log, halt. State the previous
  outcome and a root-cause hypothesis before trying anything else.
- **Budget check** — use the harness's context indicator when it has
  one; otherwise estimate (1000 words ≈ 750 tokens). Past the warning
  threshold, prepend a one-line warning and keep working. Past the hard
  stop, start no new task — go straight to wrap-up (§7).

## 3. File verification

After every file write or edit, confirm it applied before reporting
success: read the file back, or check `git diff --stat` shows a
non-zero delta, or confirm the target string is present. If
verification fails:

- Do not report success, and do not ask the user to "test and see".
- Log the attempt with outcome `PHANTOM`, state "Edit did not apply.
  Diagnosing.", and give a root-cause hypothesis (wrong path,
  permissions, encoding, stale buffer) before re-attempting.
- Maximum two re-attempts per edit; on the second failure, halt and
  escalate with the full diagnosis.

On a surface without file access, every proposed change ends with:
"This is a proposed change only — confirm it is in place before I
continue," and the task stays incomplete until the user confirms.

## 4. Loop detection

A loop is the same file **and** the same intent appearing twice in the
attempts log with no verified success between them. On detection: halt,
state what was attempted, what was expected, what actually happened
each time, and a hypothesis — then ask the user to choose: retry with a
new approach, skip and log as blocked, or escalate. Log the outcome
either way.

## 5. Constraint drift check

At every major subtask boundary (checklist item done, or switching
files/modules), re-read PROJECT.md's Constraints and the plan's Global
Constraints. If the next action would violate one, name the conflict
before proceeding — never drift past it silently.

## 6. Progress surfacing

Every three turns, append to the ledger and state inline:

```text
Progress: <N>/<total> tasks. Budget ~<N>%. Blocked: <none|list>.
```

## 7. Wrap-up protocol

Triggered by hard stop, user request, or all tasks complete. In order,
no skipping or reordering:

1. **Finish the current atomic task only** — never start the next.
2. **Finalize the ledger** — tasks complete/incomplete/blocked, final
   budget estimate, reasons for anything blocked.
3. **Update the plan** in `.constraint-kit/plans/` — check off what is
   actually done; move unfinished tasks to an explicit carry-forward
   note.
4. **Append a session entry to `.constraint-kit/PROJECT.md`** under a
   `## Session log` section (create it at the end of the file if
   missing):

   ```markdown
   ### <YYYY-MM-DD> — <plan/topic>
   - Done: <N> tasks · Carried forward: <N> · Budget: ~<N>%
   - Lessons: <what worked, what failed and why, decisions made>
   ```

   Keep the log distilled: when a lesson hardens into a durable rule,
   move it up into Constraints or Conventions and drop the log entry —
   the log is a buffer, not an archive.
5. **Commit** (file-access surfaces): `git add -A && git commit` with a
   one-line summary; state the hash.
6. **Produce the continuation prompt** — a ready-to-paste block naming
   the plan file, the next task, and any carry-forwards.
7. **State wrap-up complete** and stop.

## Red flags

- Task work before the ledger is initialized
- Reporting an edit successful without reading the file back
- "Test and see if it works" as a substitute for verification
- A third re-attempt without a root-cause diagnosis
- Marking a task complete from your own output rather than verified
  outcome
- Starting a new task past the hard stop
- A wrap-up that says "complete" while blocked items exist unnamed
- A session entry that omits carried-forward tasks
- Silently drifting past a constraint instead of naming the conflict
