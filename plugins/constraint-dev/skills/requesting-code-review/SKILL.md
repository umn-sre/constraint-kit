---
name: requesting-code-review
description: Use when completing a task, finishing a major feature, or before merging - dispatches a reviewer subagent via runSubagent with a precisely scoped diff and requirements, and returns prioritized findings without polluting the coordinator's context.
argument-hint: 'Optional: BASE..HEAD range and the plan task or spec to review against'
---

# Requesting Code Review

Dispatch a reviewer subagent to catch issues before they cascade. It gets
precisely crafted context — the diff, the requirements, nothing from your
session history — and only findings come back.

**Core principle:** review early, review often.

## When

**Mandatory:** after each task in subagent-driven development; after a
major feature; before merging to main.

**Valuable:** when stuck (fresh eyes); before a refactor (baseline); after
a complex bug fix.

## How

1. **Fix the range.** BASE is the commit the work started from — a
   recorded per-task base, or `git merge-base main HEAD` for a branch.
   Never `HEAD~1`: it silently drops all but the last commit.
2. **Package the diff as a file.** Run the subagent-driven-development
   skill's `scripts/review-package PLAN_FILE BASE HEAD` (or redirect
   `git log --oneline`, `git diff --stat`, and `git diff -U10` for the
   range into one file). The diff never enters your context; the reviewer
   reads it in one call.
3. **Dispatch** the `reviewer` agent through `runSubagent` with
   [code-reviewer.md](code-reviewer.md). Fill the placeholders: what was
   built, the requirements (plan task path, brief, or spec text), BASE and
   HEAD, and the diff file path. State a preferred model: GPT-5.6 Luna or
   MAI-Code-1-Flash for a task-sized diff; the most capable model within
   the session's cost tier for a whole-branch or pre-merge review.
4. **Act on findings.** Critical: fix now. Important: fix before
   proceeding. Minor: note for later. Reviewer wrong: push back with
   technical reasoning and the code or test that proves it.

The subagent is stateless: it cannot ask you for more context, and you
cannot send it a follow-up. Put everything it needs in the dispatch; for a
second look after fixes, dispatch again with the fix range.

## Rationalizations

| Excuse | Reality |
|---|---|
| "I'll review the diff myself" | Inline review burns the context you need to keep driving. The diff and the evaluation belong in the reviewer's context. |
| "It needs my whole session history" | Hand it the diff and the requirements. Session history steers it toward your reasoning instead of the work product. |
| "It's simple, skip review" | Simple diffs are where unreviewed regressions land. |

**Never** ignore a Critical finding, proceed with an unfixed Important
finding, or argue with valid technical feedback.
