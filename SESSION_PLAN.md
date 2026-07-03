# SESSION PLAN — ck-docs

## Project Summary

Rewrites constraint-kit documentation as audience-facing Markdown committed
to the constraint-kit repo. Target audience: SRE and DevOps peers who know
context engineering but are new to constraint-kit. Scaffolding produced in
S01; documentation content written in S02–S05.

## Status Key

| Symbol | Meaning |
|--------|---------|
| `ready` | Unblocked, can be opened |
| `blocked` | Depends on incomplete session |
| `in-progress` | Currently open |
| `complete` | Done, artifacts committed |

---

## Epic List

### E1 — Scaffolding
Produce all session scaffolding artifacts before any documentation content
is written. Ensures the project is resumable and constraint-compliant.
- **Done:** All artifacts in `.constraint-kit/` committed. SESSION_PLAN.md
  at repo root. INTAKE_NOTES.md committed as reconstruction brief.
- **Out of scope:** Documentation content.

### E2 — Core Concepts Documentation
Sections 1–3: project identity, what constraint-kit is, skills.
- **Done:** Markdown files committed covering all intake questions for
  Sections 1–3.
- **Out of scope:** Rendering, agent yaml, session lifecycle.

### E3 — Tooling and Artifact Documentation
Sections 4–5: render.py / surface resolution, agent yaml files.
- **Done:** Markdown files committed covering all intake questions for
  Sections 4–5.

### E4 — Workflow and Discipline Documentation
Sections 6–8: supervisor/implementer pattern, SESSION_PLAN.md,
session lifecycle.
- **Done:** Markdown files committed covering all intake questions for
  Sections 6–8.

### E5 — Policy and Reference Documentation
Sections 9–10: artifact commit policy, discipline and workflow.
Includes before/after example (vibe session vs constraint-kit session).
- **Done:** Markdown files committed covering all intake questions for
  Sections 9–10. Before/after example reviewed by supervisor.

---

## Session Table

| ID  | Title                        | Epics | Status   | Depends on |
|-----|------------------------------|-------|----------|------------|
| S01 | Scaffolding                  | E1    | complete | —          |
| S02 | Core concepts                | E2    | ready    | S01        |
| S03 | Tooling and artifacts        | E3    | blocked  | S02        |
| S04 | Workflow and discipline      | E4    | blocked  | S03        |
| S05 | Policy, reference, wrap-up   | E5    | blocked  | S04        |

---

## S01 — Scaffolding

**Surface:** claude-browser (supervisor) + github-copilot (implementer)
**Done condition:** All six scaffolding artifacts exist on disk and are
committed. No documentation content written. Session Table updated to
reflect S01 complete and S02 unblocked.

- Status: complete
- Estimated effort: 1 session
- Actual effort: 1 session (2026-07-03)
- Lessons: validate.py --file only dispatches on skills/, roles/, bundles/ —
  .constraint-kit/ files are out of scope; checklist items updated to use
  python -c parse checks and explicit field-presence reviews instead.
  Artifact filenames use hyphens throughout, consistent with
  session-preflight-skill precedent. Lesson: update SESSION_PLAN.md and
  session_history before git commit, not after.

### Tasks
- [x] `python -c "import yaml; yaml.safe_load(open('.constraint-kit/meta.yaml'))"`
- [x] `python -c "import yaml; yaml.safe_load(open('.constraint-kit/agent-base.yaml'))"`
- [x] `python -c "import yaml; yaml.safe_load(open('.constraint-kit/agent-supervisor.yaml'))"`
- [x] `python -c "import yaml; yaml.safe_load(open('.constraint-kit/agent-implementer.yaml'))"`
- [x] Review `.constraint-kit/meta.yaml`: `bootstrap_type`, `greenfield`, `pattern`, `repo`, `schema_version` present
- [x] Review `.constraint-kit/agent-base.yaml`: `schema_version`, `project`, `environment`, `session_history` entry present
- [x] Review `.constraint-kit/agent-supervisor.yaml`: `extends`, `task`, skill freshness verification step present
- [x] Review `SESSION_PLAN.md`: Session Table present, S01–S05 rows present, each block has embedded `agent-implementer.yaml`
- [x] Review `.constraint-kit/INTAKE_NOTES.md`: Resolved Decisions table present
- [x] Report any issues to supervisor before proceeding
- [x] `git add -A && git commit -m 'S01: scaffolding artifacts' && git push`
- [x] Update `SESSION_PLAN.md` S01 row to complete, S02 to ready
- [x] Append S01 entry to `session_history` in `.constraint-kit/agent-base.yaml`

### agent-implementer.yaml

