---
name: subagent-driven-development
description: Use when executing an implementation plan with mostly independent tasks in the current session - dispatches a fresh implementer subagent per task via runSubagent, a task review after each, and a whole-branch review at the end, with ledger-tracked progress.
argument-hint: 'Path to the plan in docs/constraint-kit/plans/'
---

# Subagent-Driven Development

Execute a plan by dispatching a fresh implementer subagent per task, a
task review (spec compliance + code quality) after each, and one
whole-branch review at the end.

**Why subagents:** each subagent gets an isolated context you construct
precisely — never your session history. They stay focused; you keep your
own context for coordination.

**Continuous execution:** do not check in between tasks. Stop only for a
BLOCKED state you cannot resolve, ambiguity that prevents progress, or
completion. Narrate at most one short line between tool calls.

## When to Use

- Have a written plan → tasks mostly independent → staying in this
  session: **this skill**.
- Need a separate session or subagents are unavailable:
  `executing-plans`.
- Tasks tightly coupled or no plan: execute manually or brainstorm first.

## How Subagents Work Here

Dispatch through the `runSubagent` tool (listed as `agent` or
`runSubagent` in a `tools:` header). Each call takes an `agentName`
(this plugin's `implementer` or `reviewer` custom agent), a one-line
`description`, and the `prompt`. In Claude Code, the equivalent is the
Agent tool with `subagent_type: general-purpose`.

Constraints that shape everything below:

- **Stateless.** A subagent runs once and returns. You cannot send it a
  follow-up, so every dispatch — including fix rounds — carries all its
  context: brief path, report path, findings.
- **No questions.** Subagents cannot ask you anything mid-run. Missing
  context comes back as `NEEDS_CONTEXT`; you re-dispatch with more.
- **Cost tier cap.** A subagent's model cannot exceed the cost tier of the
  session model. Run the conductor on a tier at least as high as the
  strongest model you may escalate to.
- **Nesting is off by default** (`chat.subagents.allowInvocationsFromSubagents`).
  Subagents do the work; you do the dispatching.
- **Files, not pasted text.** Everything in a dispatch prompt and every
  reply stays in your context for the session. Hand over briefs, reports,
  and diffs as file paths.

## Model Selection

State a preferred model in each dispatch, or rely on the `model:` fallback
list in the agent file. Omitting both inherits the session model — often
the most expensive.

| Role | Preferred | Notes |
|---|---|---|
| Implementer (writes code) | Claude Sonnet 5 | Lowest-cost model that codes reliably. Fast tier only when the brief contains the complete code to write. |
| Task reviewer, re-reviewer | GPT-5.6 Luna or MAI-Code-1-Flash | Reads a diff, writes findings — no code. Scale up for subtle changes (concurrency, auth, data). |
| Final whole-branch review | Most capable model at or below the session tier | Design judgment across the whole diff. |
| Fix rounds 4-5 | One tier above the stuck implementer, within the cap | If the cap blocks escalation, change the input instead: split the task or add context. |

**Turn count beats token price.** The cheapest models take 2-3× the turns
on multi-step work. Mid-tier is the floor for implementers working from
prose descriptions.

## Setup

1. **Isolated workspace.** Verify a dedicated worktree or feature branch.
   Never implement on main/master without explicit consent.
2. **Plan workspace.** Run `scripts/sdd-workspace PLAN_FILE`; it prints
   `<repo-root>/.constraint-kit/sdd/<plan-basename>/`, home to every
   artifact for this plan. Other plans' directories are not yours.
3. **Ledger.** Check `<workspace>/progress.md`. If its first line names
   your plan, tasks with a `Task <N>: complete` line are done — resume at
   the first without one; a task whose last line is a fix round resumes at
   the next round. A ledger naming a different plan is not yours: start
   fresh with `# SDD ledger — plan: <plan file path>` as line one.
   Context does not survive compaction; the ledger and `git log` do.
   Trust them over recollection.
4. **Read the plan once.** Note its Global Constraints; create a todo per
   task.
5. **Pre-flight conflict scan.** Tasks that contradict each other or the
   constraints, or anything the plan mandates that the review rubric
   treats as a defect (a test asserting nothing, verbatim duplication):
   present all findings to the user as one batched question before Task 1.
   Clean scan → proceed silently.

## The Task Loop

### 1. Dispatch the implementer

Record `BASE=$(git rev-parse HEAD)`. Run `scripts/task-brief PLAN_FILE N`;
it writes the task text to `task-N-brief.md` and prints the path. Name the
report `task-N-report.md` beside it.

Dispatch with [implementer-prompt.md](implementer-prompt.md). The prompt
holds: one line on where the task fits; the brief path ("read this first
— it is your requirements, with exact values to use verbatim");
interfaces and decisions from earlier tasks the brief cannot know; your
resolution of any ambiguity; pointers to ledger entries parked in this
area; the report path and report contract. Exact values live only in the
brief. Never hand a subagent the whole plan, and never paste prior-task
summaries — one real dispatch reached 42k chars of pasted history.

One implementer at a time. Parallel implementers conflict.

### 2. Handle the report

- **DONE:** run `scripts/review-package PLAN_FILE $BASE HEAD` (never
  `HEAD~1`, which drops earlier commits of a multi-commit task) and
  dispatch the task reviewer with the printed path.
- **DONE_WITH_CONCERNS:** read the concerns. Correctness or scope doubts
  → address before review. Observations → note and proceed.
- **NEEDS_CONTEXT:** supply the missing context and re-dispatch.
- **BLOCKED:** diagnose. Context problem → re-dispatch with more context.
  Reasoning problem → more capable model (within the cap). Too large →
  split. Plan wrong → escalate to the user. Never retry unchanged.

### 3. Review the task

Dispatch [task-reviewer-prompt.md](task-reviewer-prompt.md) with the
brief, the report, the review package, and the plan's Global Constraints
copied verbatim (exact values, formats, stated relationships). The
template already carries process rules; the constraints block is what
this project's spec demands.

Rules for the reviewer prompt:

- No open-ended directives ("check all uses") without a concrete reason.
- Do not ask it to re-run tests the implementer ran; the report is the
  evidence.
- Never pre-judge: "do not flag", "at most Minor", "the plan chose" — stop.
  Let the finding surface and adjudicate it in the loop.

Both verdicts are required: spec compliance and task quality. Implementer
self-review never replaces the task review. Resolve every
"⚠️ Cannot verify from diff" item yourself — you hold the cross-task
context. A confirmed gap enters the fix loop as a failed spec review.

### 4. The fix loop

Triggers: spec ❌, any Critical or Important finding, or a ⚠️ you
confirmed. Two things never enter the loop:

- **Minor findings** → ledger: `Task <N>: minor (deferred): <one-liner>`.
  The final review triages them.
- **Plan-mandated findings** (or any finding contradicting plan text) →
  user decides which governs. Never dismiss, never fix against the plan
  unasked.

A fix round = one fix dispatch + one scoped re-review. Five rounds max.

- **Rounds 1-3:** fresh implementer, same model, carrying the brief path,
  the report path, and the open findings verbatim. The report file is its
  memory of what was tried.
- **Rounds 4-5:** fresh implementer, one tier up (within the cap), framed:
  "A prior implementer attempted this task [N] times; you own it now. Read
  the report file for what was tried."
- **Every round:** the implementer fixes, re-runs the covering tests
  (name them in the dispatch), appends a fix report to the same report
  file, and returns the short contract. Confirm the fix report shows the
  tests, the command, and the output before re-reviewing.
- **Re-review is scoped:** `scripts/review-package PLAN_FILE FIX_BASE HEAD`
  (FIX_BASE = head the previous review saw), then
  [re-review-prompt.md](re-review-prompt.md). Each finding gets ADDRESSED
  or NOT ADDRESSED; new Critical/Important breakage in the fix diff joins
  the open list; out-of-scope observations go to the ledger as minors.
- **Ledger after each round:**
  `Task <N>: fix round <R>/5 (<X> addressed, <Y> open — <one-liners>; commits <a7>..<b7>)`

Never fix findings yourself. Controller fixes pollute your context and
skip review.

**The breaker.** After round 5 with findings still open, adjudicate each
one — only now, and always as a ledger entry:

- Reviewer wrong or contestable → `Task <N>: parked — <finding> — ruling: <why the code stands>`
- Real but nothing downstream depends on it → park, ruling says "real, deferred"
- Real and load-bearing (a later task builds on it, or a plan defect) →
  `Task <N>: BLOCKED — <reason>`; stop and report the finding, the plan
  text, and the fix history.

### 5. Complete the task

Ledger: `Task <N>: complete (commits <base7>..<head7>, review clean)` or
`(…, <K> parked)`. Mark the todo. Never advance with an open
Critical/Important finding that is neither fixed nor parked with a ruling.

## Final Review

`scripts/review-package PLAN_FILE $(git merge-base main HEAD) HEAD`, then
dispatch the `reviewer` agent with
[code-reviewer.md](../requesting-code-review/code-reviewer.md) on the
most capable model within the cap. Point it at the ledger's deferred and
parked lines to triage what must be fixed before merge.

Findings → **one** fix dispatch with the complete list (per-finding fixers
each rebuild context; one session's fix wave cost more than all its
tasks), then **one** scoped re-review via
[re-review-prompt.md](re-review-prompt.md). Adjudicate residuals as in the
breaker. No second fix wave; load-bearing residuals reach the user when
finishing-a-development-branch presents options.

## Finish

Final review clean and fixes merged → `rm -rf <workspace>` (this plan's
directory only; git history is the record). Then use the
finishing-a-development-branch skill.

## Rationalizations

| Excuse | Reality |
|---|---|
| "Close enough on spec" | Spec gaps = not done. Fix, or reach the cap and adjudicate. |
| "I'll fix it myself" | Controller fixes skip review and pollute context. Dispatch. |
| "One more round will converge" | Past the cap the failure is structural. Adjudicate. |
| "Obviously wrong finding, drop it" | Adjudicate only at the cap; every ruling is a ledger line. |
| "Small fix, skip the re-review" | Unreviewed fixes are how regressions land. |
| "Ledger is overhead" | Controllers without one re-dispatched whole completed task sequences. |

## Example

```
[Setup: worktree ok; sdd-workspace → no ledger; todos created]
Task 2: [BASE recorded; task-brief → dispatch implementer]
Implementer: DONE — 2 commits, 8/8 passing, report at task-2-report.md
[review-package BASE..HEAD → dispatch task reviewer]
Reviewer: Spec ❌ missing progress reporting; Important: magic number 100
[Fix round 1: fresh implementer + brief + report + both findings]
Implementer: DONE — 1 commit, recovery.test.js 10/10, fix report appended
[review-package FIX_BASE..HEAD → dispatch re-review]
Re-reviewer: both ADDRESSED, no new breakage
[Ledger: Task 2: fix round 1/5 (2 addressed, 0 open; commits d4e5f6a..b7c8d9e)]
[Ledger: Task 2: complete (commits d4e5f6a..b7c8d9e, review clean)]
```
