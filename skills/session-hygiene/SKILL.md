# Skill: Session Hygiene

## Purpose

Maintain session integrity from first turn to last. Govern the
agent's runtime behavior within an implementation session: track
progress against the session plan, detect and surface loops before
they consume context, monitor token budget, verify file changes
were actually applied, and execute a clean wrap-up that leaves the
project in a known state for the next session.

## When This Skill Is Active

Every implementation session that was started with a preflight
artifact (`agent-implementer.yaml`). Apply from the first response
turn through session close. This skill is always paired with the
active `agent-implementer.yaml` for the session.

## Agent Behavior

### 1. Session Open

- On the first turn, read and acknowledge the active
  `agent-implementer.yaml`. State:
  - Session ID and title
  - Task count and task list (checkbox format)
  - Done condition
  - Surface in use and its key constraints
    (file_system_access, budget thresholds, known_failure_modes)
- Initialize the session ledger as a running markdown block
  maintained in the conversation or as a file if file system
  access is available. Ledger format:

  ```
  ## Session Ledger — <SESSION_ID>
  ### Tasks
  - [ ] <task 1>
  - [ ] <task 2>
  ### Files Touched
  | file | action | verified |
  |------|--------|----------|
  ### Attempts Log
  | turn | file/operation | outcome |
  |------|---------------|---------|
  ### Budget
  estimated_consumed: 0%
  budget_warning_threshold: <from surface profile: context.budget_warning_threshold>
  budget_hard_stop: <from surface profile: context.budget_hard_stop>
  ```

- Do not begin task work until the ledger is initialized.

### 2. Per-Turn Discipline

At the start of every response turn, before producing any output:

- Check the attempts log for the current operation. If this
  operation (same file + same intent) appears in the log:
  **halt. Do not attempt again.** State: "I have already attempted
  this. Previous outcome: <outcome>. Diagnosing before proceeding."
  Provide a root cause hypothesis before asking the user how to
  continue.
- Update the budget estimate. Use approximate token counts:
  each 1000 words ≈ 750 tokens. Sum inputs + outputs accumulated
  so far. Express as a percentage of the surface's `usable_estimate`.
- If budget estimate exceeds `budget_warning_threshold`: prepend
  a one-line warning to the response. Continue working.
- If budget estimate exceeds `budget_hard_stop`: do not begin a
  new task. Execute wrap-up protocol (see §5) immediately.

### 3. File Verification (file-access surfaces only)

Applies when surface profile has `file_system_access: true`.

After every file write or edit:

- Read the file back immediately.
- Confirm the change is present by checking either:
  - Line count changed (for additions/deletions)
  - Target string is present (for replacements)
  - `git diff --stat` shows non-zero delta (preferred when git
    is available)
- If verification fails (file unchanged, -0/+0 diff, target
  string absent):
  - Do not report success.
  - Do not ask the user to test or rerun.
  - Log the failure in the attempts log with outcome: PHANTOM.
  - State: "Edit did not apply. Diagnosing." Provide a root cause
    hypothesis (wrong path, permissions, encoding, stale buffer)
    before re-attempting.
  - Maximum two re-attempts per edit. On second failure: halt,
    escalate to user with full diagnosis.

For browser-chat surfaces (`file_system_access: false`):

- After every code block or proposed change, explicitly state:
  "This is a proposed change only. I cannot verify it was applied.
  Please confirm the change is in place before I continue."
- Do not mark the task complete until the user confirms.

### 4. Loop Detection

A loop is defined as: the same file AND the same intent appearing
two or more times in the attempts log without a successful outcome
between them.

On loop detection:
- Halt immediately. Do not produce more output for that operation.
- State: "Loop detected — I have attempted <operation> on <file>
  <N> times without a verified successful outcome."
- Provide a structured diagnosis:
  1. What was attempted
  2. What the expected outcome was
  3. What actually happened each time
  4. Hypothesis for why it is failing
- Ask the user to choose: retry with a new approach, skip and
  log as blocked, or escalate.
- Log the outcome in the attempts log regardless of choice.

### 5. Constraint Drift Check

At the boundary of every major subtask (defined as: completing
a checklist item or switching files/modules):

- Re-read the `skills:` and key constraints sections of the active
  `agent-implementer.yaml`.
- Confirm the next action complies. If a constraint would be
  violated, state the conflict explicitly before proceeding.
- Do not silently proceed past a constraint violation on the
  assumption the user will catch it.

### 6. Progress Surfacing

Every three response turns, append a brief progress summary to
the session ledger and state it inline:

```

Progress: <N>/<total> tasks complete. Budget ~<N>%. Blocked: <none|list>.

```

This gives the user a low-cost orientation point without requiring
them to read the full thread.

### 7. Wrap-Up Protocol

Triggered by: budget hard stop reached, user requests close,
or all tasks complete.

Execute in this order — do not skip steps, do not reorder:

1. **Complete current atomic task only.** If mid-task, finish the
   current indivisible unit of work. Do not start the next task.

2. **Finalize session ledger.** Mark tasks complete/incomplete/blocked.
   Record final budget estimate. Note any blocked items with
   reason.

3. **Update `SESSION_PLAN.md`.** Mark the current session row with
   status: `complete`, `partial`, or `blocked`. Update task
   checkboxes to reflect actual completion state. If tasks were
   not completed, move them to a carry-forward note in the next
   session entry.

4. **Append session history to `agent-base.yaml`.**
   Add an entry to the `session_history:` list:

   ```yaml
   - session_id: <ID>
     date: <YYYY-MM-DD>
     surface: <surface id>
     tasks_completed: <N>
     tasks_carried_forward: <N>
     budget_consumed_estimate: <N>%
     notes: >
       <one paragraph: what was accomplished, what was not,
       any decisions made or constraints established>
   ```

   Write this directly to the file if file system access is
   available. If not, produce the YAML block and instruct the
   user to append it manually.

5. **Commit if on a file-access surface.** Run:
   `git add -A && git commit -m "<SESSION_ID>: <one-line summary>"`
   State the commit hash.

6. **Produce the continuation prompt.** Output a ready-to-paste
   block for the next session:

   ```
   Continuing <PROJECT_NAME> — session <NEXT_SESSION_ID>.
   Active plan: SESSION_PLAN.md.
   Paste the <NEXT_SESSION_ID> agent-implementer.yaml block from
   SESSION_PLAN.md as your first message to begin.
   ```

7. **State wrap-up complete.** Do not produce further output
   after this point.

## Anti-Patterns

- Beginning task work before the session ledger is initialized.
- Reporting a file edit as successful without reading the file back
  (on file-access surfaces).
- Asking the user to "test and see if it works" as a substitute
  for verifying the edit was applied.
- Retrying a failed operation more than twice without diagnosing
  root cause.
- Marking a task complete based on the agent's own output rather
  than on verified outcome.
- Starting a new task after the hard stop threshold is reached.
- Skipping or reordering wrap-up steps.
- Appending a session history entry that omits tasks carried forward.
- Producing a wrap-up that says "session complete" when blocked
  items exist without naming them.
- Silently drifting past a constraint — if a constraint is being
  violated, name it before proceeding or ask for an exception.

## Transition

Do not begin task work until the session ledger is initialized.
Do not mark any task complete without verified outcome (file-access
surfaces) or explicit user confirmation (browser surfaces).
Do not begin a new task after the hard stop threshold is reached —
execute wrap-up instead. Do not close the session without completing
all seven wrap-up steps in order.
