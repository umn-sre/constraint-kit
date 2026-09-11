# Discipline Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> subagent-driven-development (recommended) or executing-plans (both in
> the constraint-dev plugin) to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a persistent discipline protocol that prevents unapproved
actions across design, implementation, testing, recovery, and resumed
sessions.

**Architecture:** A canonical `discipline-protocol` skill owns the lifecycle
state model, action classifier, detour routing, named exceptions, and
recovery behavior. Existing phase skills are thin adapters to that contract;
the repository validator checks the canonical contract, scenario matrix,
adapter references, and persistence hook.

**Tech Stack:** Markdown skills and agents, JSON plugin manifests, Python
3.12 standard library validation, GitHub Actions.

## Global Constraints

- Approved project, design, specification, and plan documents remain the
  durable authority; the active ledger points to them rather than copying
  them.
- Protocol states are exactly `ACTIVE`, `RECOVERY`, `CLOSED`, and
  `ABANDONED`.
- Active state never expires silently; completion, abandonment, and reset
  are explicit recorded transitions.
- Before workspace or external-state mutation, validation-scope expansion,
  or workflow advancement, classify the action against active state.
- Read-only discovery needed to locate, load, or classify state is allowed
  before the action guard.
- Human approval is required only for design approval, specification and
  plan handoffs, scope or constraint changes, named exceptions, destructive
  recovery, and final closure, abandonment, or reset.
- “Small,” “nearby,” and “obvious” never authorize a detour.
- A direct instruction does not override a constraint without a named
  exception identifying one rule, one action, its consequence, and the next
  checkpoint.
- Ambiguous evidence is unapproved; invalid protocol state fails closed for
  writes while allowing read-only diagnosis.
- The discipline ledger owns lifecycle state; session and SDD ledgers own
  attempts, edit verification, review rounds, progress, and budget.
- Do not add a supervisor agent, merge ledgers, build executable workflow
  orchestration, or modify consuming repositories automatically.
- Cross-plugin references use the plain skill name and identify the plugin
  that provides it.
- Test observable workflow decisions, not internal prose wording.
- Run `python3 scripts/validate.py` after every structural change and fix
  every reported problem.

## Module Design

### Module: Protocol Contract

**Interface:** The `discipline-protocol` skill accepts the consuming
repository's authoritative documents, active discipline state, and proposed
action. It yields one action classification, the allowed and forbidden
behavior, any required human gate, and the resulting protocol state.

**Depth:** The caller learns one guard and one state record while the skill
hides lifecycle transitions, detour routing, exception handling, and drift
recovery.

### Module: Protocol Contract Validator

**Interface:** `python3 scripts/validate.py` takes no arguments and returns
zero only when the canonical protocol, required scenario identifiers,
phase-adapter references, and generated-instruction hook are present along
with the existing marketplace structure.

**Depth:** One command validates both generic plugin packaging and the
load-bearing discipline integration points.

### Module: Design Lifecycle Adapter

**Interface:** The existing brainstorming, specification, and planning
skills initialize or advance the protocol only at approved gates. They call
the canonical skill by name and do not restate its state machine.

### Module: Development Lifecycle Adapter

**Interface:** Existing execution, TDD, and session-ledger skills call the
canonical skill from the constraint-design plugin before actionable work
and at testing detours or recovery boundaries. Their existing execution and
operational bookkeeping behavior remains unchanged.

### Module: Persistence and Discovery

**Interface:** Project intake emits one imperative repository instruction
that loads active discipline state before actionable work. Plugin and root
documentation expose the protocol without changing installation mechanics.

## Test Seams

The primary seam is a consumer-observable workflow decision: starting
authority plus active state plus proposed action must produce one
classification, allowed action, forbidden action, gate, and resulting state.
The structural seam is the existing validator command. Phase adapters are
tested by requiring their canonical skill reference, not by asserting their
full prose.

---

### Task 1: Canonical Protocol Contract