```yaml
extends: .constraint-kit/agent-base.yaml
schema_version: "0.1.0"
project: ck-docs
role: engineer
mode: generating-doc
target: session-prompt
surface: github-copilot

skills:
  - path: ~/ck-personal/skills/session-preflight/SKILL.md
  - path: ~/ck-personal/skills/session-hygiene/SKILL.md
  - path: ~/ck-personal/skills/session-bootstrap/SKILL.md

task: >
  S01 — Scaffolding verification only. No documentation content written.
  Verify all six artifacts are present and well-formed. Report any issues
  to supervisor before proceeding. Commit and push on clean verification.

constraints:
  - Headless — no interactive fallback loop
  - Do not write documentation content
  - File verification required before commit

checklist:
  # YAML parse checks — confirms files are not malformed, not schema-correct
  - "[ ] python -c \"import yaml; yaml.safe_load(open('.constraint-kit/meta.yaml'))\""
  - "[ ] python -c \"import yaml; yaml.safe_load(open('.constraint-kit/agent-base.yaml'))\""
  - "[ ] python -c \"import yaml; yaml.safe_load(open('.constraint-kit/agent-supervisor.yaml'))\""
  - "[ ] python -c \"import yaml; yaml.safe_load(open('.constraint-kit/agent-implementer.yaml'))\""
  # Field presence review — agent-guided, not automated
  - "[ ] Review .constraint-kit/meta.yaml: bootstrap_type, greenfield, pattern, repo, schema_version present"
  - "[ ] Review .constraint-kit/agent-base.yaml: schema_version, project, environment, session_history entry present"
  - "[ ] Review .constraint-kit/agent-supervisor.yaml: extends, task, skill freshness step present"
  - "[ ] Review SESSION_PLAN.md: Session Table present, S01-S05 rows present, each block has embedded agent-implementer.yaml"
  - "[ ] Review .constraint-kit/INTAKE_NOTES.md: Resolved Decisions table present"
  - "[ ] Report any issues to supervisor before proceeding"
  - "[ ] git add -A"
  - "[ ] git commit -m 'S01: scaffolding artifacts'"
  - "[ ] git push"
  - "[ ] Append S01 summary to session_history in .constraint-kit/agent-base.yaml"
  - "[ ] Update SESSION_PLAN.md: S01 complete, S02 ready"
```

---

## S02 — Core concepts

**Surface:** claude-browser (supervisor) + github-copilot (implementer)
**Done condition:** Markdown files committed to `docs/` covering all intake
questions in Sections 1–3 (project identity, what constraint-kit is,
skills). Supervisor has reviewed each file before commit.

- Status: blocked (S01)
- Estimated effort: 1–2 sessions
- Actual effort:
- Depends on: S01
- Lessons:

### Tasks
- [ ] Write `docs/01-what-is-constraint-kit.md` (Sections 1–2)
- [ ] Write `docs/02-skills.md` (Section 3)
- [ ] Supervisor review of both files
- [ ] Address any recovery specs from supervisor
- [ ] `git add -A && git commit -m 'S02: core concepts docs' && git push`
- [ ] Update SESSION_PLAN.md S02 row to complete, S03 to ready
- [ ] Append S02 entry to `session_history` in `.constraint-kit/agent-base.yaml`

### agent-implementer.yaml

```yaml
extends: .constraint-kit/agent-base.yaml
schema_version: "0.1.0"
project: ck-docs
role: engineer
mode: generating-doc
target: session-prompt
surface: github-copilot

skills:
  - path: ~/ck-personal/skills/session-preflight/SKILL.md
  - path: ~/ck-personal/skills/session-hygiene/SKILL.md
  - path: ~/ck-personal/skills/session-bootstrap/SKILL.md

task: >
  S02 — Write docs/01-what-is-constraint-kit.md covering Sections 1–2
  of INTAKE_NOTES.md (project identity and scope, what constraint-kit is).
  Write docs/02-skills.md covering Section 3 (skills). Each file must
  answer every question listed in its intake section. Audience: SRE/DevOps
  peers who know context engineering but not constraint-kit.
  Do not begin writing until supervisor confirms section assignments.

constraints:
  - Headless — no interactive fallback loop
  - Answer every intake question in the assigned section; none left implicit
  - Do not drift into Sections 4–10 content
  - Submit each file to supervisor for review before committing

checklist:
  - "[ ] Read .constraint-kit/INTAKE_NOTES.md Sections 1–3 in full"
  - "[ ] Confirm section assignments with supervisor before writing"
  - "[ ] Write docs/01-what-is-constraint-kit.md"
  - "[ ] Write docs/02-skills.md"
  - "[ ] Submit both files to supervisor for review"
  - "[ ] Implement any recovery specs from supervisor"
  - "[ ] git add -A"
  - "[ ] git commit -m 'S02: core concepts docs'"
  - "[ ] git push"
  - "[ ] Append S02 summary to session_history in .constraint-kit/agent-base.yaml"
  - "[ ] Update SESSION_PLAN.md: S02 complete, S03 ready"
```

