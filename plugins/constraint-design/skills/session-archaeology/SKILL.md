---
name: session-archaeology
description: Use when adopting constraint-kit in an existing codebase whose behavior and design cannot be trusted from docs or memory - runs confidence-tagged discovery passes over the code (CodeGraph-assisted), records the evidence in .constraint-kit/ARCHAEOLOGY.md, then produces the same PROJECT.md, GLOSSARY.md, and copilot-instructions files as project-intake, grounded in what the code actually does.
---

# Session Archaeology

Extract a usable picture of an existing repository that has no reliable
documented design — a vibe-coded codebase, inherited legacy code, or
anything where "what does this actually do and why" cannot be answered
by asking a person. Where `project-intake` builds the `.constraint-kit/`
workspace from an *interview* (right for new or early-stage projects),
archaeology builds it from *evidence in the code* — then runs a much
shorter interview for the decisions code cannot answer. Both skills end
at the same place: a cohesive workspace every later skill builds on.

**Announce at start:** "I'm using the session-archaeology skill to
onboard this existing codebase."

## When to use which intake

| Situation | Skill |
|---|---|
| New/empty repo, or code young enough that the user can describe it | `project-intake` |
| Substantial existing code; docs missing, stale, or untrustworthy | `session-archaeology` |
| Archaeology already ran; constraints merely changed | `project-intake` (update mode) |

One archaeology pass per project (or per subsystem chunk). Re-run only
when a new subsystem enters scope or prior evidence is overturned —
revise the existing notes and record what superseded what; never
silently overwrite a prior pass's readings.

## Outputs

All output goes to the target repo's `.constraint-kit/` folder (create
it if missing), plus one generated file in `.github/`:

| File | Content |
|---|---|
| `.constraint-kit/ARCHAEOLOGY.md` | Confidence-tagged evidence: structure, behavior contract, feature inventory, flaw taxonomy, open gaps |
| `.constraint-kit/PROJECT.md` | Same template as `project-intake` — grounded in the evidence |
| `.constraint-kit/GLOSSARY.md` | Domain terms as the *code* uses them, flagged where usage conflicts |
| `.github/copilot-instructions.md` | Same generation rules as `project-intake` |

## Process

### 1. Set up code intelligence

Use the `codegraph-setup` skill to get CodeGraph installed, wired to
this agent surface, and the project indexed. Discovery leans on it: one
`codegraph_explore` call (or `codegraph explore` CLI) returns symbols'
verbatim source, call paths, and blast radius — evidence grep loops
miss, especially dynamic-dispatch hops. If the user declines CodeGraph,
run the same passes with built-in tools and tag caller/impact claims no
higher than `I` (inferred).

### 2. Intake — one question at a time

Ask before any discovery pass; don't interleave questions with
analysis. Each question singly, with your recommended answer. Cover:

1. **Provenance** — can you state how and why this repo was built?
   Sets the mode:
   - **KNOWN** — the user can name the process (vibe-coding sessions, a
     team, a tool). Flaw root causes may cite that process when the
     evidence supports it.
   - **UNKNOWN** — no reliable record. Never infer a development-method
     cause without direct evidence (commit history, comments, style
     consistency). Absent that, root cause reads "unconfirmed" and the
     whole document is marked PROVISIONAL.
2. **Scope** — full repo, or a named subsystem? For large repos prefer
   one pass per subsystem chunk over one context-unbounded pass.
3. **Intent** — what happens to this code next: maintain, extend, or
   replace? (Determines how much the flaw taxonomy matters and whether
   findings become constraints or a rewrite spec.)
4. **Authority** — when evidence is ambiguous about whether a behavior
   is load-bearing or dead cruft, who makes the call? Default: flag as
   an open gap; never decide unilaterally.

Confirm the detected mode explicitly before proceeding.

### 3. Discovery passes

Run in order; each produces a section of `ARCHAEOLOGY.md`. Tag every
finding with confidence:

- **V** — verified: asserted by a passing test or observed at runtime
- **I** — inferred: read from code, not test-covered
- **U** — unconfirmed: best guess, no direct evidence

