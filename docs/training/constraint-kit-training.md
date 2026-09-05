# constraint-kit Training Deck

Audience: UMN SRE engineers who already understand Copilot agent mode,
custom instructions, prompt files, custom agents, skills, MCP servers, and
hooks.

Format: 30-45 minute training deck plus 15-30 minute hands-on exercise.

Source deck prerequisite: `UMN-SRE-Copilot-Agents-Training`.

## Deck Intent

The existing Copilot Agents training teaches the primitives. This deck teaches
the operating model: how UMN SRE uses those primitives through constraint-kit to
move from an idea to reviewed, tested, merge-ready work without losing project
context between sessions.

## Reuse From Existing Deck

Use these existing slides as abbreviated recap material or visual source:

| Existing slide | Reuse purpose |
|---|---|
| 2. Copilot is no longer just autocomplete | Opening reminder: agents can plan, act, observe, and iterate. |
| 3. Agent mode 101 | One-slide recap of the agent loop. |
| 4. The toolbox | Vocabulary bridge from primitives to constraint-kit. |
| 5. Where files live | Introduce personal, workspace, org, and enterprise scope. |
| 14. Agent Skills | Explain why constraint-kit can ship many capabilities without flooding context. |
| 20. Subagents | Explain conductor, implementer, and reviewer isolation. |

Do not copy the whole deck. Keep the recap to 5 minutes or less.

---

## Slide 1: constraint-kit for UMN SRE

Subtitle: From Copilot customization primitives to a disciplined design-to-merge
workflow.

Bullets:

- A practical workflow for planning, implementation, review, and compliance
- Built from Copilot agents, skills, instructions, and persistent repo artifacts
- Designed for real UMN SRE project work, not demo-only prompting

Speaker notes:

This is the follow-up to the Copilot Agents deck. That deck taught the parts;
this one teaches the way we assemble them into a repeatable work practice.

---

## Slide 2: The Problem

Title: Agents Drift When the Rules Only Live in Chat

Bullets:

- Early-session rules fade as context fills up
- Project conventions get rediscovered every time
- Planning, implementation, and review blur together
- Handoffs fail when the next session lacks the original reasoning

Speaker notes:

The failure mode is not that Copilot is weak. It is that we often ask it to
remember too much transient context. constraint-kit moves durable context into
the repo.

---

## Slide 3: The Core Idea

Title: Constraints on Disk, Not in Memory

Bullets:

- Project context lives in committed documents
- Plans and specs survive chat resets and context compaction
- Generated Copilot instructions carry project rules into future sessions
- Execution scratch lives separately and can be resumed

Speaker notes:

constraint-kit treats documentation as operational infrastructure. The files are
not ceremony; they are the memory layer the agent can reliably reload.

---

## Slide 4: What constraint-kit Is

Title: A Plugin Marketplace for Disciplined Copilot Workflows

Bullets:

- Ships skills, custom agents, and plugin manifests
- Works with GitHub Copilot CLI, VS Code, coding agent, and Claude Code
- Organizes work into design, development, and UMN compliance plugins
- Writes project-specific outputs into the consuming repo

Speaker notes:

The constraint-kit repo is not an app and has no build step. Its structure is the
contract: plugins, skills, agents, manifests, and validation.

---

## Slide 5: The Three Plugins

Title: Design, Development, Compliance

Bullets:

- `constraint-design`: intake, archaeology, brainstorming, specs, plans
- `constraint-dev`: TDD, subagent execution, reviews, ledger, branch finishing
- `umn-compliance`: UMN policy compliance analysis for UMN projects only

Speaker notes:

The first two are general workflow plugins. The third encodes UMN-specific
policy and should not be installed for non-UMN projects.

---

## Slide 6: The Workflow at a Glance

Title: Idea to Merge-Ready Work

Bullets:

- Onboard the project once
- Brainstorm the change until the design is approved
- Write the spec
- Write the test-first implementation plan
- Execute through conductor, implementer, reviewer, and TDD
- Finish with verification and an integration choice

Speaker notes:

The key behavior change is that we stop jumping straight from idea to code. The
workflow keeps design decisions, implementation steps, and review evidence
separate.

---

## Slide 7: Agent Roles

Title: Each Agent Has a Job Boundary

Bullets:

- `planner`: designs and plans; never edits source code
- `conductor`: orchestrates plan execution; never edits code directly
- `implementer`: executes one task at a time with TDD
- `reviewer`: reviews diffs; changes nothing
- `compliance-analyst`: performs UMN compliance analysis; never edits source

Speaker notes:

The boundaries are intentional. The planner should not sneak into
implementation. The conductor should not bypass implementer and reviewer loops.

---

## Slide 8: Files Created in Your Repo

Title: The Repo Becomes the Shared Memory

Bullets:

- `docs/PROJECT.md`: goals, stack, conventions, constraints, session log
- `docs/GLOSSARY.md`: agreed domain language
- `docs/ARCHAEOLOGY.md`: evidence from existing-codebase discovery
- `docs/constraint-kit/specs/`: designs and PRD-style specs
- `docs/constraint-kit/plans/`: test-first implementation plans
- `.github/copilot-instructions.md`: generated project rules for Copilot
- `.constraint-kit/sdd/`: git-ignored execution scratch and ledger

