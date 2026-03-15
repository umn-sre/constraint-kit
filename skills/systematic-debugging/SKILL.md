# Skill: Systematic Debugging

> **Provenance:** Adapted from obra/superpowers (MIT).
> Source: <https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md>
> Restructured to match constraint-kit schema; methodology preserved.

## Purpose

A fix that does not address the root cause is not a fix.
It is a delay. Systematic debugging finds the actual cause
before any code is changed.

## When This Skill Is Active

Any time something is broken, behaving unexpectedly, or failing
in a way that is not immediately obvious.

## The Four Phases

### Phase 1 — Reproduce

Before touching any code:
- Can the problem be reproduced reliably?
- What are the exact steps that trigger it?
- What is the exact symptom? (error message, wrong output, hang, crash)
- What environment does it occur in? Does it occur in all environments?

A problem that cannot be reproduced cannot be confirmed fixed.
Do not proceed to Phase 2 until reproduction is reliable.

### Phase 2 — Isolate

Narrow the problem to its smallest reproducible form:
- What is the minimum input / state that triggers the problem?
- Which component, layer, or function is involved?
- When did this start? What changed?

Isolation questions to ask systematically:
- Does the problem occur with all inputs or only specific ones?
- Does the problem occur at a specific time, load, or sequence?
- Can the problem be reproduced in isolation from the rest of the system?

Do not hypothesize causes yet — isolate first.

### Phase 3 — Hypothesize and test

With the problem isolated, form hypotheses:
1. State a specific, falsifiable hypothesis about the cause
2. Identify what evidence would confirm or refute it
3. Make one change to test the hypothesis
4. Observe the result — confirm or rule out
5. Repeat with the next hypothesis

Rules:
- One change at a time — multiple simultaneous changes make causation
  impossible to determine
- If a hypothesis is wrong, revert the change before trying the next one
- Document each hypothesis and result — this prevents cycling back
  to already-ruled-out causes

### Phase 4 — Fix and verify

Once the root cause is confirmed:
- Fix the root cause, not the symptom
- Write a test that would have caught this problem
- Verify the fix in the same environment where the problem was reproduced
- Verify that no regression was introduced

After the fix:
- Document what the root cause was
- Note whether this class of problem could occur elsewhere

## Anti-Patterns

- Do NOT make multiple changes simultaneously — causation cannot
  be established
- Do NOT skip reproduction — "I think I know what it is" leads to
  symptom masking
- Do NOT fix symptoms while leaving the root cause in place
- Do NOT skip writing a regression test after fixing
- Do NOT declare fixed without verifying in the original environment

## Transition

Once fixed and verified:
hand off to `test-driven-development` to write the regression test
if not already written, or to `decision-records` if the root cause
revealed a systemic issue requiring a documented decision.
