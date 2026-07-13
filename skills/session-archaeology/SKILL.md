# Skill: Session Archaeology

## Purpose

Govern extraction of a usable spec from an existing repository that
has no reliable documented design — a vibe-coded codebase, inherited
legacy code, or anything else where "what does this actually do and
why is it built this way" cannot be answered by asking a person.
Produce one artifact: `ARCHAEOLOGY_NOTES.md`, a structured,
confidence-tagged spec-discovery document. This skill runs once per
project, before `session-preflight`'s first GREENFIELD session, and
is not repeated for the same project unless a new archaeology pass is
explicitly requested (e.g. new subsystem in scope, or prior evidence
overturned — see Anti-Patterns).

This skill covers spec-discovery only. Once `ARCHAEOLOGY_NOTES.md`
exists, `session-preflight` takes over — it consumes the notes file
the same way it consumes human intake notes, and produces the actual
`SESSION_PLAN.md` for the greenfield replacement. Runtime session
behavior during the replacement build is governed by
`session-hygiene`, unchanged.

**Divergence from `session-preflight`:** that skill's Artifact
Placement section states "the agent does not read the target repo" —
all context comes from intake questions. This skill inverts that.
Archaeology's entire purpose is reading the repo; intake questions
alone cannot produce `ARCHAEOLOGY_NOTES.md`. Confirm read access
before treating any intake answer as sufficient.

## When This Skill Is Active

At the start of work on any project where an existing repository is
the starting point and no artifact equivalent to `ARCHAEOLOGY_NOTES.md`
or a trustworthy design doc already exists for it — before
`session-preflight` runs its own GREENFIELD detection. Not active for
projects with no existing code (those go straight to
`session-preflight`), and not active again once
`ARCHAEOLOGY_NOTES.md` has been produced for the current scope.

## Mode Detection

Determine mode from the signals below. State the detected mode
explicitly and confirm with the user before proceeding. Mode governs
epistemic discipline, not the discovery passes themselves — both
modes run the same passes (see Discovery Passes).

### KNOWN PROVENANCE

**Signal:** the user can state how the repository was built — e.g.
successive AI-assisted/vibe-coding sessions, a specific team or
process, a known tool's output.

