---
name: discipline-protocol
description: Use when a constraint-kit workflow starts, resumes, crosses a phase, encounters a testing detour, requests a constraint exception, or recovers from drift - persists the approved checkpoint and constrains which action may happen next.
---

# Discipline Protocol

Keep one behavioral contract active from design through explicit completion,
abandonment, or reset. Approved project and planning documents are the
authority; this skill records which authority is active and guards the next
action.

## Active State

Use `.constraint-kit/discipline.md` as git-ignored active state. Record:
status (`ACTIVE`, `RECOVERY`, `CLOSED`, or `ABANDONED`), phase, active task,
approved checkpoint, authority links, allowed scope, required validation,
next permitted action, next human gate, parked detours, named exceptions,
and recovery rulings. Authority stays in `docs/PROJECT.md` and approved
design, specification, and plan artifacts.

Before creating the ledger, run
`git check-ignore -q .constraint-kit/discipline.md`. If it is not ignored,
append the exact root rule `/.constraint-kit/discipline.md` to `.gitignore`
without changing existing entries, then rerun the check. If the ignore rule
cannot be established, fail closed and do not create the ledger.

Create or update the file with this shape:

```markdown
# Discipline — <topic>

- Status: ACTIVE | RECOVERY | CLOSED | ABANDONED
- Phase: <design | specification | planning | implementation | validation | finishing>
- Active task: <task or none>
- Approved checkpoint: <description>
- Authority: <paths to authoritative artifacts>
- Allowed scope: <bounded outcome>
- Required validation: <commands or observable checks>
- Next permitted action: <one action>
- Next human gate: <gate or none>

## Parked Detours

- <finding and evidence, or none>

## Named Exceptions

- <rule, action, consequence, approval, or none>

## Recovery Rulings

- <change, classification, disposition, or none>
```

Do not infer inactivity from a missing ledger when project instructions or
authoritative artifacts show unresolved constrained work. Missing,
malformed, contradictory, or dangling active state fails closed for writes;
read-only diagnosis remains allowed.

## Pre-action Guard

Before mutation, validation-scope expansion, or workflow advancement, read
active state and its authority and classify the proposed action. Read-only
discovery needed to locate, load, or classify state is allowed first.
Unclassifiable work is unapproved. Do not act until its gate is resolved.

Exploratory conversation may range beyond active scope. Apply the guard when
an idea would cause a tool action, edit, broader test, plan change, or phase
transition.

## Action Classifications

Use exactly one classification:

- **Approved in-scope work** — proceed with required validation.
- **Expected TDD RED** — continue the approved TDD cycle.
- **Current-work regression** — repair within the active task and rerun the
  focused check.
- **Necessary same-outcome blocker** — record a bounded micro-task, use TDD
  for behavior changes, validate it, and return to the active task.
- **Unrelated finding** — park it with evidence; do not edit or broaden
  testing for it.
- **Behavior, architecture, constraint, or scope change** — freeze and return
  to the corresponding human gate.
- **Constraint conflict** — state the conflict and request a named exception.
- **Unclassifiable action** — stop before writes and restore trustworthy
  state or obtain the missing decision.

“Small,” “nearby,” and “obvious” are not classifications and do not authorize
work. Use the [scenario matrix](SCENARIOS.md) as the behavioral reference.

## Human Gates

Require approval for design, specification and plan handoffs, scope or
constraint changes, named exceptions, destructive recovery, and final
closure, abandonment, or reset. Ordinary in-scope TDD and focused validation
proceed autonomously.

A later artifact cannot retroactively manufacture approval for an earlier
gate. Record each approved transition before advancing.

## Named Exceptions

State one violated rule, one requested action, its consequence, and the next
checkpoint. Proceed only after explicit approval of that named exception.
Record it; never treat it as a standing waiver or amendment to the project
constraint.

## Drift Recovery

Freeze edits and enter `RECOVERY`. Compare changes with the last approved
checkpoint; classify each as compliant, recoverable, or violating. Keep only
validated compliant work, route recoverable work through its missing gate,
and request approval before destructive reversal. Never erase unrelated user
work. Ambiguous evidence is unapproved.

Leave `RECOVERY` only after every affected change has a ruling and a new
approved checkpoint identifies the next permitted action.

## Close, Abandon, or Reset

Never expire silently. Record `CLOSED` or `ABANDONED` before replacing active
state. Reset requires explicit approval and a terminal record for the prior
workflow.

Closing records the final validation evidence. Abandoning records what was
retained, reverted, or left parked. Neither action deletes authoritative
artifacts.

## Red Flags

- Acting from chat memory without reading active state and its authority
- Treating a direct command as an implicit constraint override
- Fixing a testing discovery before classifying it
- Calling work in scope because it is small, nearby, or obvious
- Continuing edits while drift is under investigation
- Treating existing code as evidence that it was approved
- Silently replacing or deleting active state
- Creating active state before confirming its ignore rule