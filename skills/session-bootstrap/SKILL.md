# Skill: Session Bootstrap

## Purpose

Govern scaffold creation and validation for constraint-kit projects.
This skill runs before any preflight or implementation session when
the project scaffold does not yet exist (CREATE mode) or when an
existing scaffold needs to be audited for correctness (VERIFY mode).

Session-bootstrap produces or validates the three files every
constraint-kit project depends on: `.constraint-kit/agent-base.yaml`,
`.constraint-kit/agent-implementer.yaml` (Pattern B only), and
`SESSION_PLAN.md`. It does not govern intake planning or runtime
session behavior — those are owned by `session-preflight` and
`session-hygiene` respectively.

## When This Skill Is Active

At project inception before S01 (CREATE), or at any point when the
scaffold is suspected to be malformed, inconsistent, or incomplete
(VERIFY). Not active during implementation sessions.

## Mode Detection

Detect mode from whether `.constraint-kit/agent-base.yaml` exists
in the project directory.

| Signal | Mode |
|---|---|
| `.constraint-kit/agent-base.yaml` absent | CREATE |
| `.constraint-kit/agent-base.yaml` present | VERIFY |

State the detected mode explicitly and confirm with the user before
proceeding. Offer override once: "Type CREATE or VERIFY to force
mode."

## Intake

Ask all questions before producing any output. Do not interleave
questions with artifact generation.

1. **Project name and repo path** — what is the project name and
   absolute path to the repo root on disk?
2. **Pattern** — are project artifacts living in the target repo
   (Pattern B) or co-located in this workspace's `projects/` (Pattern A)?
   Pattern B → write `agent-implementer.yaml`.
   Pattern A → skip `agent-implementer.yaml`.
3. **AI surface** — which surface will implementation sessions use?
   (`claude-browser`, `claude-code-terminal`, `copilot-vscode`,
   or other)
4. **Environment** — Python version, venv name and path, and any
   non-Python toolchain components (Node, Terraform, Ansible, etc.)
5. **Quality gates** — select from the standard set or provide
   custom commands:
   - Markdown: `markdownlint` / `mdl`
   - Python: `black`, `isort`, `ruff`, `mypy`, `pylint`, `pytest`
6. **Session scope** — how many sessions have been scoped? Provide
   titles and task summaries for each. If scope is unknown, say so
   — the agent will write a single S01 placeholder and ask rather
   than assume.
7. **Done condition** — what does finished look like for this
   project as a whole?

VERIFY mode: questions 1–3 only. The remaining fields are read
from the existing scaffold.

## CREATE Protocol

After all intake answers are received:

1. **Confirm artifact paths.** State where each file will be
   written based on detected pattern. Wait for user confirmation
   before writing anything.

2. **Write `.constraint-kit/agent-base.yaml`.**

```yaml

   schema_version: "0.1.0"
   project: <project-name>
   role: engineer

   environment:
     repo_path: <absolute path>
     venv_activate: source <path>/.venv<version>/bin/activate
     python_version: "<major.minor>"
     toolchain:
       - <tool and version>
     quality_gates:
       - <assembled from intake>

   conventions:
     line_length: 120
     formatter: black
     linter: ruff
     import_sort: isort

   design_decisions: []

   session_plan:
     update_instructions: >
       After each session: update SESSION_PLAN.md (Status, Actual
       effort, Lessons), set Status ready for any newly unblocked
       sessions, and append a session_history entry here.

   session_history: []

```

1. **Write `.constraint-kit/agent-implementer.yaml`** (Pattern B
   only). Populate with the S01 task, constraints, and checklist
   drawn from intake. This file will be overwritten at the start
   of each session — it is always the current session's paste block.

2. **Read `skills/session-hygiene/SKILL.md §7` before writing any
   `SESSION_PLAN.md` paste blocks.** Then write `SESSION_PLAN.md`
   with one `## SXX` block per scoped session. Each block must
   contain:
   - Status, Mode, Estimated effort, Actual effort (blank),
     Depends on, Output, Lessons (blank)
   - A Session Table with a row for every `## SXX` block
   - A fenced `agent-implementer.yaml` paste block with fully
     populated `task:`, `constraints:`, and `checklist:` fields
   - The two mandatory closing checklist items sourced from
     `skills/session-hygiene/SKILL.md §7` — reference that
     section as the authority, do not hardcode the items here

   If session scope was unknown at intake, write a single S01
   placeholder and note that remaining sessions are to be scoped
   during preflight.

