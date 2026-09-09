# Scoped Re-Review Prompt Template

Dispatch via `runSubagent` after a fix round. The re-reviewer verdicts
each prior finding and inspects the fix diff for new breakage. It is not
a fresh review.

```
runSubagent:
  agentName: reviewer
  description: "Re-review Task N fix round R"
  prompt: |
    Use [MODEL] for this re-review. (Preferred: MAI-Code-1-Flash or
    GPT-5.6 Luna — small fix diffs take the cheap tier; see SKILL.md.)

    You are re-reviewing one fix round. Verdict each finding and inspect
    the fix diff — nothing else.

    Task brief: [BRIEF_FILE]
    Implementer report (fix reports appended at the end): [REPORT_FILE]

    ## Findings Under Verification

    [FINDINGS]

    ## The Fix

    Fix base [FIX_BASE_SHA] (head the previous review saw), head
    [HEAD_SHA], package: [DIFF_FILE]

    Read the package once: fix commits, stat, diff with context. Do not
    re-run git. If it is missing: `git diff --stat` and `git diff` over
    [FIX_BASE_SHA]..[HEAD_SHA]. Read-only: do not mutate the working
    tree, index, HEAD, or branches.

    ## Scope

    The findings list and the fix diff. Do NOT re-review untouched code;
    anything outside the fix diff goes under Out-of-Scope Observations and
    does not block this task.

    ## Tests

    The fix report should name the covering tests and show their output.
    Treat it as unverified claims and check them against the diff. Do not
    re-run the suite; run one focused test only for a specific doubt no
    existing run answers.

    ## Output

    Begin directly with the first verdict. No preamble or narration.

    ### Finding Verdicts
    For each finding, in order:
    - **[finding]** — ADDRESSED | NOT ADDRESSED, with file:line evidence.
      "Attempted" is not addressed: the specific defect must be gone.

    ### New Breakage in the Fix Diff
    Severity (Critical/Important/Minor) and file:line, or "None".

    ### Out-of-Scope Observations
    Non-blocking; the controller ledgers these. "None" if none.

    ### Verdict
    All findings addressed, no new Critical/Important breakage |
    Findings remain open — list them.
```

**Placeholders:** `[MODEL]`; `[BRIEF_FILE]`, `[REPORT_FILE]` (same files
as the implementer); `[FINDINGS]` (Critical/Important findings and spec
gaps from the previous review, verbatim, one per bullet);
`[FIX_BASE_SHA]`, `[HEAD_SHA]`; `[DIFF_FILE]` (path printed by
`scripts/review-package PLAN_FILE FIX_BASE HEAD`).