Speaker notes:

The repo can now teach the next session how to work. New teammates and future
agents are reading the same source of truth.

---

## Slide 9: Intake Path for New Projects

Title: `project-intake`

Bullets:

- Use for new or early-stage projects
- Interviews the user one question at a time
- Captures purpose, success criteria, constraints, conventions, and terms
- Produces `PROJECT.md`, `GLOSSARY.md`, and Copilot instructions

Speaker notes:

This replaces the old habit of stuffing project background into one giant prompt
and hoping it sticks.

---

## Slide 10: Intake Path for Existing Projects

Title: `project-archaeology`

Bullets:

- Use when code exists but docs are missing, stale, or untrusted
- Reads the code before asking the user decisions
- Records confidence-tagged evidence in `docs/ARCHAEOLOGY.md`
- Produces the same project context outputs as intake

Speaker notes:

Archaeology is for repos where the code is the truth. The output separates what
the agent verified from what remains unknown.

---

## Slide 11: CodeGraph

Title: Structural Code Questions Need Structural Tools

Bullets:

- CodeGraph answers callers, symbols, impact, and affected tests
- `codegraph-setup` installs and wires it where available
- Skills degrade to built-in search when CodeGraph is absent
- Confidence is lower when structural answers come from plain search

Speaker notes:

The important training point is not the tool brand. It is that broad grep loops
are a weak substitute for structural understanding when planning changes.

---

## Slide 12: Design Comes Before Code

Title: `brainstorming`

Bullets:

- Turns an idea into an approved design
- Asks one question at a time
- Proposes alternatives and trade-offs
- Captures glossary terms and decision records as they crystallize
- Writes design output under `docs/constraint-kit/specs/`

Speaker notes:

The skill is intentionally strict because small changes are where assumptions
hide. The design can be short, but it should still be explicit.

---

## Slide 13: From Design to Spec

Title: `writing-specs`

Bullets:

- Synthesizes the approved design into a PRD-style spec
- Captures problem, solution, user stories, decisions, testing seams, and scope
- Does not reopen the interview unless something is ambiguous
- Produces a stable target for planning and review

Speaker notes:

Specs are for shared intent. They let the implementer and reviewer test work
against something firmer than chat memory.

---

## Slide 14: From Spec to Plan

Title: `writing-plans`

Bullets:

- Designs module boundaries before task steps
- Produces small, test-first implementation steps
- Names files, tests, validation commands, and review checkpoints
- Hands execution to `constraint-dev`

Speaker notes:

The plan is not a vague checklist. It should be bite-sized enough that each task
can be implemented, tested, and reviewed independently.

---

## Slide 15: Development Mode

Title: `constraint-dev` Executes the Plan

Bullets:

- `conductor` reads the plan and manages the execution loop
- `implementer` changes code one task at a time
- `reviewer` checks spec compliance and quality after each task
- `session-ledger` records verified progress

Speaker notes:

The conductor coordinates but does not edit. That keeps orchestration context
clean and makes review a normal part of every task, not an afterthought.

---

## Slide 16: TDD Is the Default

Title: Red, Green, Refactor

Bullets:

- Tests are written at pre-agreed seams
- Failing tests prove the behavior gap
- Passing tests prove the implementation changed the right behavior
- Refactor happens only after the behavior is protected

Speaker notes:

This is not TDD theater. A test that would pass before the implementation is not
evidence. The loop keeps the agent honest.

---

## Slide 17: Subagent-Driven Development

Title: Fresh Context Per Task

Bullets:

- Each implementation task gets a fresh implementer context
- Each task gets reviewed before being marked complete
- Fix loops are bounded
- The ledger, not memory, is the source of truth

Speaker notes:

This is where the current Copilot Agents deck's subagent slide becomes useful.
constraint-kit applies subagents to reduce context contamination during longer
work.

---

## Slide 18: The Session Ledger

Title: Verified Progress, Not Vibes

Bullets:

- Records what was done and how it was verified
- Detects edit failures and repeated loops
- Survives compaction and handoff
- Appends durable lessons to `docs/PROJECT.md`

Speaker notes:

The ledger is a guardrail against false completion. It lets a later session
resume from evidence rather than recollection.

---

## Slide 19: Security Principles

Title: Secure Defaults During Implementation

Bullets:

- Vault-first secrets handling
- Least privilege access
- No credentials in logs, errors, commits, or MCP config
- Risk-based findings rather than reflex severity labels
- Activates whenever work touches auth, credentials, or sensitive data

Speaker notes:

This is task-level secure coding discipline. It is distinct from the UMN
compliance analysis plugin.

---

## Slide 20: UMN Compliance Plugin

Title: Compliance Is a Separate Analysis Workflow

Bullets:

