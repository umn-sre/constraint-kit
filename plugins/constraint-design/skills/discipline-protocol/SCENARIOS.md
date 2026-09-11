# Discipline Protocol Scenario Matrix

These scenarios define the consumer-observable decision seam. Phase adapters
must preserve the classification, allowed and forbidden actions, human gate,
resulting state, and recovery outcome.

| ID | Starting state | Proposed action | Classification | Allowed | Forbidden | Human gate | Resulting state | Recovery outcome |
|---|---|---|---|---|---|---|---|---|
| design-to-spec | Approved design | Write specification | Approved in-scope work | Synthesize specification | Implement | Approve specification handoff | ACTIVE/specification | None |
| resumed-session | ACTIVE with authority links | Resume next action | Approved in-scope work | Reload authority and continue | Infer state from chat | None | Unchanged | None |
| expected-red | ACTIVE implementation task | Run expected failing test | Expected TDD RED | Continue TDD | Enter recovery | None | Unchanged | None |
| current-work-regression | ACTIVE implementation task | Repair caused regression | Current-work regression | Repair and rerun focused check | Broaden scope | None | Unchanged | Current task restored and revalidated |
| dry-run-blocker | ACTIVE validation | Fix required same-outcome blocker | Necessary same-outcome blocker | Record micro-task and test | Casual adjacent fix | None | Unchanged | Validated micro-task returns to active task |
| unrelated-finding | ACTIVE task | Fix unrelated issue | Unrelated finding | Park evidence | Edit or widen tests | None | Unchanged | Finding remains parked for later triage |
| scope-changing-finding | ACTIVE task | Change approved behavior | Behavior, architecture, constraint, or scope change | Freeze and return to gate | Implement new behavior | Scope approval | ACTIVE/design or planning | Resume only from a newly approved checkpoint |
| implicit-override | ACTIVE task | “Just fix it” against a rule | Constraint conflict | Name exception request | Treat command as waiver | Named-exception approval | Unchanged | No action until the exception is approved or rejected |
| named-exception | ACTIVE with approved exception | Perform named action | Approved in-scope work | Execute only named action | Generalize waiver | None | Unchanged | Record consequence and continue from named checkpoint |
| post-edit-drift | ACTIVE with unapproved changes | Continue editing | Unclassifiable action | Freeze and classify changes | Add more changes | Recovery rulings | RECOVERY | Rule every affected change before resuming |
| invalid-ledger | Missing or invalid active state | Mutating action | Unclassifiable action | Read-only diagnosis | Write | Restore state | RECOVERY | Restore trustworthy state before writes |
| explicit-close-reset | ACTIVE completed or abandoned work | Replace active state | Approved in-scope work | Record terminal state | Silent replacement | Close/reset approval | CLOSED or ABANDONED | Retain terminal record before replacement |