**Files:**
- Modify: `scripts/validate.py:13-104`
- Create: `plugins/constraint-design/skills/discipline-protocol/SKILL.md`
- Create: `plugins/constraint-design/skills/discipline-protocol/SCENARIOS.md`

**Interfaces:**
- Consumes: authoritative project/planning artifacts, optional
  `.constraint-kit/discipline.md`, and a proposed action.
- Produces: one action classification, gate decision, resulting state, and
  the canonical active-ledger schema used by every later adapter.

- [x] **Step 1: Add the failing canonical-contract check**

Add these constants and helper near the top of `scripts/validate.py`:

```python
DISCIPLINE_SKILL = (
    ROOT
    / "plugins"
    / "constraint-design"
    / "skills"
    / "discipline-protocol"
    / "SKILL.md"
)
DISCIPLINE_SCENARIOS = DISCIPLINE_SKILL.with_name("SCENARIOS.md")

REQUIRED_DISCIPLINE_HEADINGS = (
    "## Active State",
    "## Pre-action Guard",
    "## Action Classifications",
    "## Human Gates",
    "## Named Exceptions",
    "## Drift Recovery",
    "## Close, Abandon, or Reset",
)

REQUIRED_SCENARIOS = (
    "design-to-spec",
    "resumed-session",
    "expected-red",
    "current-work-regression",
    "dry-run-blocker",
    "unrelated-finding",
    "scope-changing-finding",
    "implicit-override",
    "named-exception",
    "post-edit-drift",
    "invalid-ledger",
    "explicit-close-reset",
)


def require_text(path: Path, required: tuple[str, ...]) -> None:
    if not path.is_file():
        err(f"{path}: missing required discipline contract file")
        return
    text = path.read_text(encoding="utf-8")
    for value in required:
        if value not in text:
            err(f"{path}: missing required discipline contract text: {value}")


def check_discipline_protocol() -> None:
    require_text(DISCIPLINE_SKILL, REQUIRED_DISCIPLINE_HEADINGS)
    require_text(DISCIPLINE_SCENARIOS, REQUIRED_SCENARIOS)
```

Call `check_discipline_protocol()` in `main()` after
`check_marketplace()`.

- [x] **Step 2: Run the validator to verify RED**

Run: `python3 scripts/validate.py`

Expected: FAIL reports both missing discipline contract files.

- [x] **Step 3: Create the canonical skill**

Create `SKILL.md` with frontmatter that triggers whenever a
constraint-kit workflow starts, resumes, crosses a phase, encounters a
testing detour, requests an exception, or recovers from drift. Its body must
contain these exact sections and rules:

```markdown
## Active State

Use `.constraint-kit/discipline.md` as git-ignored active state. Record:
status (`ACTIVE`, `RECOVERY`, `CLOSED`, or `ABANDONED`), phase, active
task, approved checkpoint, authority links, allowed scope, required
validation, next permitted action, next human gate, parked detours, named
exceptions, and recovery rulings. Authority stays in `docs/PROJECT.md` and
approved design, specification, and plan artifacts.

## Pre-action Guard

Before mutation, validation-scope expansion, or workflow advancement, read
active state and its authority and classify the proposed action. Read-only
discovery needed to locate, load, or classify state is allowed first.
Unclassifiable work is unapproved. Do not act until its gate is resolved.

## Action Classifications

Use exactly one: approved in-scope work; expected TDD RED; current-work
regression; necessary same-outcome blocker; unrelated finding; behavior,
architecture, constraint, or scope change; constraint conflict; or
unclassifiable action. Route each classification using SCENARIOS.md.

## Human Gates

Require approval for design, specification and plan handoffs, scope or
constraint changes, named exceptions, destructive recovery, and final
closure, abandonment, or reset. Ordinary in-scope TDD and focused
validation proceed autonomously.

## Named Exceptions

State one violated rule, one requested action, its consequence, and the
next checkpoint. Proceed only after explicit approval of that named
exception. Record it; never treat it as a standing waiver.

## Drift Recovery

Freeze edits and enter `RECOVERY`. Compare changes with the last approved
checkpoint; classify each as compliant, recoverable, or violating. Keep
only validated compliant work, route recoverable work through its missing
gate, and request approval before destructive reversal. Never erase
unrelated user work. Ambiguous evidence is unapproved.

## Close, Abandon, or Reset

Never expire silently. Record `CLOSED` or `ABANDONED` before replacing
active state. Reset requires explicit approval and a terminal record for
the prior workflow.
```

