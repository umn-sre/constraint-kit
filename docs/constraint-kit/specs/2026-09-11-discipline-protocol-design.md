# Discipline Protocol Design

Date: 2026-09-11
Status: Approved design

## Purpose

Constraint-kit's phase-specific disciplines are strong, but discipline can
be lost between phases or inside testing detours. A session can move from
approved implementation into an unplanned fix during unit testing or a dry
run, then continue from the changed state without an explicit scope or
design decision.

The discipline protocol is a persistent behavioral contract spanning
design, specification, planning, implementation, testing, detours, recovery,
and closure. It allows exploratory conversation, but prevents conversation
from becoming an unapproved action.

## Goals

- Keep the approved constraints, scope, checkpoint, and next gate visible
  across skills, agents, compaction, and resumed sessions.
- Interrupt drift before an unapproved tool action, edit, test of new scope,
  or plan change occurs.
- Route issues discovered during testing without casually absorbing them
  into the active task.
- Recover selectively from drift without automatically discarding compliant,
  verified work or legitimizing work merely because it already exists.
- Make exceptions explicit, specific, consequential, and auditable.
- Preserve the existing responsibilities of the planner, conductor,
  implementer, phase skills, and session ledger.

## Non-goals

- Executable workflow orchestration or a new workflow engine.
- A supervisor agent that replaces the existing agent boundaries.
- Automatic modification of consuming repositories during plugin install.
- Human approval for every normal TDD cycle or in-scope task transition.
- Duplication of full designs, specs, plans, attempts, or review history in
  the active-state file.

## Terms

**Discipline protocol** -- The cross-lifecycle contract that constrains
which action may happen next and which gate must be satisfied before the
workflow advances.

**Approved checkpoint** -- The latest human-approved lifecycle state and
authoritative artifact against which proposed actions and existing changes
are evaluated.

**Detour** -- Work discovered while executing an approved task that is not
already represented by the task's expected behavior and validation.

**Named exception** -- Explicit human approval to violate one identified
constraint for one stated action after the agent states the consequence.

**Drift** -- An action or existing change that cannot be justified by the
active approved scope, task, transition, or named exception.

## Architecture

The protocol has three layers.

### Durable authority

`docs/PROJECT.md` and approved design, specification, and plan artifacts
remain authoritative for project constraints, scope, decisions, testing
seams, and done conditions. The protocol never replaces these documents.

### Active state

A consuming repository stores active lifecycle state in the git-ignored
`.constraint-kit/discipline.md` file. It contains pointers to authoritative
artifacts rather than copies of their content.

The file records:

- protocol status: `ACTIVE`, `RECOVERY`, `CLOSED`, or `ABANDONED`;
- current phase and active task;
- approved checkpoint and referenced authoritative artifacts;
- allowed scope and required validation;
- next permitted action and next human gate;
- parked detours;
- named exceptions and their consequences;
- recovery classification and unresolved decisions, when applicable.

The active state never expires silently. Completion, abandonment, and reset
are explicit recorded transitions. A reset closes or abandons the prior
state before a replacement is initialized.

### Phase adapters

Existing skills retain their specialized responsibilities and interact with
the protocol at their boundaries:

- `brainstorming` initializes active state and records design approvals;
- `writing-specs` and `writing-plans` advance state only from approved
  predecessor artifacts;
- execution and TDD skills check the action guard and record task/gate
  progress;
- testing follows the detour classifier before changing scope;
- `session-ledger` records operational evidence and references the active
  discipline checkpoint.

The discipline ledger owns lifecycle state. The existing session or SDD
ledger owns attempts, edit verification, review rounds, progress, and
budget. Neither ledger duplicates the other's details.

Generated `.github/copilot-instructions.md` files include a compact
invariant: when an active discipline ledger exists, read it and its
referenced authority before taking action.

## Canonical Component

Add a `discipline-protocol` skill to the `constraint-design` plugin. It is
the canonical definition of:

- the active-state schema;
- lifecycle states and permitted transitions;
- the pre-action guard;
- detour classification;
- named exceptions;
- drift recovery; and
- explicit closure, abandonment, and reset.

Other skills contain short adapter rules and cross-reference this canonical
skill. They do not reproduce its state machine.

The integration surface is:

- `constraint-design`: `brainstorming`, `writing-specs`, `writing-plans`,
  and `project-intake`;
- `constraint-dev`: `executing-plans`, `subagent-driven-development`,
  `test-driven-development`, and `session-ledger`;
- relevant planner, conductor, and implementer instructions only where the
  existing skill invocation rules do not already load the protocol;
- plugin manifests and READMEs; and
- structural validation for new skill and cross-plugin references.

No new agent is introduced, and the existing ledgers are not merged.

## Pre-action Guard

Before every action that can mutate workspace or external state, broaden
validation scope, or advance the workflow, the acting skill or agent reads
the active state and classifies the proposed action. Read-only discovery
needed to locate, load, or classify the protocol state is allowed first.

