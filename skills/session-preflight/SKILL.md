# Skill: Session Preflight

## Purpose

Govern project intake and planning before any implementation session
begins. Produce the two artifacts every implementation session
depends on: `agent-base.yaml` (persistent project ledger) and
`SESSION_PLAN.md` (session sequence with paste-ready implementer
blocks). This skill runs once per project at inception and again
whenever scope or environment changes require replanning.

This skill covers intake only. Runtime session behavior — loop
detection, file verification, wrap-up protocol — is governed by
`session-hygiene`.

## When This Skill Is Active

At the start of S01 for any new project (GREENFIELD), at the start
of a replanning session when scope changes (RE-PLANNING), or when
the environment has drifted since the last session (ENVIRONMENT
DRIFT). This skill is not active during implementation sessions.

## Mode Detection

Determine mode from the signals below. State the detected mode
explicitly and confirm with the user before proceeding.

### GREENFIELD

**Signal:** No `agent-base.yaml` exists under
`.constraint-kit/` in the project directory.

S01 is always a planning session. Produce both `agent-base.yaml`
and `SESSION_PLAN.md` from scratch. All sessions are drafted
through to the done condition before the session closes.

### RE-PLANNING

**Signal:** `agent-base.yaml` exists and `session_history`
contains at least one entry. No environment changes reported.

Prior history is the foundation — do not overwrite it. Read the
existing `SESSION_PLAN.md` and `session_history` before producing
anything. Add new session entries only. Revise incomplete or
blocked entries in place, noting the revision date.

### ENVIRONMENT DRIFT

**Signal:** `agent-base.yaml` exists but the user reports that
the Python version, venv, toolchain, or key dependencies have
changed since the last session.

Explicitly ask what changed before producing any output. Do not
assume the scope of the drift. Produce an updated `environment:`
block in `agent-base.yaml` and revised quality gate commands in
all remaining SESSION_PLAN.md paste blocks.

## Artifact Placement

Detect pattern from the project path provided by the user.

- **Pattern A** — project lives co-located inside this constraint-kit
  workspace's own `projects/<name>/` directory (used by personal or
  team extension repos that host multiple projects side by side).
  Artifacts live at `projects/<name>/.constraint-kit/agent-base.yaml`
  and `projects/<name>/SESSION_PLAN.md`.
- **Pattern B** — project is a separate external repo entirely.
  Artifacts live at `<repo-root>/.constraint-kit/agent-base.yaml`
  and `<repo-root>/SESSION_PLAN.md`.

State the detected pattern and confirm before writing any files.

Note: the agent does not read the target repo. All environment
paths, project structure, and quality gate commands must be
surfaced through intake questions.

## Intake Protocol

Ask all questions before producing any output. Do not interleave
questions with artifact generation.

### Questions

1. **Project name and location** — what is the repo name and
   absolute path on disk?
2. **AI surface** — which surface will implementation sessions
   use? (`claude-browser`, `claude-code-terminal`,
   `copilot-vscode`, or other)

   The detected surface determines the render `target:` for every
   paste block — do not default to `session-prompt` regardless of
   surface:
   - `claude-browser`, `claude-code-terminal`, `chatgpt-browser`,
     `gemini-browser` (browser-chat or agentic-cli interfaces,
     per `registries/surface-registry.yaml`) → `target: session-prompt`
   - `copilot-vscode` (`ide-chat` interface) → `target:
     copilot-instructions`, since `render.py` has a dedicated
     target for that surface
   - Unrecognized surface → ask the user which render target
     applies rather than assuming `session-prompt`
3. **Done condition** — what does finished look like? What is
   the acceptance criterion for the project as a whole?
4. **Environment** — Python version, venv name/path, and any
   non-Python toolchain components (Node, Terraform, Ansible, etc.)
5. **Quality gates** — select from the standard set or provide
   custom commands:
   - Markdown: `markdownlint` / `mdl`
   - Python: `black`, `isort`, `ruff`, `mypy`, `pylint`, `pytest`

   Agent assembles selected commands into the quality gate
   checklist line in every paste block.
