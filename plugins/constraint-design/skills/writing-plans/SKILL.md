---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code - designs the modules (deep interfaces at clean seams), then writes a bite-sized, test-first implementation plan.
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero
context for our codebase and questionable taste. Document everything they
need to know: which files to touch for each task, code, testing, docs they
might need to check, how to test it. Give them the whole plan as
bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our
toolset or problem domain. Assume they don't know good test design very
well.

**Announce at start:** "I'm using the writing-plans skill to create the
implementation plan."

**Save plans to:** `docs/constraint-kit/plans/YYYY-MM-DD-<feature-name>.md`

Use the vocabulary from `docs/GLOSSARY.md` and respect decision
records in `docs/constraint-kit/adr/`.

## Scope Check

If the spec covers multiple independent subsystems, it should have been
broken into sub-project specs during brainstorming. If it wasn't, suggest
breaking this into separate plans — one per subsystem. Each plan should
produce working, testable software on its own.

## Design the Modules First

Before defining tasks, decide the shape of the code: which modules exist,
what each one's interface is, and where the seams go. This is where
decomposition decisions get locked in — every task boundary follows from
it. Use this vocabulary exactly (don't substitute "component," "service,"
or "boundary"):

- **Module** — anything with an interface and an implementation: a
  function, class, package, or tier-spanning slice.
- **Interface** — everything a caller must know to use the module
  correctly: the type signature, but also invariants, ordering
  constraints, error modes, required configuration, and performance
  characteristics.
- **Seam** — the place where a module's interface lives; where you can
  alter behavior without editing in that place. Where the seam goes is its
  own design decision, distinct from what sits behind it.
- **Adapter** — a concrete thing that satisfies an interface at a seam.
- **Depth** — leverage at the interface: how much behavior a caller (or
  test) exercises per unit of interface they must learn. Design **deep
  modules**: a lot of behavior behind a small interface. Shallow modules —
  interfaces nearly as complex as their implementations — are the thing to
  avoid.

Principles that govern the design:

- **Depth is a property of the interface, not the implementation.** A deep
  module may be internally composed of small swappable parts — they just
  aren't part of the interface.
- **The deletion test.** Imagine deleting the module. If complexity
  vanishes, it was a pass-through. If complexity reappears across N
  callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same
  seam. If you want to test *past* the interface, the module is probably
  the wrong shape.
- **One adapter means a hypothetical seam; two adapters means a real
  one.** Don't introduce a seam unless something actually varies across it.
- **Design for testability:** accept dependencies, don't create them;
  return results, don't produce side effects; keep the surface small.

When designing an interface, ask: can I reduce the number of methods? Can
I simplify the parameters? Can I hide more complexity inside?

Going deeper:

- **Deepening a module given its dependencies** — see
  [DEEPENING.md](DEEPENING.md): dependency categories, seam discipline,
  and replace-don't-layer testing.
- **Exploring alternative interfaces** — see
  [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md): design the interface several
  radically different ways (parallel subagents if available), then compare
  on depth, locality, and seam placement.

### File Structure

With the modules decided, map out which files will be created or modified
and what each is responsible for:

- Each file should have one clear responsibility. Prefer smaller, focused
  files — you reason best about code you can hold in context at once.
- Files that change together should live together. Split by
  responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses
  large files, don't unilaterally restructure — but if a file you're
  modifying has grown unwieldy, including a split in the plan is
  reasonable.

This structure informs the task decomposition. Each task should produce
self-contained changes that make sense independently.

## Task Right-Sizing

A task is the smallest unit that carries its own test cycle and is worth a
fresh reviewer's gate. When drawing task boundaries: fold setup,
configuration, scaffolding, and documentation steps into the task whose
deliverable needs them; split only where a reviewer could meaningfully
reject one task while approving its neighbor. Each task ends with an
independently testable deliverable.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**

- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> subagent-driven-development (recommended) or executing-plans (both in
> the constraint-dev plugin) to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are
**plan failures** — never write them:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks
  out of order)
- Steps that describe what to do without showing how (code blocks required
  for code steps)
- References to types, functions, or methods not defined in any task

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and
check the plan against it. This is a checklist you run yourself — not a
subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you
point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags — any of the
patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property
names you used in later tasks match what you defined in earlier tasks? A
function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task
7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and
move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/constraint-kit/plans/<filename>.md`. Two
execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per
task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using
executing-plans, batch execution with checkpoints

**Which approach?"**

Both execution skills ship in the **constraint-dev** plugin:

- **If Subagent-Driven chosen:** REQUIRED SUB-SKILL:
  `subagent-driven-development` — fresh subagent per task + two-stage
  review
- **If Inline Execution chosen:** REQUIRED SUB-SKILL: `executing-plans` —
  batch execution with checkpoints
