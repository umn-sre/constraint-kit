# Implementer Subagent Prompt Template

Dispatch via `runSubagent`. The subagent is stateless and cannot ask
questions: everything it needs is in this prompt or the files it names.

```
runSubagent:
  agentName: implementer
  description: "Implement Task N: [task name]"
  prompt: |
    Use [MODEL] for this task. (Preferred: Claude Sonnet 5 — see SKILL.md
    Model Selection. Omit only if the agent file's model list is right.)

    You are implementing Task N: [task name]. Work from: [directory]

    ## Requirements

    Read your task brief first: [BRIEF_FILE]. It is your requirements,
    with the exact values to use verbatim.

    ## Context

    [One line on where this fits; interfaces and decisions from earlier
    tasks; the controller's resolution of any ambiguity in the brief;
    pointer to any parked ledger entry in this area]

    ## Your Job

    1. Implement exactly what the brief specifies — nothing more (YAGNI).
    2. Write tests (TDD if the brief says so). Run the focused test while
       iterating; run the full suite once before committing.
    3. Commit your work.
    4. Self-review (below), fix what you find.
    5. Write the report and return the short contract.

    Follow the plan's file structure and the codebase's existing patterns.
    If a file you create grows beyond the plan's intent, or a file you
    modify is already tangled, do not restructure — finish and report
    DONE_WITH_CONCERNS.

    ## When to Stop

    You cannot ask questions mid-run. If requirements are ambiguous, the
    task needs an architectural decision, you cannot find the code you
    need, or you are reading file after file without progress: stop and
    report NEEDS_CONTEXT (missing information) or BLOCKED (cannot
    complete). Say what you are stuck on, what you tried, and what would
    unblock you. Bad work is worse than no work; escalating is not
    penalized.

    ## Self-Review

    - Completeness: every requirement met; edge cases handled.
    - Quality: names say what things do; code is clean and maintainable.
    - Discipline: nothing beyond the request; existing patterns followed.
    - Tests: verify behavior, not mocks; output pristine (no warnings).

    ## Report

    Write the full report to [REPORT_FILE]: what you implemented (or
    attempted), tests and results, TDD evidence if required (RED: command,
    failing output, why expected; GREEN: command, passing output), files
    changed, self-review findings, concerns.

    Then return ONLY, under 15 lines:
    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - Commits (short SHA + subject)
    - One-line test summary ("14/14 passing, output pristine")
    - Concerns, if any
    - Report file path

    For BLOCKED or NEEDS_CONTEXT, put the specifics in this message — the
    controller acts on it directly. Never silently return work you doubt.
```

## Fix-round dispatch

Same template, fresh subagent, with this replacing **Context**:

```
    ## Fix Round R

    A previous review found these issues (verbatim):
    [FINDINGS]

    Read [REPORT_FILE] for what was already built and tried. Fix each
    finding, re-run the covering tests ([TEST_FILES]), and append a fix
    report to the same report file: what changed, tests run, command,
    output. Reviewers will not re-run tests — your report is the evidence.
    Return the same short contract.
```

Rounds 4-5 add: "A prior implementer attempted this task [N] times; you
own it now."

**Placeholders:** `[MODEL]`, `[BRIEF_FILE]` (from `scripts/task-brief`),
`[REPORT_FILE]` (`task-N-report.md` beside the brief), `[FINDINGS]`,
`[TEST_FILES]`.
