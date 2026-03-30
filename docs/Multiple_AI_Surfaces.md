# Multi-Surface AI-Assisted Software Development: A Practitioner's Lessons Learned

**Author:** Tim Peiffer
**Date:** March 2026
**Status:** Internal draft — for review and refinement
**Intended audience:** OIT Site Reliability Engineering / constraint-kit community
**Future target:** dev.to practitioner article

## Abstract

This document captures lessons learned from sustained AI-assisted
software development using multiple AI surfaces simultaneously.
The work involved adding new capabilities to existing production
Python codebases — not greenfield projects. The engagement used
GitHub Copilot Chat for in-editor code generation and Claude
(browser) for architecture, constraint management, and recovery.
A purpose-built constraint framework, constraint-kit, provided
model-agnostic context portability across surfaces.

The primary finding is that multi-surface AI assistance, when
managed with explicit session discipline and portable constraints,
produces better outcomes than single-surface approaches for complex
feature work — but requires more deliberate workflow design than
most current guidance suggests. The failure modes are well-defined
and recoverable when detected early. The supervision burden, while
real, can be reduced significantly by using the right surface for
each task type.

## The Problem This Engagement Was Trying to Solve

AI coding assistants are widely available but their reliability
degrades in ways that are not well documented. Single-session
context drift — where an agent progressively ignores constraints
it acknowledged at session start — is a known problem with no good
systematic solution in current tooling. The longer a session runs,
the more supervision is required, which inverts the productivity
gain that motivated using AI assistance in the first place.

A second problem is surface lock-in. Most practitioners use one AI
surface for all tasks — whatever is integrated into their editor.
This is convenient but suboptimal: code generation tools with file
context (Copilot, Cursor) are better for implementation;
browser-based assistants with longer context windows are better for
design, architecture, and recovery. Using the wrong surface for a
task adds unnecessary friction.

The engagement described here attempted to address both problems:
context drift through an explicit portable constraint framework, and
surface lock-in through deliberate surface selection by task type.

## Representative Use Cases

The multi-surface pattern was validated across several distinct
task types. Three representative cases illustrate where it adds
the most value.

### Adding an Observability Feature to an Existing Production Codebase

**Context:** A new cross-cutting capability needs to be added to
multiple existing modules — not as a greenfield class, but wired
consistently into existing call sites, respecting existing patterns,
without disrupting what already works.

**Why multi-surface helps:** The design phase (interface definition,
integration points, configuration schema) benefits from a reasoning
surface with long context. The implementation phase (actual wiring
into each module) benefits from an editor-integrated surface with
direct file access. Attempting both on one surface consistently
produces lower-quality outputs than separating them.

**Where drift hurts most:** Wiring work is highly repetitive across
modules. After the third or fourth repetition, a single-surface
agent begins diverging from the established pattern without
flagging it. The portable constraint document — loaded fresh in
each short session — is what keeps the pattern consistent across
the full set of modules.

**Session structure that worked:**
- Reasoning session (browser): design the interface, produce a
  configuration artifact, record key architectural decisions
- One generating session per module (Copilot): wire one module,
  commit, exit
- Recovery session (browser) if a file was corrupted: reconstruct
  from specification

### Refactoring Shared Infrastructure Under Active Use

**Context:** A shared helper module or library used by multiple
callers needs to be modernized — new patterns introduced, old
patterns deprecated, signatures updated — without breaking the
callers.

**Why multi-surface helps:** Refactoring requires holding two
things simultaneously: the new design intent and the full map of
existing call sites. Browser-based surfaces with long context
windows are better suited to the analysis and decision phases.
The implementation of individual callsite updates is mechanical
and benefits from file-context tools.

**Where drift hurts most:** A long single-surface session attempting
both analysis and implementation typically produces an agent that
has partially lost the original analysis by the time it is writing
the tenth callsite update. Decisions made in the reasoning phase
get re-litigated mid-implementation.

**Session structure that worked:**
- Reasoning session (browser): inventory call sites, identify
  breaking changes, record decisions about deprecation path
- Generating sessions (Copilot): one callsite update per session,
  with the decision record loaded via the constraint document
- Final reasoning session (browser): verify consistency across
  the full set of changes before opening the pull request