Also include an active-ledger Markdown template with every field named
above, a fail-closed rule for missing/malformed/contradictory state, a rule
that a missing ledger does not prove inactivity when authoritative artifacts
show unresolved work, and a relative link to `[Scenario matrix](SCENARIOS.md)`.

- [x] **Step 4: Create the scenario matrix**

Create `SCENARIOS.md` with this exact table interface and one row for every
required scenario identifier:

```markdown
| ID | Starting state | Proposed action | Classification | Allowed | Forbidden | Human gate | Resulting state |
|---|---|---|---|---|---|---|---|
| design-to-spec | Approved design | Write specification | Approved transition | Synthesize spec | Implement | Approve spec handoff | ACTIVE/specification |
| resumed-session | ACTIVE with authority links | Resume next action | Approved in-scope work | Reload authority and continue | Infer state from chat | None | Unchanged |
| expected-red | ACTIVE implementation task | Run expected failing test | Expected TDD RED | Continue TDD | Enter recovery | None | Unchanged |
| current-work-regression | ACTIVE implementation task | Repair caused regression | Current-work regression | Repair and rerun focused check | Broaden scope | None | Unchanged |
| dry-run-blocker | ACTIVE validation | Fix required same-outcome blocker | Necessary same-outcome blocker | Record micro-task and test | Casual adjacent fix | None | Unchanged |
| unrelated-finding | ACTIVE task | Fix unrelated issue | Unrelated finding | Park evidence | Edit or widen tests | None | Unchanged |
| scope-changing-finding | ACTIVE task | Change approved behavior | Scope change | Freeze and return to gate | Implement new behavior | Scope approval | ACTIVE/design or planning |
| implicit-override | ACTIVE task | “Just fix it” against a rule | Constraint conflict | Name exception request | Treat command as waiver | Named-exception approval | Unchanged |
| named-exception | ACTIVE with approved exception | Perform named action | Approved exception | Execute only named action | Generalize waiver | None | Unchanged |
| post-edit-drift | ACTIVE with unapproved changes | Continue editing | Drift | Freeze and classify changes | Add more changes | Recovery rulings | RECOVERY |
| invalid-ledger | Missing or invalid active state | Mutating action | Unclassifiable action | Read-only diagnosis | Write | Restore state | RECOVERY |
| explicit-close-reset | ACTIVE completed or abandoned work | Replace active state | Terminal transition | Record terminal state | Silent replacement | Close/reset approval | CLOSED or ABANDONED |
```

- [x] **Step 5: Run validation to verify GREEN**

Run: `python3 scripts/validate.py`

Expected: `OK — marketplace and plugin structure valid`

- [x] **Step 6: Commit the canonical contract**

```bash
git add scripts/validate.py plugins/constraint-design/skills/discipline-protocol
git commit -m "feat: define persistent discipline protocol"
```

### Task 2: Design Lifecycle Adapters

**Files:**
- Modify: `scripts/validate.py`
- Modify: `plugins/constraint-design/skills/brainstorming/SKILL.md:27-43`
- Modify: `plugins/constraint-design/skills/writing-specs/SKILL.md:6-36`
- Modify: `plugins/constraint-design/skills/writing-plans/SKILL.md:6-23`

**Interfaces:**
- Consumes: the canonical `discipline-protocol` skill and each phase's
  existing approval result.
- Produces: initialized or advanced active state with no duplicated
  transition logic.

