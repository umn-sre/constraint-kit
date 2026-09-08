# speckit-agent and constraint-kit Integration Design

Date: 2026-09-05
Status: Proposed

## Purpose

Define how HEAT's `speckit-agent` framework and UMN SRE's `constraint-kit`
workflow can co-exist without merging their responsibilities or creating
conflicting agent instructions.

The goal is composition by explicit handoff contract:

- `speckit-agent` remains the domain-specific governance workflow for the Hybrid
  Enterprise Architecture Team (HEAT).
- `constraint-kit` remains the reusable workflow-discipline toolkit for planning,
  implementation, review, session hygiene, security principles, and UMN
  compliance.
- A small bridge defines routing, artifact ownership, conflict precedence, and
  handoff points between the two.

## Context

`speckit-agent` is HEAT's GitHub Copilot agent framework. It provides a
constitution-driven workflow for feature delivery, small fixes, exploratory work,
roadmaps, in-flight collaboration claims, and one-repository-per-spec governance.

Its primary workflow is:

```text
/speckit.specify -> /speckit.clarify -> /speckit.plan ->
/speckit.tasks -> /speckit.implement
```

It also provides:

- a `speckit` concierge agent for request classification
- optional `/speckit.roadmap` project-repository workflow
- `/speckit.fix` for bounded corrections
- `.specify/` templates, scripts, roadmaps, claims, and constitution state
- always-on HEAT governance in `.github/copilot-instructions.md`

`constraint-kit` is a plugin marketplace for disciplined Copilot workflows. Its
main workflow is:

```text
project-intake or project-archaeology -> brainstorming -> writing-specs ->
writing-plans -> subagent-driven-development or executing-plans ->
finishing-a-development-branch
```

It provides:

- `constraint-design` for intake, archaeology, brainstorming, specs, and plans
- `constraint-dev` for TDD, subagent-driven execution, reviews, session ledger,
  security principles, and branch finishing
- `umn-compliance` for UMN-only compliance analysis
- persistent project context in `docs/`, `docs/constraint-kit/`,
  `.github/copilot-instructions.md`, and `.constraint-kit/sdd/`

The frameworks overlap in lifecycle shape. They should not both own the same
phase for the same work item.

## Design Principle

One framework is the workflow router at a time.

When a request is HEAT-governed, `speckit-agent` should usually be the front door.
When a request is not HEAT-governed, `constraint-kit` should usually be the front
door. The other framework can participate only at a documented handoff point.

Do not install or invoke both frameworks as competing always-on authorities for
the same phase.

## Ownership Boundaries

| Concern | Owner | Notes |
|---|---|---|
| HEAT constitution | `speckit-agent` | HEAT-specific governance, principles, and technology defaults. |
| Request classification for HEAT work | `speckit-agent` | The `speckit` concierge routes to roadmap, feature, fix, or exploration. |
| HEAT roadmap/project-repository model | `speckit-agent` | Includes project repositories, roadmap pointers, and one-repository-per-spec. |
| In-flight collaboration claims | `speckit-agent` | GitHub issue claims and overlap scans remain authoritative for HEAT work. |
| General project intake | `constraint-kit` | Use for projects without HEAT-specific governance ownership. |
| Existing-codebase archaeology | `constraint-kit` | Evidence-first discovery and confidence-tagged project context. |
| Design interview discipline | `constraint-kit` | `brainstorming` asks one question at a time and records decisions. |
| General specs and implementation plans | Choose per route | Do not create duplicate specs/plans for one work item. |
| TDD execution discipline | `constraint-kit` or `speckit-agent`, explicitly selected | If using constraint-kit, hand off to `conductor` after speckit tasks are ready. |
| Per-task reviewer loop | `constraint-kit` | Useful as an implementation discipline layer when adopted. |
| Session ledger | `constraint-kit` | `.constraint-kit/sdd/` is scratch and should be git-ignored in consuming repos. |
| Task-level secure coding defaults | `constraint-kit` | `security-principles` applies during implementation. |
| UMN policy compliance analysis | `constraint-kit` | `umn-compliance` is UMN-only and distinct from HEAT constitution compliance. |

## Routing Table

