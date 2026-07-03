# Intake Notes — constraint-kit Documentation Rewrite
<!-- bootstrap-type: reconstruction -->
<!-- project-state: scaffolding artifacts committed in S01 -->
<!-- preflight-mode: HYBRID RECONSTRUCTION — work has occurred but session ledger was missing -->
<!-- generated: 2026-06-17 -->
<!-- resolved: 2026-07-03 — all blocking gaps closed, S01 artifacts produced -->

---

## Status

QC Drill has been run against these notes. All blocking gaps are closed.
Recoverable gaps are resolved. S01 scaffolding artifacts are committed.

---

## Resolved Decisions

| Question | Answer |
|---|---|
| Repo path | `~/constraint-kit` |
| Pattern A or B | Pattern A — artifacts live in `.constraint-kit/` at repo root |
| Target audience | SRE and DevOps peers; context engineering is familiar, constraint-kit is the unknown |
| Output format | Markdown committed to the repo under `docs/` |
| Surfaces | Dual surface — Claude browser (supervisor) + GitHub Copilot (implementer) |
| Update contract | Skill schema changes invalidate skill structure sections; agent yaml schema changes invalidate agent yaml sections; enforced via session-preflight checklist item |
| Minimum committed artifact set | `agent-base.yaml`, `SESSION_PLAN.md`, `meta.yaml`, `INTAKE_NOTES.md` |
| Prior state of agent-base.yaml | Non-existent — true greenfield on the scaffolding |
| Session ledger format | `session_id`, `date`, `surface`, `tasks_completed`, `tasks_carried_forward`, `budget_consumed_estimate`, `summary` |
| meta.yaml reconstruction flag | `bootstrap_type: reconstruction`, `greenfield: false` |
| SESSION_PLAN.md horizon | S01–S05 |
| Schema version | `0.1.0` |
| Artifact directory | `.constraint-kit/` at repo root |
| Copilot skill resolution | Absolute paths in `agent-implementer.yaml` from `~/ck-personal/skills/` |
| Supervisor render freshness | Re-render immediately before each session open; verify injected skill blocks before proceeding |
| SESSION_PLAN.md location | Repo root (`~/constraint-kit/SESSION_PLAN.md`) |

---

## S01 Scope Commitment

The first session produces scaffolding artifacts only. No documentation content is written.

Surfaces: Claude browser (supervisor) + GitHub Copilot (implementer).

Deliverables:
- `.constraint-kit/meta.yaml`
- `.constraint-kit/agent-base.yaml`
- `.constraint-kit/agent-supervisor.yaml`
- `.constraint-kit/agent-implementer.yaml`
- `SESSION_PLAN.md`
- `.constraint-kit/INTAKE_NOTES.md`

Nothing else. If scope creep toward doc content occurs in S01, it is a session hygiene failure.

Note: Copilot operates headlessly with no interactive fallback loop. Skill resolution
paths in `agent-implementer.yaml` are a blocking S01 requirement, not optional.

---

## Section Coverage (S02–S05)

| Session | Sections | Doc files |
|---|---|---|
| S02 | 1–3 (identity, what it is, skills) | `docs/01-what-is-constraint-kit.md`, `docs/02-skills.md` |
| S03 | 4–5 (rendering, agent yaml) | `docs/03-rendering-and-surfaces.md`, `docs/04-agent-yaml-files.md` |
| S04 | 6–8 (supervisor/implementer, SESSION_PLAN, lifecycle) | `docs/05-supervisor-implementer.md`, `docs/06-session-plan.md`, `docs/07-session-lifecycle.md` |
| S05 | 9–10 (commit policy, discipline) + before/after example | `docs/08-artifact-policy.md`, `docs/09-discipline-and-workflow.md` |
