# Preflight Notes QC Drill

**Location:** `constraint-kit/docs/QC_DRILL.md`
**Purpose:** Validate opening notes before a real preflight run.
**When to use:** Any time you want confidence that your notes are preflight-ready
before invoking `session-preflight` (core skill, `skills/session-preflight/SKILL.md`)
for real.

This drill is surface-agnostic and project-agnostic — it contains no
constraint-kit-specific or ck-personal-specific questions, only the generic
gap-audit prompt below. Consumers that vendor constraint-kit as a submodule
(e.g. `ck-personal`) should reference this copy at
`vendor/constraint-kit/docs/QC_DRILL.md` rather than keeping a duplicate.

## Workflow

## How to Use

1. Write your opening notes as you normally would for a preflight session.
2. Open a fresh session on your target surface (claude-browser, copilot, etc.).
3. Paste your notes, then paste the drill prompt below.
4. Read the three lists the agent produces.
5. Revise your notes to eliminate all blocking gaps.
6. Repeat until the blocking gap list is empty.
7. Only then begin the real preflight session.

The drill prompt instructs the agent not to generate any artifacts.
If the agent drifts into planning or spec generation, that is itself a signal
that your notes were specific enough to trigger execution — check the
recoverable gaps list and decide if you are satisfied.

## Prompt Section

## QC Drill Prompt

> Paste your opening notes above this line, then append the block below.

## Prompt Body

Read the notes above. Do not generate any artifacts, SESSION_PLAN.md,
agent-base.yaml, or agent-implementer.yaml blocks.

Produce exactly three lists:

**1. Blocking gaps**
Assumptions you would have to make that could produce wrong or misaligned
output if incorrect. For each, write it as a specific question the notes
do not answer.

**2. Recoverable gaps**
Assumptions you would make that have a reasonable default, but the person
should confirm before proceeding. For each, state the assumption and the
default you would use.

**3. What is clear**
A brief, specific confirmation of what is unambiguous and requires no
assumption. Be concrete — do not just restate the notes.

Do not proceed past this output. Wait for the person to revise their notes
before taking any further action.

## Readiness Gate

## Exit Criterion

Your notes are preflight-ready when:

- [ ] Blocking gap list is empty
- [ ] Recoverable gaps are reviewed and either resolved or consciously accepted
- [ ] "What is clear" covers the core intent, mode, surface, and scope