### Incident Response Runbook Authoring

**Context:** A novel incident type has occurred. A new runbook needs
to be authored quickly — drawing on system knowledge, existing
runbook patterns, and the incident timeline — and validated against
the existing runbook corpus before use.

**Why multi-surface helps:** The authoring task has two distinct
phases that require different capabilities. The synthesis phase —
extracting lessons from the incident, mapping them to runbook
structure, identifying gaps — requires broad context and reasoning.
The generation phase — producing well-formed runbook YAML or
Markdown against an established schema — requires precision and
compliance checking.

**Where drift hurts most:** An agent asked to do both in one session
tends to produce runbooks that look correct but contain subtle
schema violations or deviations from established step patterns that
only become visible when the runbook is exercised. Separating
synthesis from generation, with a checkpoint between, produces
more reliable output.

**Session structure that worked:**
- Reasoning session (browser): review incident timeline, identify
  key steps and decision points, map to runbook section structure
- Generating session (Copilot or browser): produce the runbook
  against the schema, with the session starter loaded from the
  constraint document
- Review session (browser): compare the new runbook against two
  or three existing runbooks for pattern consistency

## The Two-Surface Architecture

**Claude (browser):** Architecture design, constraint management,
decision record generation, session starter creation, recovery
specifications, cross-session continuity, this document.

**GitHub Copilot Chat (VS Code):** In-editor code generation with
`#file` references to actual source files, incremental method
implementation, targeted file wiring.

**The binding layer:** constraint-kit — a purpose-built framework
providing a portable `agent.yaml` project config that renders
model-agnostic session starters. The same constraint document
worked whether the session was in Copilot Chat, Claude browser,
or Gemini.

## What Worked

### Separating Design from Implementation

The most productive sessions were those with a clear single purpose.
Reasoning sessions (design, architecture, decision-making) used
`mode: collaborating` and `mode: reasoning` in the constraint-kit
config. Generating sessions used `mode: generating-code`. The
mode boundary was a forcing function — it prevented the agent from
jumping to implementation before the design was confirmed.

The most effective pattern: read the relevant files, produce an
inventory or analysis artifact, confirm the artifact, then begin
implementation. Each step confirmed before the next began. Artifacts
produced this way rarely required structural changes during
implementation.

### Decision Records as Cross-Session Memory

Architectural decisions made through structured reasoning before
any code is written should be recorded in a format that captures
context, the decision, consequences, and a review trigger. When
later sessions introduce contradictory proposals, the decision
records provide a reliable reference. Without them, the agent
re-litigates settled questions in every session.

### Asking Questions Before Proposing Changes

A consistent pattern that caught problems early: before any
implementation code was proposed, the agent was asked to read the
actual files and answer specific questions about signatures, call
patterns, and where variables were defined. This caught significant
design mismatches — assumed interfaces that differed from the actual
implementation — before they became bugs.

The question sequence was: "Read these files. Answer these specific
questions. Do not propose any changes until I confirm your answers."
This is a simple discipline that consistently prevented wasted effort.

### Tools for Mechanics, Agent for Logic

`ruff check --fix`, `isort`, `pycompliance.py`, and `py_compile`
handled all formatting, import ordering, and compliance issues.
Asking the agent to fix these was consistently less reliable and
more time-consuming than running the tools directly. The agent was
used for logic, design, and generation. The tools were used for
verification and mechanical correction.

### Short Sessions, Commit Between

Sessions focused on one file or one function, with a git commit
after each clean verification. When a session produced a corrupted
file, the recovery path was always clear: restore from the last
commit or rebuild from specification. Sessions without commit
checkpoints had no clean recovery point.

## What Failed

### Context Drift in Long Generating Sessions

The most significant recurring failure. After approximately 90
minutes of generating-code work, agents began violating constraints
they had acknowledged at session start. Observed patterns:

- Import ordering violations placed above module docstrings after
  being corrected multiple times in the same session
- Methods presented as "additions only" that deleted existing content
- File changes reported as no-ops while actually modifying the file
- Correct code replaced with non-compliant code when asked to fix
  a different issue

The critical characteristic: the agent did not self-identify drift.
It continued to claim compliance while producing non-compliant
output. Detection required the human to verify against the
constraint document, not the agent to flag its own failures.