- [x] **Step 1: Add failing design-adapter checks**

Add this map and checker to `scripts/validate.py`, then call
`check_discipline_adapters()` from `main()`:

```python
DISCIPLINE_ADAPTERS = {
    ROOT / "plugins/constraint-design/skills/brainstorming/SKILL.md":
        "REQUIRED SUB-SKILL: Use `discipline-protocol`",
    ROOT / "plugins/constraint-design/skills/writing-specs/SKILL.md":
        "REQUIRED SUB-SKILL: Use `discipline-protocol`",
    ROOT / "plugins/constraint-design/skills/writing-plans/SKILL.md":
        "REQUIRED SUB-SKILL: Use `discipline-protocol`",
}


def check_discipline_adapters() -> None:
    for path, required in DISCIPLINE_ADAPTERS.items():
        require_text(path, (required,))
```

- [x] **Step 2: Run the validator to verify RED**

Run: `python3 scripts/validate.py`

Expected: FAIL names all three design-phase skills as missing the required
protocol invocation.

- [x] **Step 3: Add the brainstorming adapter**

Add a `## Discipline Protocol` section before the checklist:

```markdown
**REQUIRED SUB-SKILL: Use `discipline-protocol`.** At workflow start, create
or resume its active state before producing an actionable artifact. Record
the topic as allowed exploratory scope and the approved design as the first
approved checkpoint. Exploration may remain conversational, but no edit,
validation expansion, or phase transition may bypass the protocol guard.
```

Update the transition step so written-design approval advances the active
state to the specification gate before invoking `writing-specs`.

- [x] **Step 4: Add the specification adapter**

Add after the writing-spec overview:

```markdown
**REQUIRED SUB-SKILL: Use `discipline-protocol`.** Resume the active state
and verify that it references an approved design before writing the spec.
After the user confirms the testing seams and the spec is saved, record the
specification checkpoint and its plan-handoff gate. Never use the spec to
retroactively approve a missing design gate.
```

- [x] **Step 5: Add the planning adapter**

Add after the writing-plan overview:

```markdown
**REQUIRED SUB-SKILL: Use `discipline-protocol`.** Resume the active state
and verify that it references an approved specification before writing the
plan. After the plan is saved and the user chooses an execution mode,
record the approved plan checkpoint, execution mode, first task, required
validation, and next gate.
```

- [x] **Step 6: Run validation to verify GREEN**

Run: `python3 scripts/validate.py`

Expected: `OK — marketplace and plugin structure valid`

- [x] **Step 7: Commit design adapters**

```bash
git add scripts/validate.py plugins/constraint-design/skills/brainstorming/SKILL.md plugins/constraint-design/skills/writing-specs/SKILL.md plugins/constraint-design/skills/writing-plans/SKILL.md
git commit -m "feat: preserve discipline across design phases"
```

### Task 3: Development Lifecycle Adapters

**Files:**
- Modify: `scripts/validate.py`
- Modify: `plugins/constraint-dev/skills/executing-plans/SKILL.md:12-35`
- Modify: `plugins/constraint-dev/skills/subagent-driven-development/SKILL.md:117-159`
- Modify: `plugins/constraint-dev/skills/test-driven-development/SKILL.md:20-68`
- Modify: `plugins/constraint-dev/skills/session-ledger/SKILL.md:21-95`

**Interfaces:**
- Consumes: an approved plan checkpoint and the canonical
  `discipline-protocol` skill from the constraint-design plugin.
- Produces: guarded execution, deterministic testing-detour routing, and a
  session ledger tied to the active lifecycle checkpoint.

- [x] **Step 1: Extend the adapter check to development skills**

Add these entries to `DISCIPLINE_ADAPTERS`:

