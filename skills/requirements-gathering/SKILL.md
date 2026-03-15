# Skill: Requirements Gathering

## Purpose

Produce a clear, confirmed set of requirements before any work product
is created. Requirements are not a wish list — they are a contract
between what is needed and what will be built or written.

## When This Skill Is Active

After brainstorming has confirmed the goal, before generating any
code, document, or structured output.

## Agent Behavior

### Distinguish requirement types

Sort everything into one of three buckets:

| Type | Meaning | Example |
|---|---|---|
| **Must** | Non-negotiable. Work fails without this. | "Must run on Python 3.12" |
| **Should** | Strong preference. Deviation needs justification. | "Should use existing pattern" |
| **Could** | Nice to have. Drop if scope demands it. | "Could include a summary report" |

### Separate requirements from assumptions

- State assumptions explicitly — never leave them implicit
- Ask the person to confirm or correct each assumption
- An unconfirmed assumption is a future bug or misunderstanding

### Identify what is out of scope

- Explicitly name things that are NOT being addressed
- Out-of-scope items are as important as in-scope ones
- They prevent scope creep and set expectations

### Produce a requirements summary

Before proceeding, write a short summary structured as:

```

GOAL: [one sentence]

MUST:
- [requirement]

SHOULD:
- [requirement]

COULD:
- [requirement]

ASSUMPTIONS:
- [assumption] — confirmed? yes/no

OUT OF SCOPE:
- [item]

```

Ask for explicit sign-off on this summary before generating anything.

## Anti-Patterns

- Do NOT conflate "must" and "should" — this causes scope creep
- Do NOT skip the out-of-scope list — omission implies inclusion
- Do NOT proceed without a confirmed summary
- Do NOT let assumptions stay implicit — name them every time
- Do NOT treat requirements as fixed — update the summary if scope changes

## Transition

When the person signs off on the requirements summary:
- For code: hand off to `test-driven-development` or `decision-records`
- For documents: hand off to `document-structure`
- For structured output: hand off to `decision-records` or the relevant template skill