| Request shape | Front door | Handoff pattern |
|---|---|---|
| HEAT feature or significant change | `speckit-agent` | Run speckit feature workflow through `/speckit.tasks`; optionally hand execution to constraint-kit `conductor`. |
| HEAT small fix | `speckit-agent` | Use `/speckit.fix`; optionally apply constraint-kit TDD/reviewer discipline if the fix becomes nontrivial. |
| HEAT multi-spec initiative with dependencies | `speckit-agent` | Use `/speckit.roadmap`; each roadmap item still becomes its own spec. |
| Non-HEAT SRE feature | `constraint-kit` | Use planner workflow through spec/plan, then constraint-dev execution. |
| UMN compliance review | `constraint-kit` | Use `umn-compliance`; resulting design gaps can enter either framework based on owning team. |
| Cross-team work touching HEAT and non-HEAT repositories | Split the work | HEAT-governed repository changes go through speckit; other repositories use their owning workflow. Relate them through roadmap or plan references. |
| Ambiguous ownership | Ask one routing question | Determine whether HEAT constitution/roadmap/claim governance applies. |

## Artifact Mapping

| speckit-agent artifact | constraint-kit counterpart | Integration rule |
|---|---|---|
| `.specify/memory/constitution.md` | `docs/PROJECT.md` constraints | Do not duplicate. Reference HEAT constitution from project context when needed. |
| speckit spec | `docs/constraint-kit/specs/*` | Choose one authoritative spec. For HEAT work, speckit spec wins. |
| speckit plan | `docs/constraint-kit/specs/*` or plan design sections | Choose one planning artifact family per work item. Avoid parallel plans. |
| speckit tasks | `docs/constraint-kit/plans/*` | Can be converted into a constraint-kit execution plan if using `conductor`. |
| speckit evidence | session ledger and test output | Keep evidence where the front-door framework expects it; cross-link if needed. |
| speckit claims | no direct equivalent | Claims stay in speckit/GitHub issues. constraint-kit should not recreate them. |
| `.specify/roadmaps.yml` | project context links | If constraint-kit runs in a governed repo, record the roadmap pointer in `PROJECT.md`. |
| `.constraint-kit/sdd/` | no speckit equivalent | Use only for constraint-kit execution scratch; do not commit. |

## Conflict Precedence

When both frameworks are visible in a workspace, apply the most specific governing
rule for the active task:

1. Safety and secrets rules always apply. If either framework forbids exposing or
   committing sensitive data, the stricter rule wins.
2. HEAT constitution rules win for HEAT-governed repositories and specs.
3. UMN policy compliance rules win for UMN compliance analysis outputs.
4. The front-door framework owns spec, plan, and evidence artifact locations.
5. The execution framework owns task loop mechanics after handoff.
6. Repo-local instructions win over generic personal preferences.

If a conflict remains unresolved, stop and ask one routing question rather than
silently blending workflows.

## Handoff: speckit to constraint-kit

Use this when a HEAT-governed feature has already gone through speckit planning,
but the team wants constraint-kit implementation discipline.

Preconditions:

- A speckit spec exists.
- `/speckit.plan` and `/speckit.tasks` have completed.
- The implementation repository is named explicitly.
- In-flight claim checks have run according to speckit rules.
- The user explicitly chooses constraint-kit execution.

Handoff packet:

```text
Source framework: speckit-agent
Execution framework: constraint-kit
Authoritative spec: <path or URL to speckit spec>
Authoritative task list: <path or URL to speckit tasks>
Implementation repository: <owner/repo>
Allowed files or surfaces: <paths, globs, interfaces>
Evidence expectations: <tests, plans, logs, PR evidence>
HEAT constitution constraints: <principles most relevant to this task>
Stop conditions: <when to return to speckit/spec owner>
```

Constraint-kit then creates or uses a `docs/constraint-kit/plans/*` execution plan
that references the speckit spec as authoritative. The plan should not restate the
business requirements except where needed to preserve test seams and task intent.

Execution proceeds through `conductor`:

```text
conductor -> implementer -> reviewer -> ledger -> next task
```

Completion evidence is linked back to the speckit claim, task list, or pull request.

## Handoff: constraint-kit to speckit

Use this when constraint-kit discovery reveals that the work is governed by HEAT.

Preconditions:

- `planner` or `project-archaeology` discovers HEAT ownership, roadmap pointers,
  or speckit governance notice.
- The requested change affects a HEAT-governed repository or initiative.
- No conflicting speckit claim has already been ignored.

Handoff packet:

