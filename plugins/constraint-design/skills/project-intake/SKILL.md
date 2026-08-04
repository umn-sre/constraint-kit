---
name: project-intake
description: Use at the start of a new project or when adopting constraint-kit in an existing repo - interviews the user about goals, stack, and conventions, explores the codebase, then writes the .constraint-kit/ workspace and generates .github/copilot-instructions.md so constraints persist across every session.
---

# Project Intake

Establish the project's constraints once, on disk, so no session ever has
to rediscover them. AI assistants drift: rules given at the start of a
session are forgotten by the middle. The fix is structural — keep the
rules in files the assistant re-reads, not in conversation memory. This
skill creates those files.

**Announce at start:** "I'm using the project-intake skill to set up this
project's constraints."

## Outputs

All output goes to the target repo's `.constraint-kit/` folder (create it
if missing), plus one generated file in `.github/`:

| File | Content |
|---|---|
| `.constraint-kit/PROJECT.md` | Goals, audience, stack, conventions, constraints, working agreement |
| `.constraint-kit/GLOSSARY.md` | Seed domain glossary (grow it during brainstorming) |
| `.github/copilot-instructions.md` | Generated repo-wide Copilot instructions distilled from PROJECT.md |

## Process

### 1. Explore before asking

Look up every *fact* you can from the environment first — languages,
frameworks, package manager, test runner, lint config, CI, directory
conventions, existing docs. Never ask the user something the repo can
answer. If `.github/copilot-instructions.md` or `.constraint-kit/` already
exists, read it — you are updating, not starting over.

### 2. Interview — one question at a time

The *decisions* are the user's. Put each one to them singly, with your
recommended answer, and wait for the reply before continuing. Prefer
multiple choice where possible. Cover, in order:

1. **Purpose** — what is this project for, and for whom?
2. **Success** — what does "working" mean? How is it verified?
3. **Scope boundaries** — what is explicitly out of scope?
4. **Conventions** — code style, naming, commit style, branch strategy
   (confirm what you inferred from the repo rather than asking open-ended).
5. **Process** — TDD expected? Review required before merge? What may the
   assistant do without asking, and where are the checkpoints it must not
   pass without explicit confirmation?
6. **Domain language** — the handful of terms that must be used precisely.

Stop interviewing when new answers stop changing what you would write.

### 3. Write PROJECT.md

```markdown
# <Project name>

## Purpose
<what and for whom — 2-3 sentences>

## Success criteria
<how "working" is verified: tests, builds, review gates>

## Stack
<languages, frameworks, tooling — with versions where they matter>

## Conventions
<style, naming, commits, branching — one line each, exact values>

## Constraints
<hard rules: what must always / never happen>

## Working agreement
<what the assistant may do unprompted; checkpoints requiring explicit
confirmation; TDD and review expectations>

## Out of scope
<explicit exclusions>
```

### 4. Seed GLOSSARY.md

One entry per confirmed term:

```markdown
# Glossary

**<Term>** — <one-sentence definition>. Avoid: <rejected synonyms>.
```

### 5. Generate .github/copilot-instructions.md

Distill PROJECT.md into repo-wide custom instructions. Rules for the
generated file:

- Short — aim for under 60 lines. Instructions are injected into every
  Copilot request; bloat dilutes them.
- Imperative, testable statements ("Run `pnpm test` before claiming a task
  complete"), not aspirations ("write good code").
- Include: build/test/lint commands, the conventions and constraints with
  exact values, the working agreement, and a pointer to
  `.constraint-kit/PROJECT.md` and `.constraint-kit/GLOSSARY.md` for the
  full context.
- Include this line so future sessions maintain the loop: "Planning
  artifacts (specs, plans, decision records) live in `.constraint-kit/`;
  read the relevant ones before starting work there."
- If the file already exists, merge — preserve user-authored sections and
  never silently delete rules you did not write.

### 6. Confirm

Show the user the three files and ask for corrections. Apply them, then
point at the next step:

> "Intake complete. When you're ready to design a feature, use the
> `brainstorming` skill — it builds on PROJECT.md and grows the glossary."

## Red flags

- Asking the user facts the repo already answers
- Multiple questions in one message
- A copilot-instructions file full of generic advice no linter could check
- Writing any file outside `.constraint-kit/` and `.github/copilot-instructions.md`
