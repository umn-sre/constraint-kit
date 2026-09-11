# Discipline Protocol Specification

Date: 2026-09-11
Status: Approved for planning

## Problem Statement

Constraint-kit establishes disciplined behavior within individual phases,
but that discipline is not continuously represented across design,
implementation, unit testing, functional testing, dry runs, recovery, and
resumed sessions. An agent can follow an approved plan, encounter a nearby
issue during testing, make an unplanned fix, and gradually treat the drifted
state as the new plan. Users then have to discard work or manually invoke
brainstorming to reconstruct the lost constraints.

The absence of one durable lifecycle contract makes phase handoffs and
testing detours dependent on conversation memory. It also leaves no
deterministic way to distinguish an expected test failure, a regression, a
necessary blocker, an unrelated finding, and a discovery that invalidates
the approved design.

## Solution

Provide a persistent discipline protocol that remains active from design
through explicit completion, abandonment, or reset. Approved project and
planning documents remain authoritative, while a compact git-ignored active
state records the current phase, approved checkpoint, active task, allowed
scope, required validation, next permitted action, next human gate, parked
detours, named exceptions, and recovery status.

A canonical protocol skill defines the state model, pre-action guard,
detour classifier, exception process, and recovery process. Existing design
and development skills integrate through narrow phase adapters. Before any
action that can mutate state, broaden validation, or advance the workflow,
the agent classifies it against the active checkpoint. Read-only discovery
needed to load and classify state remains available.

The protocol permits autonomous work inside an approved task and reserves
human approval for hard gates. It fails closed for writes when active state
cannot be trusted and preserves verified compliant work when recovering
from drift.

## User Stories

1. As a user, I want discipline to remain active across design,
   implementation, and testing, so that phase changes do not erase the
   working agreement.
2. As a user, I want active discipline to survive chat compaction and
   resumed sessions, so that workflow safety does not depend on conversation
   memory.
3. As a user, I want the agent to state the approved checkpoint and next
   permitted action, so that I can see what currently authorizes the work.
4. As a user, I want exploratory conversation to remain free-form, so that
   brainstorming does not become cumbersome.
5. As a user, I want the agent to stop before exploration becomes an
   unapproved edit or tool action, so that ideas do not silently become
   implementation.
6. As a user, I want normal in-scope TDD cycles to proceed autonomously, so
   that discipline does not require approval for every red-green-refactor
   step.
7. As a user, I want expected failing tests distinguished from defects, so
   that an intentional RED does not trigger unnecessary recovery.
8. As a user, I want regressions caused by current work repaired within the
   active task, so that restoring promised behavior does not require a new
   design cycle.
9. As a user, I want a necessary same-outcome blocker represented as an
   explicit micro-task, so that small enabling fixes remain bounded and
   testable.
10. As a user, I want unrelated findings parked with evidence, so that useful
    discoveries are retained without expanding current scope.
11. As a user, I want findings that invalidate behavior, architecture,
    constraints, scope, or the plan returned to a human gate, so that major
    decisions are not made implicitly during testing.
12. As a user, I want “small,” “nearby,” and “obvious” rejected as permission
    categories, so that subjective convenience cannot bypass scope.
13. As a user, I want direct urgency commands to preserve constraints unless
    I approve a named exception, so that “just fix it” does not silently
    discard the process.
14. As a user, I want an exception request to identify the rule, action,
    consequence, and next checkpoint, so that I can make an informed choice.
15. As a user, I want each named exception limited to one approved action, so
    that it does not become a standing waiver.
16. As a user, I want exceptions recorded in durable state, so that resumed
    sessions can distinguish authorized deviation from drift.
17. As a user, I want the protocol to detect drift before writes whenever
    possible, so that recovery is exceptional rather than routine.
18. As a user, I want suspected drift to freeze new edits, so that the
    affected change set does not continue growing during diagnosis.
19. As a user, I want drifted changes classified against the last approved
    checkpoint, so that recovery decisions have a stable basis.
20. As a user, I want compliant and currently validated work retained during
    recovery, so that regaining discipline does not require needless rework.
21. As a user, I want desired but unapproved work routed back through its
    missing gate, so that it can be reconsidered without being smuggled into
    the active task.
22. As a user, I want violating changes proposed for reversal, so that the
    workspace can return to its approved state.
23. As a user, I want destructive recovery to require approval, so that the
    agent cannot erase my unrelated or uncommitted work.
24. As a user, I want ambiguous evidence treated as unapproved, so that the
    mere existence of code cannot retroactively prove authorization.
25. As a user, I want missing, malformed, or contradictory active state to
    fail closed for writes, so that corrupted process state cannot authorize
    changes.
26. As a user, I want read-only diagnosis available when state is invalid, so
    that the agent can explain and repair the protocol without making the
    workspace less trustworthy.
27. As a user, I want completion, abandonment, and reset recorded explicitly,
    so that active discipline never expires silently.
28. As a planner, I want brainstorming to initialize the protocol and record
    approvals, so that downstream phases inherit a known checkpoint.
29. As a planner, I want specifications and plans to advance only from an
    approved predecessor, so that later documents cannot manufacture earlier
    approval retroactively.
30. As an implementer, I want one canonical action classifier, so that I do
    not have to reconcile different drift rules in every development skill.
31. As a conductor, I want dispatched work tied to the same active checkpoint,
    so that subagents cannot independently broaden scope.
32. As a reviewer, I want deviations associated with a checkpoint, parked
    detour, or named exception, so that authorized and unauthorized changes
    can be distinguished.
33. As a skill maintainer, I want phase skills to contain narrow adapters
    rather than copies of the state machine, so that enforcement rules do not
    diverge.
34. As a skill maintainer, I want lifecycle state separate from attempts,
    review rounds, edit verification, and budget, so that the discipline and
    session ledgers have clear ownership.
