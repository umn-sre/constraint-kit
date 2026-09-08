# constraint-kit Training Facilitator Guide

Audience: facilitators delivering `UMN-SRE-constraint-kit-Training` to UMN SRE
engineers who already understand Copilot agents and VS Code customization
primitives.

Primary slide deck:

- Google Slides: `UMN-SRE-constraint-kit-Training`
- Source: `docs/training/constraint-kit-training.md`
- PowerPoint import artifact: `docs/training/UMN-SRE-constraint-kit-Training.pptx`

Related prerequisite deck:

- `UMN-SRE-Copilot-Agents-Training`

Archive/reference decks:

- `AI-Assisted Engineering - companion`
- `AI-Assisted Engineering - paradigm comparison`

The archive decks describe the pre-2.0 YAML/render.py constraint-kit model.
Do not use them as current training unless they are explicitly framed as design
history.

## Training Goal

By the end of the session, participants should be able to explain and practice
the current constraint-kit workflow:

- Use Copilot agents and skills as workflow roles, not just prompt containers.
- Put durable project context in the consuming repo's `docs/` tree.
- Run planning through `constraint-design` before implementation.
- Run implementation through `constraint-dev` with TDD, review, and ledger
  discipline.
- Use `umn-compliance` only for UMN policy analysis.
- Distinguish current plugin-marketplace constraint-kit from the archived
  YAML/render.py model.

## Recommended Session Shape

### 45-minute version

| Time | Activity | Slides |
|---|---|---|
| 0:00-0:05 | Frame the problem and prerequisite knowledge | 1-4 |
| 0:05-0:12 | Explain plugins, workflow, agents, and repo artifacts | 5-8 |
| 0:12-0:23 | Walk through planner-side work | 9-14 |
| 0:23-0:33 | Walk through dev-side work | 15-20 |
| 0:33-0:38 | Explain day-to-day usage and failure modes | 21-23 |
| 0:38-0:43 | Walk the example and exercise | 24-27 |
| 0:43-0:45 | Recap and resources | 28-29 |

### 75-minute workshop version

| Time | Activity | Slides |
|---|---|---|
| 0:00-0:10 | Deck walkthrough opening | 1-8 |
| 0:10-0:25 | Planner workflow deep dive | 9-14 |
| 0:25-0:38 | Development workflow deep dive | 15-20 |
| 0:38-0:45 | Usage rules and example walkthrough | 21-24 |
| 0:45-1:05 | Hands-on: design-to-plan pass | 25 |
| 1:05-1:15 | Optional extension: execute one task | 26 |
| 1:15-1:20 | Adoption path, questions, resources | 27-29 |

## Facilitator Prep

Before the session:

1. Open the current Google Slides deck and confirm it has 29 slides.
2. Open `docs/training/constraint-kit-training.md` as the canonical content
   source.
3. Open `README.md`, `docs/GETTING-STARTED.md`, and `docs/DESIGN.md` in the
   constraint-kit repo.
4. Pick one demo repo or sample repo where generated planning artifacts can be
   created safely.
5. Confirm whether participants should only observe, run the planner workflow,
   or also execute one development task.
6. If running hands-on, tell participants whether `umn-compliance` should be
   installed for the exercise.

Avoid live-editing the Google Slides deck during the session. Treat the
Markdown source as canonical, then regenerate/import slides when the source
changes.

## Opening Framing

Use this framing before Slide 1:

> The prior Copilot Agents deck taught the parts: instructions, prompts,
> agents, skills, MCP, hooks, and subagents. This deck teaches the operating
> model we want to use for real UMN SRE work. constraint-kit is the layer that
> turns agent capability into a repeatable design-to-merge workflow.

Emphasize that the session is not about writing clever prompts. It is about
making the repo hold the context, decisions, plans, and evidence that agents
need in order to behave consistently.

## Slide-by-Slide Notes

### Slides 1-4: Why This Exists

Key message:

- Copilot agent mode is powerful, but chat memory is not a reliable operating
  model.
- The durable unit is the repository, not the current conversation.

Ask:

- Where do we currently lose context between sessions?
- Which project conventions do we repeatedly re-explain to agents?

Avoid:

- Spending too long re-teaching Copilot customization primitives. That belongs
  in the prerequisite deck.

### Slides 5-8: The Current Architecture

Key message:

- `constraint-design`, `constraint-dev`, and `umn-compliance` map to different
  jobs.
- Agent boundaries are a feature, not ceremony.
- The consuming repo gets the persistent artifacts.

Call out:

- `planner` writes docs and plans, not source code.
- `conductor` orchestrates implementation, but does not edit code directly.
- `.constraint-kit/sdd/` is scratch and should not be committed.

### Slides 9-14: Planner Workflow

Key message:

- Planning is a workflow, not a prompt style.
- New projects start with `project-intake`; existing undocumented projects start
  with `project-archaeology`.
- `brainstorming`, `writing-specs`, and `writing-plans` create increasingly
  concrete artifacts.

Suggested demo prompt:

```text
Use the planner workflow to onboard this repo, then help me design a small
change: add a new runbook validation check that reports missing owner metadata.
```

Stop the demo before implementation unless using the 75-minute workshop format.

### Slides 15-20: Development Workflow

Key message:

- Implementation starts from an approved plan.
- TDD, reviewer feedback, and the session ledger make progress verifiable.
- `security-principles` is task-level secure coding discipline.
- `umn-compliance` is separate project-wide policy analysis.