3. **Confirm placement.** After writing, state each file path
   and ask the user to confirm files are in place before closing.

## VERIFY Protocol

Read the existing scaffold before producing any output. Do not
write anything until the full report is confirmed.

### Checks

**`agent-base.yaml`**
- `schema_version` present and well-formed
- Required top-level keys present: `project`, `role`, `environment`,
  `session_plan`, `session_history`
- `session_history` entries use `session_id` key (not `session`
  or `id`)
- Dates in `session_history` are `YYYY-MM-DD` format

**`agent-implementer.yaml`** (Pattern B only)
- `schema_version` present
- `extends:` is the bare filename `agent-base.yaml` — **not**
  `.constraint-kit/agent-base.yaml`. `render.py`'s
  `load_agent_with_base()` resolves `extends:` relative to the
  *implementer file's own directory*, not the repo root. Since both
  files live in `.constraint-kit/`, the correct value is the bare
  filename; a `.constraint-kit/`-prefixed value double-nests to
  `.constraint-kit/.constraint-kit/agent-base.yaml` and fails to
  load. Verified against `render.py` directly — this is not a style
  preference.
- Required keys present: `project`, `role`, `mode`, `surface`,
  `task`, `checklist`

**`SESSION_PLAN.md`**
- A Session Table (`| ID | Title | Epics | Status |`) exists —
  its absence is an error, not a warning
- Every `## SXX` block has a corresponding row in the Session
  Table and every Session Table row has a corresponding `## SXX`
  block — no orphans in either direction
- Each `## SXX` block contains an embedded `agent-implementer.yaml`
  fenced block
- Closing hygiene checklist items are present in each paste block
  and consistent with `skills/session-hygiene/SKILL.md §7`

**Internal consistency across files**
- `project` value matches across `agent-base.yaml`,
  `agent-implementer.yaml`, and `SESSION_PLAN.md` header
- `schema_version` matches across both YAML files

### Fix Flow

1. **Report all findings first.** Number each finding, state
   severity (`error` or `warning`), and quote the offending
   content.
2. **Propose corrected content per finding.** Each proposal is
   a fenced block containing the corrected excerpt.
3. **Single confirmation gate.** Ask: "Confirm fixes? State any
   exceptions before I write." Do not write until confirmed.
4. **Write fixes only after confirmation.** If the user rejects
   a specific fix, skip it and note it as unresolved.

## Anti-Patterns

- Writing any artifact before all intake questions are answered
  and artifact paths are confirmed.
- Assuming Pattern A or B without asking explicitly.
- Writing a single S01 placeholder when session scope was provided
  during intake — write all scoped sessions.
- Hardcoding closing hygiene checklist items instead of referencing
  `skills/session-hygiene/SKILL.md §7`.
- Writing `SESSION_PLAN.md` paste blocks before reading
  `skills/session-hygiene/SKILL.md §7`.
- Omitting the Session Table from a newly written `SESSION_PLAN.md`.
- Using `session` or `id` as the key in `session_history` entries
  instead of `session_id`.
- Writing `extends: .constraint-kit/agent-base.yaml` instead of
  the correct bare `extends: agent-base.yaml`. `render.py` resolves
  `extends:` relative to the implementer file's own directory
  (`.constraint-kit/`), so the prefixed form double-nests the path
  and fails to load — verified directly against `render.py`.
- Producing VERIFY fixes before the full findings report is
  complete.
- Writing any fix before the user confirms the batch.
- Reporting a missing Session Table as a warning — it is an error.

## Transition

Do not write any file until intake is complete and artifact paths
are confirmed with the user. In VERIFY mode, do not write any fix
until the full findings report has been produced and the user has
confirmed the fix batch. Hand off to `session-preflight` for
planning once the scaffold is in place. Hand off to
`session-hygiene` for runtime behavior once an implementation
session begins.