| Classification | Required behavior |
|---|---|
| Approved in-scope work | Proceed autonomously and preserve required validation. |
| Expected TDD RED | Continue the approved TDD cycle. |
| Regression caused by current work | Repair within the active task and rerun the focused check. |
| Necessary same-outcome blocker | Add an explicit micro-task, use TDD where behavior changes, then return to the active task. |
| Unrelated finding | Park it with evidence; do not edit or broaden testing for it. |
| Behavior, architecture, constraint, or scope change | Stop at a human gate and return to the appropriate design or planning phase. |
| Constraint conflict | Name the rule and consequence; proceed only with a named exception. |
| Unclassifiable action | Treat as unapproved and stop before writes. |

Exploratory conversation may range beyond the active scope. It becomes
subject to the guard when it would cause a tool action, edit, test of new
scope, plan change, or workflow transition.

A later-phase artifact cannot retroactively manufacture approval for an
earlier gate. Each transition requires its approved predecessor.

## Human Gates

Explicit human approval is required for:

- design approval;
- specification and plan handoffs;
- behavior, architecture, constraint, or scope changes;
- named exceptions;
- destructive recovery actions; and
- final closure, abandonment, or reset.

Compliant actions inside an approved task, including ordinary RED-GREEN-
REFACTOR cycles and focused validation, proceed autonomously.

## Testing Detours

When a unit test, functional test, or dry run reveals an issue, the agent
classifies the finding before editing:

1. If the finding is an expected failure proving the active behavior is
   absent, continue the current TDD cycle.
2. If current changes caused a regression against previously passing
   behavior, repair it in the active task.
3. If the active outcome cannot be validated without a small same-outcome
   fix, record an explicit micro-task and its focused validation.
4. If the issue is unrelated to the approved outcome, park it and return to
   the active task.
5. If the issue invalidates approved behavior, architecture, constraints,
   scope, or the plan, freeze implementation and return to the corresponding
   human gate.

“Nearby,” “small,” and “obvious” are not classifications and do not grant
permission to make a fix.

## Named Exceptions

A direct instruction such as “just fix it” does not implicitly override the
protocol. To request an exception, the agent states:

- the exact constraint that would be violated;
- the single action for which the exception is requested;
- the expected consequence, including lost evidence or increased risk; and
- the next checkpoint after the action.

Only explicit approval of that identified exception permits the action. The
active ledger records the request, approval, action, and consequence. An
exception does not amend the underlying project constraint or authorize
later similar actions.

## Drift Recovery

When drift is suspected after changes exist:

1. Freeze new edits and transition to `RECOVERY`.
2. Identify the last approved checkpoint and inventory changes since it.
3. Classify each change as:
   - **compliant** -- authorized by the checkpoint and backed by required
     validation;
   - **recoverable** -- desired but missing the required gate or task; or
   - **violating** -- conflicts with an active constraint or rejected scope.
4. Retain compliant work only when its validation evidence is current.
5. Remove recoverable work from the active task and route it through its
   required design, planning, or TDD gate.
6. Propose reversal of violating work. Destructive reversal requires
   explicit approval and must not erase unrelated user changes.
7. Re-establish an approved checkpoint and leave `RECOVERY` only after all
   affected changes have a ruling.

Ambiguous evidence is treated as unapproved. Existing code is not evidence
of approval.

## Protocol Failures

If an active ledger is missing, malformed, contradictory, or points to a
missing authoritative artifact, writes fail closed. Read-only diagnosis is
allowed. The agent reports:

- the violated or unverifiable constraint;
- the last trustworthy checkpoint;
- the affected proposed action or existing changes; and
- one next decision needed to restore valid state.

A missing ledger is not itself proof that no protocol is active. The agent
also checks referenced planning artifacts and generated project
instructions for an unresolved active workflow.

## Acceptance

Behavioral acceptance uses a scenario matrix. Each scenario records the
starting state, proposed action, expected classification, allowed action,
forbidden action, required gate, resulting state, and recovery outcome.

Required scenarios are:

| Scenario | Essential expectation |
|---|---|
| Approved design to specification | Transition only after design approval. |
| Resumed session | Reconstruct the next action from durable state, not chat memory. |
| Expected RED | Continue TDD without a new human gate. |
| Regression from current work | Repair in-task and rerun focused validation. |
| Dry-run blocker | Create an explicit same-outcome micro-task. |
| Unrelated miscellaneous issue | Park without editing or widening tests. |
| Scope-changing finding | Freeze and return to the appropriate human gate. |
| “Just fix it” | Refuse implicit override and identify the conflict. |
| Approved named exception | Record and execute only the approved action. |
| Drift discovered after edits | Enter recovery and classify every affected change. |
| Missing or malformed active ledger | Allow diagnosis but fail closed for writes. |
| Explicit close or reset | Record terminal state before replacing active state. |

Review the scenario matrix against every phase adapter so no adapter permits
an action the canonical protocol forbids. Run `python3 scripts/validate.py`
after structural changes and fix every reported issue.

## Rollout Boundaries

Implementation changes only skills, agent instructions where required,
plugin metadata, documentation, scenario fixtures, and structural validator
coverage. It does not create executable orchestration, automatically edit
consumer repositories, or redesign unrelated constraint-kit workflows.

Existing consuming repositories adopt the protocol when an updated intake
or active constraint-kit workflow initializes the discipline ledger. Until
then, their existing project instructions and artifacts remain unchanged.