The flaw taxonomy's root-cause column may assert causes tied to that
known process (e.g. "duplication consistent with copy-paste drift
across prompt sessions") when the evidence in the artifact supports
it.

### UNKNOWN PROVENANCE

**Signal:** the user cannot state how or why the repository was
built, or has no reliable record of authorship, tooling, or process.

Do not infer a development-method cause without direct evidence
(commit history, comments, or style consistency that actually
support it). Absent that evidence, the root-cause column reads
"consistent with X, unconfirmed" or is left blank. Confidence tagging
(see Output Artifacts) is mandatory throughout in this mode, and
`ARCHAEOLOGY_NOTES.md` is treated as provisional — readings are
expected to be revised if later evidence overturns them, not treated
as settled on first pass.

## Artifact Placement

Same detection and patterns as `session-preflight` (Pattern A:
co-located `projects/<name>/`; Pattern B: separate external repo).
`ARCHAEOLOGY_NOTES.md` lands alongside where `agent-base.yaml` and
`SESSION_PLAN.md` will later be written — Pattern A:
`projects/<name>/ARCHAEOLOGY_NOTES.md`; Pattern B:
`<repo-root>/ARCHAEOLOGY_NOTES.md`. State the detected pattern and
confirm before writing.

## Intake Protocol

Ask all questions before beginning any discovery pass. Do not
interleave questions with notes generation.

### Questions

1. **Project name and location** — repo name and absolute path on
   disk, same as `session-preflight` Q1.
2. **Provenance** — can you state how and why this repo was built?
   Determines mode (see Mode Detection).
3. **Repo access** — confirm the agent has (or will be given) read
   access to the code, the test suite, any existing docs, and a
   runnable instance if one exists. Do not proceed on intake answers
   alone; this skill requires the artifact itself.
4. **Target language/paradigm** — will the eventual replacement stay
   in the source language/paradigm, or move to a different one? If
   different, name it. Determines whether the Source Implementation
   Notes layer needs explicit "advisory only, translate before use"
   framing (see Output Artifacts).
5. **Scope** — is this a full-repo pass, or bounded to a named
   subsystem? For a large repository, prefer chunking by subsystem
   and running one archaeology pass per chunk rather than one
   context-unbounded pass.
6. **Preserve/deprecate authority** — where the evidence is
   ambiguous about whether a behavior is load-bearing or dead cruft,
   who confirms the call? Default to flagging as an open gap rather
   than the agent deciding unilaterally.

### Outputs per mode

| Mode | Produces |
|---|---|
| KNOWN PROVENANCE | `ARCHAEOLOGY_NOTES.md`, root-cause column populated where evidence supports the known process |
| UNKNOWN PROVENANCE | `ARCHAEOLOGY_NOTES.md`, root-cause column populated only with direct evidence, confidence tags mandatory throughout, marked PROVISIONAL |

## Discovery Passes

Run in order, each producing the corresponding section of
`ARCHAEOLOGY_NOTES.md`:

1. **Structural inventory** — module/package boundaries, entry
   points, external dependencies, actual runtime data flow. Directory
   structure often reflects session/commit history, not architecture
   — do not trust it uncorroborated.
2. **Behavior contract** — every passing test is a fragment of
   verified ground truth, regardless of test quality. Tag confidence
   `V` (verified).
3. **Feature inventory** — trace each entry point to what it actually
   does, not what its name implies. Separate used features from
   dead/unreachable code.
4. **Flaw taxonomy** — for each flaw: category (testability /
   performance / coupling / duplication / dead code), evidence,
   confidence, and root cause per Mode Detection rules above.
5. **Preserve vs. deprecate** — explicit must-survive list vs.
   known-cruft list. Ambiguous calls go to Open Gaps, not a guess.

## Output Artifacts

### ARCHAEOLOGY_NOTES.md

```markdown

# Archaeology Notes: <project-name>

Source: session-archaeology pass over <repo-path> on <date>
Provenance mode: KNOWN | UNKNOWN
Scope: <full repo | named subsystem>
Status: PROVISIONAL — readings may be revised on later evidence

## Confidence Key

- V — verified (asserted directly by a passing test)
- I — inferred (read from code, not test-covered)
- U — unconfirmed (best guess, no direct evidence)

## Design Spec Layer

(portable — this is what session-preflight scopes the replacement
against)

### Structural inventory

- <finding> [confidence]

### Behavior contract

- <contract item> [V]

### Feature inventory

- Preserve: <feature> — <why>
- Deprecate: <feature> — <why, e.g. unreachable>

## Source Implementation Notes

(paradigm-specific — advisory only; if target language/paradigm
differs from source, translate each item to the target's equivalent
concern before writing it into agent-implementer.yaml constraints —
do not copy verbatim)

### Flaw taxonomy

| Flaw | Category | Evidence | Confidence | Root cause |
|---|---|---|---|---|
| <flaw> | <category> | <evidence> | <V/I/U> | <cause, or "unconfirmed"> |

## Open Gaps

(only things genuinely undiscoverable from the artifact itself —
business rationale, external SLAs, ambiguous preserve/deprecate
calls needing a human decision)

- <gap>

```

## Anti-Patterns

- Asserting a root cause without direct evidence in UNKNOWN
  PROVENANCE mode.
- Treating dead or unreachable code as a preserve-worthy requirement
  just because it exists in the repo.
- Copying Source Implementation Notes flaws verbatim into a different
  target language's constraints instead of translating them to that
  paradigm's equivalent concern.
- Proceeding on intake answers alone without confirmed repo access —
  this skill cannot run as a pure Q&A session.
- Overwriting a prior archaeology pass's readings instead of marking
  the revision and what superseded it.
- Treating `ARCHAEOLOGY_NOTES.md` as a finished deliverable in
  itself — it is intake material for `session-preflight`, not a
  substitute for `SESSION_PLAN.md`.
- Skipping provenance-mode confirmation and defaulting to KNOWN
  PROVENANCE assumptions.
- Running one unbounded pass over a large repository instead of
  chunking by subsystem per intake Q5.

## Transition

Do not begin any discovery pass until all intake questions are
answered, repo access is confirmed, and mode is confirmed with the
user. On completion, hand off directly to `session-preflight` in
GREENFIELD mode: `ARCHAEOLOGY_NOTES.md`'s Design Spec Layer supplies
scope and the preserve/deprecate list; the Flaw Taxonomy's root
causes become `agent-implementer.yaml` constraints, translated per
target language/paradigm where Q4 indicated a change; Open Gaps are
surfaced to the user for a decision before `SESSION_PLAN.md` is
produced.