**Implication:** Session length limits are a safety mechanism, not
a preference. 90 minutes appears to be a practical ceiling for
generating sessions on complex code. Longer sessions require
increasingly close supervision that defeats the productivity gain.

### The Iterative Patching Anti-Pattern

The initial approach to wiring changes into existing files was
incremental patching — one section at a time, show the diff,
confirm, write. This produced accumulated indentation errors,
deleted content, and corrupted files. The supervision overhead
was high and the error rate increased with each patch.

The replacement approach — write the complete correct function,
verify syntax before applying, apply in one operation — was faster,
produced no corruption, and required less supervision. The lesson:
for well-specified mechanical work on existing files, write it
yourself and use the agent to review, rather than supervising the
agent to write it.

### File Corruption and Recovery

Files were corrupted during generating sessions: once by incremental
method building over a long session, once by an agent applying
patches while claiming to make no changes. In both cases, recovery
required the browser surface — the recovery task required holding
the full design context across multiple sessions, which benefited
from the longer context window.

The recovery pattern that worked: delete the corrupted file, write
a complete precise specification, give it to a fresh agent, verify
syntax output with `py_compile` and `ruff check`. When the
specification is sufficiently precise, a fresh agent produces a
correct file on the first attempt. The specification, not the
corrupted file, is the source of truth.

This recovery path requires that the specification exists before
recovery is needed. Reasoning sessions that produce no durable
artifacts leave no recovery path.

### Cross-Session Context Loss

Information established in one session and not recorded is
permanently lost. The agent has no memory across sessions. Design
decisions, agreed-upon patterns, and constraints exist only in the
session where they were stated. Without the constraint document
re-injected at the start of each session, every session starts
from scratch.

The failure mode: a later session proposes changes that contradict
earlier decisions, with no way to detect the contradiction without
maintaining the decision record externally. The constraint layer
is not optional overhead — it is the only mechanism preventing
cross-session context loss.

### The Supervision Paradox

The engagement surfaced a fundamental tension in AI-assisted
development: the tasks that most benefit from AI assistance (large,
complex, multi-file changes) are also the tasks most vulnerable to
drift and corruption. Small, well-specified tasks can be done with
less supervision but could often be done directly by the developer
in less time than supervising the agent.

There is a sweet spot — tasks that are medium-sized, well-specified,
and benefit from the agent's ability to generate code faster than
typing — where AI assistance clearly adds value. Outside that sweet
spot, the supervision overhead approaches or exceeds the time saved.

## The Multi-Surface Pattern

### Surface Selection by Task Type

| Task type | Best surface | Reason |
|---|---|---|
| Architecture and design | Browser (Claude/Gemini) | Longer context, reasoning |
| Decision exploration | Browser (Claude/Gemini) | Structured dialogue |
| Code generation | Copilot Chat (VS Code) | File context via `#file` |
| Recovery and reconstruction | Browser (Claude) | Cross-session continuity |
| Mechanical fixes | Tools (ruff, isort, pycompliance) | More reliable than any agent |
| Verification | Tools (py_compile, ruff check) | Deterministic |

### The Constraint Layer

The constraint layer is what makes multi-surface work tractable.
Without a portable constraint document, switching surfaces means
re-establishing context from scratch. The constraint-kit `agent.yaml`
rendered a session starter that worked in any surface — the same
architectural context, decision history, and behavioral constraints
loaded into each new session regardless of which surface it was on.

### Session Boundaries as Safety Gates

Each session had explicit entry and exit conditions:

**Entry:** Update `agent.yaml` (task, mode, session history),
re-render session starter, open new session, paste starter,
reference files.

**Exit:** End session explicitly, commit clean files, update
`agent.yaml` session history, re-render for next session.

The re-render between sessions was not overhead — it was the
mechanism that prevented context from the previous session's
failures from contaminating the next session.

## Observations on Surface Capabilities

### Context Drift Detection

