# Skill: Decision Records

## Purpose

Decisions made without a record become invisible. Future contributors —
including your future self — cannot understand why things are the way
they are, cannot safely change them, and repeat the same deliberations.
A decision record makes the reasoning permanent.

## When This Skill Is Active

Whenever a significant decision is being made or documented:
architecture choices, methodology selections, approach tradeoffs,
policy decisions, research design choices.

## Agent Behavior

### What qualifies as a recordable decision

Record a decision when:
- It would be costly or disruptive to reverse
- Multiple reasonable alternatives existed
- Future contributors might question or revisit it
- The "why" is not obvious from the outcome alone

### Decision record structure

Every decision record contains exactly these sections:

```markdown

# Decision: [short title]

Date: YYYY-MM-DD
Status: proposed | accepted | deprecated | superseded by [id]

## Context

What situation or problem prompted this decision?
What forces are at play? What constraints exist?
(3-6 sentences. Be specific about the circumstances.)

## Options Considered

### Option A: [name]

[brief description]
Pros: [what it gets right]
Cons: [what it gets wrong or risks it carries]

### Option B: [name]

[brief description]
Pros:
Cons:

(add more options as needed — minimum two)

## Decision

[State the decision clearly in one or two sentences.]
[Name the option chosen.]

## Rationale

[Explain why this option over the others.]
[Reference the context and constraints above.]
[Be specific — "it seemed best" is not rationale.]

## Consequences

### Positive

- [what this decision enables or improves]

### Negative / Trade-offs

- [what this decision costs or forecloses]

### Risks

- [what could go wrong, and how it will be monitored]

## Review Trigger

[Under what circumstances should this decision be revisited?]
[Example: "If X changes" or "When load exceeds Y"]

```

### Before drafting a decision record

Ask:
1. Is the context specific enough that someone unfamiliar could understand
   the situation?
2. Are at least two genuine options documented — not a real option
   and a straw man?
3. Is the rationale tied to the context, not just generic preference?
4. Are the negative consequences honestly stated?

## Anti-Patterns

- Do NOT document decisions after the fact as if alternatives were
  never considered — that produces a rationale document, not a
  decision record
- Do NOT record trivial decisions — reserve this for consequential ones
- Do NOT omit the negative consequences — honest records are more
  useful than flattering ones
- Do NOT leave status as "proposed" indefinitely — decisions should
  be accepted, deprecated, or superseded

## File naming convention (for repo-based projects)

```

docs/decisions/
  0001-[short-title].md
  0002-[short-title].md

```

Sequential numbering. kebab-case title. Permanent — never delete,
only supersede.

## Transition

A decision record is a terminal artifact — it documents a decision
that has been made. Once written and accepted, return to the workflow
that produced the decision:
- Back to `requirements-gathering` if requirements need updating
- Back to `brainstorming` if the decision opened new questions
- Forward to implementation if the decision was the blocker