---

## S03 — Tooling and artifacts

**Surface:** claude-browser (supervisor) + github-copilot (implementer)
**Done condition:** Markdown files committed covering all intake questions
in Sections 4–5 (render.py / surface resolution, agent yaml files).
Supervisor reviewed before commit.

- Status: blocked (S02)
- Estimated effort: 1–2 sessions
- Actual effort:
- Depends on: S02
- Lessons:

### Tasks
- [ ] Write `docs/03-rendering-and-surfaces.md` (Section 4)
- [ ] Write `docs/04-agent-yaml-files.md` (Section 5)
- [ ] Supervisor review of both files
- [ ] Address any recovery specs from supervisor
- [ ] `git add -A && git commit -m 'S03: tooling and artifact docs' && git push`
- [ ] Update SESSION_PLAN.md S03 row to complete, S04 to ready
- [ ] Append S03 entry to `session_history` in `.constraint-kit/agent-base.yaml`

### agent-implementer.yaml

```yaml
extends: .constraint-kit/agent-base.yaml
schema_version: "0.1.0"
project: ck-docs
role: engineer
mode: generating-doc
target: session-prompt
surface: github-copilot

skills:
  - path: ~/ck-personal/skills/session-preflight/SKILL.md
  - path: ~/ck-personal/skills/session-hygiene/SKILL.md
  - path: ~/ck-personal/skills/session-bootstrap/SKILL.md

task: >
  S03 — Write docs/03-rendering-and-surfaces.md covering Section 4
  of INTAKE_NOTES.md (rendering and surface resolution). Write
  docs/04-agent-yaml-files.md covering Section 5 (agent yaml files).
  Each file must answer every question listed in its intake section.
  Do not begin writing until supervisor confirms section assignments.

constraints:
  - Headless — no interactive fallback loop
  - Answer every intake question in the assigned section; none left implicit
  - Do not drift into other sections
  - Submit each file to supervisor for review before committing

checklist:
  - "[ ] Read .constraint-kit/INTAKE_NOTES.md Sections 4–5 in full"
  - "[ ] Confirm section assignments with supervisor before writing"
  - "[ ] Write docs/03-rendering-and-surfaces.md"
  - "[ ] Write docs/04-agent-yaml-files.md"
  - "[ ] Submit both files to supervisor for review"
  - "[ ] Implement any recovery specs from supervisor"
  - "[ ] git add -A"
  - "[ ] git commit -m 'S03: tooling and artifact docs'"
  - "[ ] git push"
  - "[ ] Append S03 summary to session_history in .constraint-kit/agent-base.yaml"
  - "[ ] Update SESSION_PLAN.md: S03 complete, S04 ready"
```

---

## S04 — Workflow and discipline

**Surface:** claude-browser (supervisor) + github-copilot (implementer)
**Done condition:** Markdown files committed covering all intake questions
in Sections 6–8 (supervisor/implementer pattern, SESSION_PLAN.md, session
lifecycle). Supervisor reviewed before commit.

- Status: blocked (S03)
- Estimated effort: 1–2 sessions
- Actual effort:
- Depends on: S03
- Lessons:

### Tasks
- [ ] Write `docs/05-supervisor-implementer.md` (Section 6)
- [ ] Write `docs/06-session-plan.md` (Section 7)
- [ ] Write `docs/07-session-lifecycle.md` (Section 8)
- [ ] Supervisor review of all files
- [ ] Address any recovery specs from supervisor
- [ ] `git add -A && git commit -m 'S04: workflow and discipline docs' && git push`
- [ ] Update SESSION_PLAN.md S04 row to complete, S05 to ready
- [ ] Append S04 entry to `session_history` in `.constraint-kit/agent-base.yaml`

### agent-implementer.yaml

