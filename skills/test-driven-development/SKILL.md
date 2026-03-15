# Skill: Test-Driven Development

> **Provenance:** Adapted from obra/superpowers (MIT).
> Source: <https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md>
> Restructured to match constraint-kit schema; methodology preserved.

## Purpose

Tests written after code test what the code does.
Tests written before code define what the code must do.
The difference is not procedural — it is a fundamentally different
relationship between intent and implementation.

## When This Skill Is Active

Any time code is being written or modified.

## The Cycle: RED → GREEN → REFACTOR

### RED — Write a failing test first

- Write one test that describes the next required behavior
- Run it. Confirm it FAILS. A test that passes before code is written
  is not a test — it is noise.
- If the test cannot be run, stop and fix the test infrastructure
  before writing any production code.

### GREEN — Write the minimum code to pass

- Write only enough code to make the failing test pass
- Do not write code for cases not yet covered by a test
- Resist the urge to generalize — YAGNI (You Aren't Gonna Need It)
- Run the test. Confirm it PASSES.

### REFACTOR — Improve without changing behavior

- Clean up the code while all tests remain green
- Extract duplication, improve names, clarify intent
- Run tests again after every refactor step
- Do not add behavior during refactor — that is a new RED step

### Commit at green

Commit after every RED → GREEN → REFACTOR cycle, not after larger chunks.
Small commits mean small rollbacks when something goes wrong.

## What Counts as a Test

- Unit tests covering individual functions or methods
- Integration tests covering interactions between components
- Any automated check that can fail if behavior regresses

Manual verification does not count. "I checked it works" is not a test.

## Code Written Before a Test

If code was written before a test exists for it:
1. Delete the code
2. Write the test
3. Confirm it fails
4. Rewrite the code

This is not punitive — untested code has unknown behavior.
Deleting and restarting takes less time than debugging untested code later.

## Anti-Patterns

- Do NOT write tests after the fact to "cover" code already written
- Do NOT write multiple tests before writing any code
- Do NOT skip the RED step — always confirm the test fails first
- Do NOT write tests that test implementation details instead of behavior
- Do NOT let refactor become feature addition
- Do NOT commit code with failing tests

## Transition

When a feature is complete (all tests green, coverage sufficient):
hand off to `decision-records` if architectural decisions were made,
or to code review if the work is ready for human review.