35. As a skill maintainer, I want scenario-based behavioral acceptance, so
    that the protocol is reviewed through observable decisions rather than
    prose similarity.
36. As a skill maintainer, I want repository structural validation to cover
    the new skill and references, so that packaging errors are caught before
    release.
37. As an existing consumer, I want adoption to begin only when an updated
    workflow initializes active state, so that a plugin update does not
    unexpectedly rewrite my repository.

## Implementation Decisions

- Add one canonical `discipline-protocol` skill to the design plugin.
- Define four protocol states: `ACTIVE`, `RECOVERY`, `CLOSED`, and
  `ABANDONED`.
- Store active state in a git-ignored discipline ledger in the consuming
  repository.
- Keep project context and approved design, specification, and plan artifacts
  authoritative. The active ledger references them and does not copy their
  full contents.
- Record current phase, active task, approved checkpoint, authority
  references, allowed scope, validation requirements, next action, next
  gate, parked detours, named exceptions, and recovery rulings in active
  state.
- Require explicit recorded completion, abandonment, or reset. Do not infer
  expiration from chat termination, phase changes, inactivity, or missing
  conversational context.
- Add narrow protocol adapters to brainstorming, specification writing,
  plan writing, plan execution, subagent-driven execution, TDD, and session
  ledger workflows.
- Make brainstorming responsible for initialization and design approval
  checkpoints.
- Permit specification and plan transitions only when the required approved
  predecessor is referenced by active state.
- Add one compact generated project instruction requiring agents to read an
  active discipline ledger and its referenced authority before actionable
  work.
- Define the pre-action guard at the boundary of workspace or external-state
  mutation, validation-scope expansion, and workflow advancement.
- Allow read-only discovery before the guard when needed to find, load, or
  classify protocol state.
- Use these exhaustive action classifications: approved in-scope work,
  expected TDD RED, current-work regression, necessary same-outcome blocker,
  unrelated finding, behavior/architecture/constraint/scope change,
  constraint conflict, and unclassifiable action.
- Treat an unclassifiable action as unapproved.
- Permit expected RED, in-scope work, regression repair, focused validation,
  and normal approved task transitions without human approval.
- Require human approval for design, specification and plan handoffs, scope
  or constraint changes, named exceptions, destructive recovery, and final
  closure, abandonment, or reset.
- Represent a same-outcome blocker as a bounded micro-task with focused
  validation and TDD when it changes behavior.
- Park unrelated findings without editing for them or broadening tests to
  investigate them during the active task.
- Route findings that invalidate an approved decision back to the
  corresponding design or planning gate.
- Require named exceptions to identify one rule, one action, its consequence,
  and the next checkpoint. An exception does not amend the underlying rule.
- Enter `RECOVERY` and freeze edits when post-change drift is suspected.
- Classify recovery changes as compliant, recoverable, or violating against
  the last approved checkpoint.
- Retain compliant work only with current required validation evidence.
- Route recoverable work through its missing gate and require approval before
  destructive reversal of violating work.
- Never reverse unrelated user changes as part of protocol recovery.
- Fail closed for writes when active state is missing but an unresolved
  workflow is indicated, malformed, contradictory, or references missing
  authority.
- Keep the discipline ledger responsible for lifecycle state and the session
  or SDD ledger responsible for attempts, edit verification, review rounds,
  task progress, and budget.
- Do not add a supervisor agent or merge existing ledgers.
- Update plugin metadata and documentation to expose the new capability and
  its cross-plugin integration.
- Extend structural validation only as needed to verify the new skill and its
  references.

## Testing Decisions

- Test at the consumer-observable workflow-decision seam. Given authoritative
  artifacts, active state, and a proposed action, each scenario must produce
  one expected classification, allowed action, forbidden action, human gate,
  and resulting state.
- Do not test internal prose wording or duplicate tests for each repeated
  adapter sentence. Test that each adapter agrees with the canonical
  decision for the scenarios it can encounter.
- Maintain a scenario matrix covering at least:
  - approved design-to-specification handoff;
  - resumed session;
  - expected RED;
  - regression caused by current work;
  - dry-run blocker;
  - unrelated miscellaneous issue;
  - scope-changing discovery;
  - direct “just fix it” instruction without a named exception;
  - approved named exception;
  - drift discovered after edits;
  - missing or malformed active state; and
  - explicit close or reset.
- For each scenario, record starting state, proposed action, expected
  classification, allowed action, forbidden action, required gate, resulting
  state, and recovery outcome.
- Use the existing repository validator as the structural seam for manifests,
  skill frontmatter, marketplace consistency, and relative references.
- Add focused validator coverage only when the new structure introduces a
  structural contract not already checked.
- Require the complete repository validator to pass after implementation.

## Out of Scope

- Building an executable state-machine engine or workflow service.
- Adding a supervisor agent or replacing planner, conductor, implementer, or
  reviewer responsibilities.
- Automatically modifying existing consuming repositories on plugin update.
- Merging the discipline ledger with session or SDD ledgers.
- Requiring human confirmation for every test cycle, edit, or compliant task
  transition.
- Redesigning unrelated skills or repository documentation.
- Treating the protocol as enforcement outside agents that have loaded the
  relevant plugin instructions.

## Further Notes

The central behavioral distinction is between free exploration and
actionable work. Conversation may explore alternatives, but mutation,
validation expansion, and workflow advancement require authorization from
the active checkpoint.

The protocol should use the glossary terms consistently. “Small,” “nearby,”
and “obvious” are deliberately not domain classifications because they do
not establish whether work is authorized.

Adoption is incremental. Updated intake or a newly started constrained
workflow initializes active state in a consuming repository; existing
repositories remain unchanged until that occurs.