```yaml
extends: .constraint-kit/agent-base.yaml
schema_version: "0.1.0"
project: ck-docs
role: engineer
mode: generating-doc
target: session-prompt
surface: github-copilot

skills:
  - path: ~/ck-personal/skills/session-preflight/SKILL.md
  - path: ~/ck-personal/skills/session-hygiene/SKILL.md
  - path: ~/ck-personal/skills/session-bootstrap/SKILL.md

task: >
  S04 — Write docs/05-supervisor-implementer.md covering Section 6
  of INTAKE_NOTES.md. Write docs/06-session-plan.md covering Section 7.
  Write docs/07-session-lifecycle.md covering Section 8. Each file must
  answer every question listed in its intake section.
  Do not begin writing until supervisor confirms section assignments.

constraints:
  - Headless — no interactive fallback loop
  - Answer every intake question in the assigned section; none left implicit
  - Do not drift into other sections
  - Submit each file to supervisor for review before committing

checklist:
  - "[ ] Read .constraint-kit/INTAKE_NOTES.md Sections 6–8 in full"
  - "[ ] Confirm section assignments with supervisor before writing"
  - "[ ] Write docs/05-supervisor-implementer.md"
  - "[ ] Write docs/06-session-plan.md"
  - "[ ] Write docs/07-session-lifecycle.md"
  - "[ ] Submit all files to supervisor for review"
  - "[ ] Implement any recovery specs from supervisor"
  - "[ ] git add -A"
  - "[ ] git commit -m 'S04: workflow and discipline docs'"
  - "[ ] git push"
  - "[ ] Append S04 summary to session_history in .constraint-kit/agent-base.yaml"
  - "[ ] Update SESSION_PLAN.md: S04 complete, S05 ready"
```

---

## S05 — Policy, reference, and wrap-up

**Surface:** claude-browser (supervisor) + github-copilot (implementer)
**Done condition:** Markdown files committed covering all intake questions
in Sections 9–10 (artifact commit policy, discipline and workflow).
Before/after example (vibe session vs constraint-kit session) written and
supervisor-reviewed. All doc files pass supervisor accuracy review against
actual repo artifacts.

- Status: blocked (S04)
- Estimated effort: 1–2 sessions
- Actual effort:
- Depends on: S04
- Lessons:

### Tasks
- [ ] Write `docs/08-artifact-policy.md` (Section 9)
- [ ] Write `docs/09-discipline-and-workflow.md` (Section 10)
- [ ] Write before/after example (vibe vs constraint-kit session)
- [ ] Supervisor final accuracy review across all doc files
- [ ] Address any recovery specs from supervisor
- [ ] `git add -A && git commit -m 'S05: policy, reference, wrap-up' && git push`
- [ ] Update SESSION_PLAN.md S05 row to complete
- [ ] Append S05 entry to `session_history` in `.constraint-kit/agent-base.yaml`

### agent-implementer.yaml

```yaml
extends: .constraint-kit/agent-base.yaml
schema_version: "0.1.0"
project: ck-docs
role: engineer
mode: generating-doc
target: session-prompt
surface: github-copilot

skills:
  - path: ~/ck-personal/skills/session-preflight/SKILL.md
  - path: ~/ck-personal/skills/session-hygiene/SKILL.md
  - path: ~/ck-personal/skills/session-bootstrap/SKILL.md

task: >
  S05 — Write docs/08-artifact-policy.md covering Section 9 of
  INTAKE_NOTES.md. Write docs/09-discipline-and-workflow.md covering
  Section 10. Write a before/after example contrasting a vibe session
  with a constraint-kit session; audience is a skeptical SRE peer.
  Submit all files to supervisor for final accuracy review before commit.

constraints:
  - Headless — no interactive fallback loop
  - Answer every intake question in the assigned section; none left implicit
  - Before/after example must be concrete and specific, not generic
  - Final supervisor accuracy review is required before any commit
  - Do not commit until supervisor sign-off received

checklist:
  - "[ ] Read .constraint-kit/INTAKE_NOTES.md Sections 9–10 in full"
  - "[ ] Confirm section assignments with supervisor before writing"
  - "[ ] Write docs/08-artifact-policy.md"
  - "[ ] Write docs/09-discipline-and-workflow.md"
  - "[ ] Write before/after example"
  - "[ ] Submit all files to supervisor for final accuracy review"
  - "[ ] Implement any recovery specs from supervisor"
  - "[ ] git add -A"
  - "[ ] git commit -m 'S05: policy, reference, wrap-up'"
  - "[ ] git push"
  - "[ ] Append S05 summary to session_history in .constraint-kit/agent-base.yaml"
  - "[ ] Update SESSION_PLAN.md: S05 complete"
```

---

## Skill Gap Backlog

- TODO: session-preflight SKILL.md — add reground/anchor step for RE-PLANNING
  mode and gap-return scenarios (agent reads SESSION_PLAN.md, summarizes
  current state back to user, confirms scope before proceeding).
- TODO: session-hygiene SKILL.md — add scope-creep guard at session open
  (agent states understood scope from agent-implementer.yaml; mid-session,
  flags any topic not in original task and offers to log for future session).