```python
    ROOT / "plugins/constraint-dev/skills/executing-plans/SKILL.md":
        "REQUIRED SUB-SKILL: Use `discipline-protocol` from the constraint-design plugin",
    ROOT / "plugins/constraint-dev/skills/subagent-driven-development/SKILL.md":
        "REQUIRED SUB-SKILL: Use `discipline-protocol` from the constraint-design plugin",
    ROOT / "plugins/constraint-dev/skills/test-driven-development/SKILL.md":
        "REQUIRED SUB-SKILL: Use `discipline-protocol` from the constraint-design plugin",
    ROOT / "plugins/constraint-dev/skills/session-ledger/SKILL.md":
        "REQUIRED SUB-SKILL: Use `discipline-protocol` from the constraint-design plugin",
```

- [x] **Step 2: Run the validator to verify RED**

Run: `python3 scripts/validate.py`

Expected: FAIL names all four development skills as missing the required
cross-plugin invocation.

- [x] **Step 3: Guard inline plan execution**

Add beside the existing session-ledger requirement:

```markdown
**REQUIRED SUB-SKILL: Use `discipline-protocol` from the constraint-design
plugin.** Before task execution, verify that active state references this
approved plan, selected inline execution, and names the first permitted
task. Apply its pre-action guard before each task and its detour classifier
to every finding that is not already represented by the task.
```

- [x] **Step 4: Guard subagent-driven execution**

Add at the start of workspace setup:

```markdown
**REQUIRED SUB-SKILL: Use `discipline-protocol` from the constraint-design
plugin.** Verify the approved plan checkpoint before the first dispatch.
Every task brief carries the checkpoint, allowed scope, required validation,
and named exceptions. Classify findings before dispatching fixes; park
unrelated findings and return scope-changing findings to the human gate.
```

Also require each task completion ledger entry to update the active task and
next gate without copying attempts or review rounds into the discipline
ledger.

- [x] **Step 5: Add the TDD detour classifier**

Add before the RED-GREEN-REFACTOR procedure:

```markdown
**REQUIRED SUB-SKILL: Use `discipline-protocol` from the constraint-design
plugin.** Classify every test result before editing: expected RED continues
the cycle; a current-work regression is repaired in-task; a necessary
same-outcome blocker becomes a bounded micro-task; an unrelated finding is
parked; and a behavior, architecture, constraint, or scope change returns
to its human gate. “Small,” “nearby,” and “obvious” do not authorize work.
```

- [x] **Step 6: Bind the operational ledger to lifecycle state**

Add to session open and replace the current major-boundary-only drift check:

```markdown
**REQUIRED SUB-SKILL: Use `discipline-protocol` from the constraint-design
plugin.** Read `.constraint-kit/discipline.md` and its authority before
initializing operational tracking. Record the approved checkpoint in the
session ledger. The discipline ledger owns lifecycle state; this ledger
continues to own attempts, edit verification, review rounds, progress, and
budget.

Before any mutation, validation-scope expansion, or workflow advancement,
apply the protocol's pre-action guard. Keep the existing major-subtask
constraint re-read as a second check, not the first point at which drift is
detected. During wrap-up, retain `ACTIVE` state with final closure as the
next gate; record `CLOSED` or `ABANDONED` only after explicit human approval.
```

- [x] **Step 7: Run validation to verify GREEN**

Run: `python3 scripts/validate.py`

Expected: `OK — marketplace and plugin structure valid`

- [x] **Step 8: Commit development adapters**

```bash
git add scripts/validate.py plugins/constraint-dev/skills/executing-plans/SKILL.md plugins/constraint-dev/skills/subagent-driven-development/SKILL.md plugins/constraint-dev/skills/test-driven-development/SKILL.md plugins/constraint-dev/skills/session-ledger/SKILL.md
git commit -m "feat: guard implementation against discipline drift"
```

### Task 4: Persistence Hook and Product Documentation

**Files:**
- Modify: `scripts/validate.py`
- Modify: `plugins/constraint-design/skills/project-intake/SKILL.md:110-130`
- Modify: `plugins/constraint-design/README.md:1-31`
- Modify: `plugins/constraint-design/plugin.json`
- Modify: `plugins/constraint-dev/README.md:1-30`
- Modify: `plugins/constraint-dev/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md:1-105`
- Modify: `docs/DESIGN.md:36-170`
- Modify: `CHANGELOG.md:7-76`