```text
Source framework: constraint-kit
Target framework: speckit-agent
Discovery summary: <what constraint-kit found>
Candidate request type: <roadmap | feature | fix | exploration>
Relevant repositories: <owner/repo list>
Relevant paths or interfaces: <paths, globs, interfaces>
Known constraints: <PROJECT.md, ARCHAEOLOGY.md, or glossary references>
Recommended speckit entry point: </speckit.* command>
```

After handoff, speckit owns the spec/plan/task artifacts unless the team later
chooses a speckit-to-constraint-kit execution handoff.

## Optional Bridge Skill

A future bridge skill could make the handoff explicit without merging the two
frameworks.

Possible name:

```text
speckit-constraint-kit-handoff
```

Activation description:

```text
Use when a HEAT speckit workflow needs to hand implementation to constraint-kit,
or when constraint-kit discovers that work belongs under HEAT speckit governance.
Produces a handoff packet and routing recommendation; does not create duplicate
specs or plans.
```

The bridge skill should:

- read the authoritative artifact from the front-door framework
- identify the active workflow owner
- produce a handoff packet
- refuse to create duplicate specs for the same work item
- record cross-links between artifacts
- stop before implementation unless an approved execution plan exists

It should not:

- copy the HEAT constitution into constraint-kit
- copy constraint-kit skills into speckit always-on instructions
- bypass speckit in-flight claims
- bypass constraint-kit review or ledger rules once constraint-kit owns execution

## Example: HEAT Feature Uses speckit Front Door and constraint-kit Execution

1. User asks for a new HEAT feature.
2. `speckit` concierge classifies it as a feature.
3. `/speckit.specify` creates the business-driven spec.
4. `/speckit.clarify` resolves ambiguities.
5. `/speckit.plan` creates technical design artifacts.
6. `/speckit.tasks` creates dependency-ordered tasks and runs collaboration scans.
7. User chooses constraint-kit execution discipline.
8. Bridge produces a handoff packet referencing the speckit spec and tasks.
9. `conductor` executes one task at a time with implementer/reviewer loops.
10. Evidence and PR links are posted back to the speckit claim or task artifact.

## Example: SRE Planner Discovers HEAT Governance

1. User starts in constraint-kit `planner` for an SRE project change.
2. `project-archaeology` finds `.specify/roadmaps.yml` or a speckit governance
   notice in `.github/copilot-instructions.md` or `AGENTS.md`.
3. Planner stops before producing a competing spec.
4. Bridge recommends `/speckit.specify` or `/speckit.roadmap` based on scope.
5. User switches to speckit for governance-owned planning.
6. constraint-kit can re-enter later only if selected as execution discipline.

## Anti-Patterns

- Running `/speckit.specify` and `writing-specs` for the same work item.
- Creating both speckit tasks and a separate constraint-kit plan with different
  task boundaries.
- Copying the HEAT constitution into constraint-kit plugin instructions.
- Copying constraint-kit agent roles into speckit without preserving speckit
  routing and claim behavior.
- Allowing both frameworks to generate `.github/copilot-instructions.md` for the
  same repository without a clear owner.
- Treating `umn-compliance` as a replacement for HEAT constitution compliance.
- Treating HEAT constitution compliance as a replacement for UMN policy analysis.

## Adoption Plan

1. Document this coexistence model in both repositories.
2. Pick one HEAT feature and run speckit through `/speckit.tasks` only.
3. Convert that task list into a constraint-kit execution plan by reference.
4. Run only the first task through `conductor`.
5. Review whether evidence, claims, PRs, and ledger entries are easy to follow.
6. Adjust the handoff packet before creating any bridge skill.
7. Only then automate the bridge.

## Open Questions

- Should speckit task artifacts be converted into constraint-kit plans, or should
  constraint-kit consume them directly by reference?
- Which repository should own the optional bridge skill: `speckit-agent`,
  `constraint-kit`, or a small shared integration repo?
- Should the bridge write cross-links automatically, or only produce a checklist
  for the engineer to confirm?
- Should constraint-kit `umn-compliance` outputs be referenced from speckit specs
  when HEAT work has UMN policy implications?

## Recommendation

Keep the frameworks separate and composable.

Use `speckit-agent` as the HEAT governance front door. Use `constraint-kit` as a
general workflow-discipline layer that can take over at explicit implementation
handoff points, or route away when HEAT governance applies. Build a bridge only
after one manual handoff proves the artifact mapping and precedence rules are
correct.