6. **Environment drift check** (RE-PLANNING and ENVIRONMENT DRIFT
   modes only) — has anything changed since the last session?
   Python version, venv, dependencies, toolchain?

### Outputs per mode

| Mode | Produces |
|---|---|
| GREENFIELD | `agent-base.yaml` (full), `SESSION_PLAN.md` (all sessions) |
| RE-PLANNING | New/revised `SESSION_PLAN.md` entries only |
| ENVIRONMENT DRIFT | Updated `environment:` block, revised paste blocks |

## Output Artifacts

### agent-base.yaml

```yaml

schema_version: "0.1.0"
project: <project-name>
role: engineer

environment:
  repo_path: <absolute path to repo root>
  venv_activate: source <path>/.venv<version>/bin/activate
  python_version: "<major.minor>"
  toolchain:
    - <tool and version if relevant>
  quality_gates:
    - <assembled from intake question 5>

conventions:
  line_length: 120
  formatter: black
  linter: ruff
  import_sort: isort
  # extend as needed

design_decisions: []

session_plan:
  update_instructions: >
    After each session: update SESSION_PLAN.md (Status, Actual effort,
    Lessons), set Status ready for any newly unblocked sessions, and
    append a session_history entry here.

session_history: []

```

### SESSION_PLAN.md

```markdown

# Session plan: <project-name>

Source of truth for the session sequence. Each entry defines one
agent session. The `### agent-implementer.yaml` block under each
session is paste-ready — copy the entire fenced block and replace
the contents of `.constraint-kit/agent-implementer.yaml` to start
that session.

After each session completes:

1. Update `Actual effort` and add a `Lessons` bullet in this file
2. Add a `session_history` entry in `agent-base.yaml`
3. Update the session `Status` to `complete`

## Status key

- `complete` — session finished, output committed
- `ready` — prerequisites met, paste block ready to use
- `blocked` — waiting on a prior session
- `draft` — task definition needs refinement before running

## S01 — <title>

- Status: ready
- Mode: generating-code | generating-doc | collaborating
- Estimated effort: 1 session
- Actual effort: (fill after session)
- Depends on: none
- Output: (files created or modified)
- Lessons: (fill after session)

### agent-implementer.yaml

​```yaml
extends: agent-base.yaml
schema_version: "0.1.0"
project: <project-name>
role: engineer
mode: generating-code
target: session-prompt  # see Intake Protocol Q2 — set per detected surface, not always session-prompt
surface: <surface>

task: >
  <scoped task description>

constraints:
  - Read <key files> before writing any code
  - <hard constraints>

checklist:
  - "[ ] Read <key files> in full before writing"
  - "[ ] <implementation steps>"
  - "[ ] Run quality gates: <assembled commands> — must pass clean"
  - "[ ] Update SESSION_PLAN.md: set Status complete, fill
        Actual effort, add Lessons if applicable, set Status
        ready for any newly unblocked sessions"
  - "[ ] Append session summary to session_history in
        .constraint-kit/agent-base.yaml"
​```

```

The final two checklist items are mandatory in every session block.
Do not omit them.

## Anti-Patterns

- Producing `agent-base.yaml` or `SESSION_PLAN.md` before all
  intake questions are answered.
- Overwriting `session_history` entries in RE-PLANNING mode.
- Assuming environment details — always surface them through intake.
- Producing a partial `SESSION_PLAN.md` that does not cover all
  sessions through the done condition (GREENFIELD mode).
- Omitting the two mandatory closing checklist items from any
  paste block.
- Omitting quality gate commands from paste blocks, or using
  generic placeholders instead of the commands selected in intake.
- Skipping the pattern detection step and hardcoding artifact
  paths without confirmation.
- Beginning artifact generation before mode is confirmed with
  the user.

## Transition

Do not produce any artifact until all intake questions are answered
and the detected mode is confirmed. On browser surfaces, deliver
artifacts as proposed content — the user applies them to disk
manually. On file-access surfaces, write directly and confirm
placement with the user before committing. Hand off to
`session-hygiene` for all runtime behavior once the first
implementation session begins.