**Interfaces:**
- Consumes: the canonical protocol name and active-ledger location.
- Produces: an imperative generated instruction that persists enforcement
  across sessions, plus discoverable plugin metadata and workflow docs.

- [x] **Step 1: Add the failing persistence-hook check**

Add this entry to `DISCIPLINE_ADAPTERS`:

```python
    ROOT / "plugins/constraint-design/skills/project-intake/SKILL.md":
        "When `.constraint-kit/discipline.md` is ACTIVE or RECOVERY",
```

- [x] **Step 2: Run the validator to verify RED**

Run: `python3 scripts/validate.py`

Expected: FAIL names `project-intake` as missing the persistent instruction
hook.

- [x] **Step 3: Add the generated project instruction**

Add this required line to the project-intake instruction-generation rules:

```markdown
- Include this line so active discipline survives session boundaries:
  "When `.constraint-kit/discipline.md` is ACTIVE or RECOVERY, read it and
  every authoritative artifact it references before mutating files or
  external state, broadening validation, or advancing workflow."
```

Because project archaeology explicitly follows project-intake's generation
rules, do not duplicate the sentence there.

- [x] **Step 4: Document discovery and ownership**

Update the design-plugin README skill table with a `discipline-protocol` row
whose stage is `Cross-lifecycle` and whose output is
`.constraint-kit/discipline.md`. Add it to the workflow as the persistent
guard spanning design and development.

Update the development-plugin README to state that execution skills consume
`discipline-protocol` from constraint-design while `session-ledger` retains
operational bookkeeping ownership.

Update both plugin descriptions and marketplace descriptions to mention the
persistent cross-lifecycle discipline protocol. Add the keyword
`discipline` to both plugin keyword arrays without changing plugin versions.

Update the root README workflow and artifact tree to show
`.constraint-kit/discipline.md` beside `.constraint-kit/sdd/`. Update the
architecture design's skill map and artifact table. Add an `Unreleased`
changelog entry describing the canonical protocol, phase adapters, scenario
contract, and persistent instruction hook.

- [x] **Step 5: Run complete protocol and structure validation**

Run: `python3 scripts/validate.py`

Expected: `OK — marketplace and plugin structure valid`

- [x] **Step 6: Review the complete diff against the specification**

Run:

```bash
git diff --check
git diff --stat
```

Expected: `git diff --check` prints nothing; the stat contains only the
files named by this plan plus the approved design, specification, glossary,
and plan artifacts.

- [x] **Step 7: Commit persistence and documentation**

```bash
git add scripts/validate.py plugins/constraint-design plugins/constraint-dev .claude-plugin/marketplace.json README.md docs/DESIGN.md CHANGELOG.md docs/GLOSSARY.md docs/constraint-kit
git commit -m "docs: integrate discipline protocol workflow"
```

## Final Verification

- [x] Run `python3 scripts/validate.py` and require exit code 0.
- [x] Run `git diff --check` and require no output.
- [x] Confirm `git status --short --branch` shows
  `feature/discipline-protocol` and no uncommitted files.
- [x] Review all twelve scenario rows against each relevant adapter and
  confirm no adapter authorizes a forbidden action.
- [ ] Use the `finishing-a-development-branch` skill from the constraint-dev
  plugin to choose merge, pull request, retention, or discard.

## Execution Record

- Implemented in commits `a9baa76`, `1bee1f6`, `b991d43`, and `2fff137`.
- Independent review found planner authorization, ignore initialization,
  scenario recovery outcomes, and structural scenario validation gaps.
- Corrected and re-reviewed in `5681262`; no Critical or Important findings
  remain.
- Parked Minor: validate the Markdown delimiter row in addition to the table
  header and data rows if future table parsing becomes more general.