No AI surface reliably detects its own context drift. This is a
fundamental limitation — a drifted model cannot reliably evaluate
its own drift. Detection requires the human to verify against an
external reference (the constraint document, the session starter,
the decision records). This is one reason why constraint-kit's
mandatory checkpoint behavior ("do not proceed without explicit
confirmation") matters — it creates natural verification points
rather than relying on the agent to self-assess.

### Recovery Capability

Browser assistants with long context windows (Claude in particular)
have a meaningful advantage for recovery tasks. Reconstructing a
corrupted file from a specification requires holding the full design
history in context simultaneously. The single-spec recovery pattern —
write a complete precise specification, give it to a fresh agent,
verify the output — worked reliably when the specification was
sufficiently precise.

### File Context

Copilot Chat's `#file` reference system is a genuine advantage for
implementation work. Reading actual source code is more reliable
than reading pasted excerpts. The practical limit appeared to be
4-5 files before context truncation affected response quality. For
sessions requiring more context, reducing the file list to the most
directly relevant files produced better results than attempting to
load everything.

## Recommendations

**For teams adopting AI-assisted development:**

1. **Establish session length limits.** 90 minutes for generating
   sessions. Longer sessions require increasing supervision that
   approaches zero net productivity gain.

2. **Commit between sessions, not within them.** Each session should
   produce one committed artifact. Mid-session commits create
   ambiguous recovery points.

3. **Use tools for mechanical work.** `ruff --fix`, `isort`,
   `py_compile` are more reliable than any agent for formatting,
   import ordering, and syntax validation. Run them after every write.

4. **Separate design from implementation.** Reasoning sessions
   should produce no code. Generating sessions should start from
   confirmed designs. The temptation to do both in one session
   consistently produces worse outcomes than doing them separately.

5. **Ask questions before proposing changes.** For any session
   involving an existing codebase, require the agent to demonstrate
   it has read and understood the relevant files before proposing
   changes. This single discipline catches the majority of
   design-to-implementation mismatches.

6. **Write it yourself when the specification is complete.** For
   well-specified mechanical work on existing files, the
   write-then-review pattern is more productive than the
   supervise-while-writing pattern. The agent's value shifts from
   generation to verification.

7. **Build a portable constraint layer.** Whether using constraint-kit
   or another approach, the constraint document needs to survive
   surface switches. Re-establishing context manually at every
   session start is a significant overhead that compounds over a
   long engagement.

## Open Questions

These questions emerged from the engagement and are not yet answered:

**Is 90 minutes the right session length limit, or is it
model-specific?** Different models may have different drift
characteristics. Systematic measurement would be needed to establish
reliable limits per model and task type.

**Would formal multi-agent orchestration (Claude, Gemini, agentic
frameworks) reduce the supervision burden?** The multi-surface
pattern described here was manual — a human coordinating between
surfaces. Automated orchestration might handle some of the
coordination, but the fundamental drift problem likely persists
regardless of orchestration layer.

**How does team size affect this pattern?** This engagement was a
solo operation. Multiple developers using the same constraint layer
would introduce coordination questions: who updates the session
history, how are decision records reviewed, how are conflicts in
the constraint document resolved?

**When is AI assistance counterproductive?** The supervision paradox
suggests there is a class of tasks where AI assistance adds negative
value. Characterizing that class more precisely would help teams
allocate AI assistance to where it actually adds value.

## What to Develop Next

This document reflects one practitioner's sustained engagement with
the multi-surface pattern. Before it is ready for a broader
practitioner audience, it would benefit from input across task types,
team contexts, and codebases that look nothing like the one described
here.

**Specific questions for colleagues:**

- Have you used a similar surface-separation pattern, even
  informally? What held up and what did not?
- Is 90 minutes recognizable as a drift threshold, or have you
  observed different breakpoints with different models or task types?
- What does your recovery path look like when an agent corrupts a
  file? Is the constraint layer the missing piece, or something else?
- For teams larger than one: how do you maintain shared context
  across developers in an AI-assisted workflow?

Contributions in the form of annotated session logs, additional
use case sketches, or counter-examples where the pattern failed
would significantly strengthen the recommendations.

## Related Work

- constraint-kit: https://github.com/\<handle\>/constraint-kit
- obra/superpowers: https://github.com/obra/superpowers
- HOW_TO_USE_GITHUB.md — constraint-kit technical path
- HOW_TO_USE_DRIVE.md — constraint-kit non-technical path