| Pass | What it establishes | CodeGraph leverage |
|---|---|---|
| 1. Structural inventory | Module boundaries, entry points, dependencies, actual runtime data flow | `codegraph files`; `codegraph explore "<area>"` per area; explore a flow ("how does X reach Y") to get real call paths |
| 2. Behavior contract | Every passing test is verified ground truth, regardless of test quality — tag `V` | Run the suite; `codegraph affected` maps which code each test file actually covers |
| 3. Feature inventory | What each entry point *actually does*, not what its name implies; used vs. dead | Explore from each entry point; a symbol `codegraph callers` finds unreferenced is dead-code evidence (`I`, not proof — check dynamic entry points) |
| 4. Flaw taxonomy | Testability / performance / coupling / duplication / dead code — each with evidence, confidence, root cause per mode | `codegraph impact <symbol>` sizes coupling blast radius; wide impact + no tests = the highest-risk flaws |
| 5. Preserve vs. deprecate | Explicit must-survive list vs. known-cruft list | Evidence from passes 2–4; ambiguous calls go to Open Gaps, not a guess |

Directory structure often reflects commit history, not architecture —
never trust it uncorroborated.

### 4. Write ARCHAEOLOGY.md

```markdown
# Archaeology: <project name>

Pass: <scope> on <date> · Provenance: KNOWN (<how>) | UNKNOWN
Status: CURRENT | PROVISIONAL — revise on new evidence; record what
superseded what.

## Confidence key
V — verified (passing test / observed) · I — inferred (read from
code) · U — unconfirmed (best guess)

## Structural inventory
- <finding> [V/I/U]

## Behavior contract
- <contract item asserted by a passing test> [V]

## Feature inventory
| Entry point | What it actually does | Verdict | Confidence |
|---|---|---|---|
| <entry> | <observed behavior> | Preserve / Deprecate / Open gap | V/I/U |

## Flaw taxonomy
| Flaw | Category | Evidence | Confidence | Root cause |
|---|---|---|---|---|
| <flaw> | <category> | <file:line / impact result> | V/I/U | <cause, or "unconfirmed"> |

## Open gaps
(only what the artifact itself cannot answer — business rationale,
external SLAs, ambiguous preserve/deprecate calls)
- <gap> — needs: <who decides>
```

### 5. Resolve open gaps

Put each gap to the user, one at a time, with your recommended answer.
Move resolved gaps into the section they belong to (with confidence `V`
— the authority answered) and record decisions worth keeping as ADRs
per the `brainstorming` skill's criteria.

### 6. Produce the workspace

Now follow `project-intake` steps 3–5 (PROJECT.md, GLOSSARY.md,
`.github/copilot-instructions.md`) with the facts pre-filled from
`ARCHAEOLOGY.md` — the interview shrinks to the few decisions evidence
didn't settle (purpose, success criteria, working agreement). Ground
rules for the archaeology-fed versions:

- **PROJECT.md** — Stack and Conventions come from the structural
  inventory (state what the code *does*, flag where it is
  inconsistent); Constraints inherit the preserve list ("<behavior>
  must survive — see ARCHAEOLOGY.md") and the worst flaws as guardrails
  ("do not extend <module> without tests; impact radius is N files").
- **GLOSSARY.md** — seed from the names the code actually uses; where
  code and user vocabulary conflict, record both and mark which wins.
- **copilot-instructions.md** — same generation rules as
  `project-intake` (short, imperative, merge-don't-clobber), plus one
  line: "Before modifying unfamiliar code here, read
  `.constraint-kit/ARCHAEOLOGY.md` and query CodeGraph
  (`codegraph_explore`) rather than grepping."

### 7. Confirm and hand off

Show the user all four files and ask for corrections. Then:

> "Onboarding complete. When you're ready to design a change, use the
> `brainstorming` skill — it reads PROJECT.md and ARCHAEOLOGY.md and
> grows the glossary. If the intent is replacement, brainstorm the
> replacement design against the Behavior contract and Preserve list."

## Red flags

- Proceeding on intake answers alone — archaeology requires reading the
  artifact; confirm repo (and test-suite) access first
- Asserting a root cause without direct evidence in UNKNOWN mode
- Treating dead or unreachable code as preserve-worthy because it exists
- Skipping mode confirmation and defaulting to KNOWN-mode assumptions
- One unbounded pass over a large repo instead of subsystem chunks
- Overwriting a prior pass's readings instead of recording the revision
- Treating ARCHAEOLOGY.md as the deliverable — it feeds PROJECT.md and
  the design skills; it is not a substitute for them
- Writing any file outside `.constraint-kit/` and
  `.github/copilot-instructions.md`