- `umn-compliance` is UMN-only
- Maps projects against the 16 UMN Information Security Policy Standards
- Records data classification and security level in `PROJECT.md`
- Produces design gaps that feed back into planner workflow

Speaker notes:

This should not be framed as a generic open-source plugin. It encodes UMN policy
and belongs in UMN contexts.

---

## Slide 21: Install Path

Title: Installing the Plugins

Bullets:

- Add the marketplace: `umn-sre/constraint-kit`
- Install `constraint-design`
- Install `constraint-dev`
- Install `umn-compliance` only for UMN projects
- For VS Code, vendor skills and agents into `.github/` when needed

Speaker notes:

The README has exact commands. Keep this slide conceptual unless the session is
a hands-on install workshop.

---

## Slide 22: How to Use It Day to Day

Title: Which Agent Do I Pick?

Bullets:

- New project or stale docs: switch to `planner`
- New feature idea: stay in `planner` for brainstorming, spec, and plan
- Approved plan: switch to `conductor`
- Single task execution: use `implementer` only when appropriate
- Review-only work: use `reviewer`
- UMN policy analysis: use `compliance-analyst`

Speaker notes:

Most confusion comes from using the right skill with the wrong agent. The agent
is the user's workflow switch.

---

## Slide 23: What Not to Do

Title: Common Failure Modes

Bullets:

- Do not ask the planner to implement
- Do not skip from idea directly to code for non-trivial work
- Do not start implementation on `main` without making that explicit
- Do not commit `.constraint-kit/sdd/`
- Do not install `umn-compliance` outside UMN work
- Do not treat generated docs as disposable ceremony

Speaker notes:

These are not stylistic preferences. They protect the behavior the workflow is
designed to create.

---

## Slide 24: Example Walkthrough

Title: Existing Runbook Repo Change

Scenario:

Add a new monitoring workflow to an existing UMN SRE runbook repository.

Flow:

1. `planner` runs `project-archaeology` if project context is missing
2. `brainstorming` resolves what the workflow should do
3. `writing-specs` captures behavior and test seams
4. `writing-plans` creates small implementation tasks
5. `conductor` executes with implementer and reviewer loops
6. `finishing-a-development-branch` verifies and presents integration options

Speaker notes:

Use a familiar repo-shaped example. The point is to show the flow, not to teach
the specific runbook domain.

---

## Slide 25: Hands-On Exercise

Title: Run One Design-to-Plan Pass

Exercise:

1. Pick a small repo or sample project
2. Ask the `planner` to onboard it
3. Propose one small change
4. Answer the brainstorming questions
5. Generate a spec
6. Generate a test-first plan
7. Stop before implementation and review the artifacts

Speaker notes:

For first training, stop at the plan. That keeps the exercise focused on the
new behavior: capturing constraints and designing before coding.

---

## Slide 26: Hands-On Exercise Extension

Title: Execute One Task

Exercise:

1. Switch to `conductor`
2. Execute the first plan task only
3. Watch the TDD loop
4. Review the ledger entry
5. Inspect the reviewer feedback
6. Discuss whether the artifacts would help a future session resume

Speaker notes:

This extension is useful for a longer workshop. It makes the planner-to-dev
handoff concrete.

---

## Slide 27: Adoption Path

Title: Start With One Repo

Bullets:

- Week 1: install plugins and onboard one active repo
- Week 2: run one real change through planner to plan
- Week 3: execute one bounded task through conductor
- Week 4: add compliance analysis for UMN projects that need it
- Then standardize lessons in repo docs and team instructions

Speaker notes:

The adoption path should be incremental. The goal is durable team behavior, not
turning on every feature everywhere at once.

---

## Slide 28: Recap

Title: The New Default

Bullets:

- Use the Copilot Agents toolbox as primitives
- Use constraint-kit as the UMN SRE workflow layer
- Put durable context in the repo
- Keep design, implementation, review, and compliance distinct
- Let future sessions resume from evidence

Speaker notes:

The headline is simple: constraint-kit turns agent capability into a repeatable
engineering practice.

---

## Slide 29: Resources

Title: Where to Go Next

Bullets:

- `README.md`: install and workflow overview
- `docs/GETTING-STARTED.md`: first complete design-to-merge pass
- `docs/DESIGN.md`: architecture and skill merge map
- `plugins/constraint-design/README.md`: design-stage skills
- `plugins/constraint-dev/README.md`: implementation-stage skills
- `plugins/umn-compliance/README.md`: UMN compliance workflow

Speaker notes:

The Getting Started guide is the best companion document for the training.

---

## Google Slides Build Notes

Recommended production approach:

1. Copy the visual theme from `UMN-SRE-Copilot-Agents-Training`.
2. Reuse the title/footer style so the two decks feel related.
3. Keep slides 2-6 visually similar to the existing deck for continuity.
4. Use a distinct workflow diagram style for slides 6, 15, and 17.
5. Keep code/file-path slides sparse; put detail in speaker notes.
6. Add screenshots only after the workflow is stable.

Suggested Google Slides title:

`UMN-SRE-constraint-kit-Training`