Ask:

- What evidence should convince us that an agent actually finished a task?
- Where do we currently rely on memory instead of a ledger or test output?

Avoid:

- Treating the reviewer as optional.
- Treating compliance as the same thing as secure coding defaults.

### Slides 21-23: Day-to-Day Usage

Key message:

- The user's main decision is which agent to use.
- The workflow fails when the wrong agent is asked to do the wrong job.

Emphasize:

- Use `planner` when intent is still being shaped.
- Use `conductor` when an approved plan exists.
- Use `reviewer` when the goal is critique, not edits.
- Use `compliance-analyst` for UMN policy analysis.

### Slides 24-27: Exercise and Adoption

Key message:

- Start with one repo and one real but bounded change.
- The first adoption win is usually a clean planner-to-plan pass, not full
  automation.

Recommended exercise outcome:

- `docs/PROJECT.md` exists or is updated.
- `docs/GLOSSARY.md` exists or is updated.
- One design/spec artifact exists under `docs/constraint-kit/specs/`.
- One plan exists under `docs/constraint-kit/plans/`.
- The group can explain what would happen next in `constraint-dev`.

### Slides 28-29: Close

Key message:

- constraint-kit is the workflow layer.
- The repo is the memory layer.
- Verification and review are part of the workflow, not afterthoughts.

Close with:

> For the next real change, do not start by asking Copilot to code. Start by
> asking the planner to shape the change and write the plan.

## Hands-On Exercise Script

Use this when participants are following along in their own repo or a shared
sample repo.

### Part 1: Onboard or refresh context

Prompt:

```text
Use constraint-kit to onboard this project. If the docs are missing or stale,
use project archaeology before asking me for decisions.
```

Expected artifacts:

- `docs/PROJECT.md`
- `docs/GLOSSARY.md`
- `docs/ARCHAEOLOGY.md` for existing-codebase archaeology
- `.github/copilot-instructions.md`

### Part 2: Design a small change

Prompt:

```text
I want to add a small validation check for missing owner metadata. Use the
planner workflow to turn this into an approved design.
```

Expected behavior:

- The agent asks one question at a time.
- The agent proposes alternatives and a recommendation.
- The agent writes a design artifact under `docs/constraint-kit/specs/`.

### Part 3: Produce a spec and plan

Prompt:

```text
Synthesize the approved design into a spec, then write a test-first
implementation plan.
```

Expected artifacts:

- PRD-style spec under `docs/constraint-kit/specs/`
- implementation plan under `docs/constraint-kit/plans/`

### Part 4: Optional execution

Prompt:

```text
Switching to the conductor workflow, execute only the first task in the plan and
stop after the first reviewer pass.
```

Expected artifacts:

- tests or implementation changes for the first task
- `.constraint-kit/sdd/<plan>/progress.md`
- reviewer findings or completion evidence

## Troubleshooting

| Symptom | Likely cause | Facilitator response |
|---|---|---|
| Agent starts editing code during planning | Wrong agent or skipped workflow stage | Stop and switch back to `planner`; restate that planner does not edit source. |
| Participant wants to skip spec/plan | Change feels small | Allow a short design, but still require explicit approval and a plan. |
| Generated docs feel too verbose | Agent overproduced ceremony | Ask for a shorter artifact focused on decisions, test seams, and constraints. |
| Agent cannot answer code-structure questions confidently | CodeGraph is absent or not indexed | Use `codegraph-setup` if appropriate, or label the answer lower-confidence. |
| `.constraint-kit/sdd/` appears in git status | Scratch directory not ignored | Add `.constraint-kit/` to the consuming repo's `.gitignore`. |
| `umn-compliance` appears in a non-UMN context | Wrong plugin installed or invoked | Remove it from the workflow; it encodes UMN policy. |
| Old decks contradict the current deck | Archive material describes pre-2.0 | Use the current deck and `docs/DESIGN.md` as authoritative. |

## Archive Deck Guidance

The older AI-Assisted Engineering decks are useful as historical context but
should not be presented as current operating guidance.

Recommended first-slide archive banner:

```text
Archive: this deck describes the pre-2.0 YAML/render.py constraint-kit model.
For current training, use UMN-SRE-constraint-kit-Training.
```

What changed:

- Old model: YAML files such as `agent-base.yaml` and `agent-implementer.yaml`
  were canonical.
- Current model: native `SKILL.md`, `*.agent.md`, plugin manifests, and repo
  docs are canonical.
- Old model: `render.py` compiled constraints into surface-specific artifacts.
- Current model: plugins are installed directly, and intake writes project
  context into the consuming repo.
- Old model: `SESSION_PLAN.md` was the main handoff object.
- Current model: specs and plans live under `docs/constraint-kit/`, while
  execution scratch and progress live under `.constraint-kit/sdd/`.

## Post-Session Follow-Up

Send participants:

- Google Slides deck link for `UMN-SRE-constraint-kit-Training`
- `docs/training/constraint-kit-training.md`
- `docs/GETTING-STARTED.md`
- `README.md`
- A sample repo or branch containing generated `docs/PROJECT.md`,
  `docs/GLOSSARY.md`, one spec, and one plan

Suggested follow-up assignment:

> Pick one active repo. Run only the planner side of constraint-kit on one small
> change. Bring the generated plan to the next team review; do not implement it
> until the plan has been read by another engineer.
