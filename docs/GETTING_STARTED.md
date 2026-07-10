# Getting Started with constraint-kit

This guide is for anyone picking up constraint-kit for the first time —
whether you're an engineer setting it up in a repo or a non-technical
user working from Google Drive. No prior context assumed.

If you already know constraint-kit and just need a command reference,
see [`AUTOMATION_REFERENCE.md`](AUTOMATION_REFERENCE.md) instead. This
guide is about understanding *why* and *what*, not command flags.

## What problem does this solve

AI assistants drift. Give one a set of rules at the start of a
conversation, and by the middle of a long session it's ignoring them,
inventing its own conventions, or producing output that conflicts with
your standards. This isn't a matter of the model being careless — it's
a structural limitation of how context works in a conversation.

constraint-kit's fix: keep rules **on disk, not in memory**, and
re-inject them at each task boundary. The AI looks the rules up every
time rather than trying to recall them from earlier in the
conversation. Drift becomes structurally difficult rather than a
matter of luck holding out.

## The three things you need to know

Every project using constraint-kit declares three things in a small
config file:

| Concept | Question it answers | Example |
|---|---|---|
| **Role** | Who is the agent acting as? | `engineer`, `researcher`, `writer`, `product-owner` |
| **Task** | What are you working on right now? | "Refactoring the token rotation workflow" |
| **Mode** | How is the agent operating? | `reasoning`, `collaborating`, `generating-code` |

A small program (the **bootstrap renderer**) reads this config,
figures out which skills apply based on your role and mode, and
produces a block of text — a **session starter** — that you paste at
the start of every AI session. When your task or mode changes, you
re-render and paste the update. The AI never has to remember anything
across the gap; it's told fresh every time.

That's the entire mental model. Everything else in constraint-kit
(roles, skills, bundles, schemas) exists to make that config-in →
session-starter-out pipeline correct and reusable.

## Two paths, same idea

**Repo path** (for engineers): a `.constraint-kit/agent.yaml` file in
your project, rendered with a Python script.

**Drive path** (for anyone, no coding required): a filled-in template
document, attached directly to a Gemini or Claude session.

Pick whichever matches how you work day to day — both produce the same
kind of output.

## Quick start: repo path

1. **Copy the template into your project:**

   ```bash
   mkdir -p .constraint-kit
   cp path/to/constraint-kit/bootstrap/templates/new-project-repo.yaml \
      .constraint-kit/agent.yaml
   ```

2. **Fill in the four required fields** in `agent.yaml`:
   - `project` — a short kebab-case name
   - `role` — `engineer`, `researcher`, `writer`, or `product-owner`
   - `task` — one or two sentences on what you're doing right now
   - `mode` — `reasoning`, `collaborating`, `generating-code`,
     `generating-doc`, or `generating-structured`
   - `target` — where the output is going (`session-prompt` for
     pasting into a browser chat is the default and simplest choice)

   Delete the placeholder instructions in the file once you've filled
   it in — they're there to guide you, not to be committed.

3. **Render it:**

   ```bash
   python bootstrap/render.py .constraint-kit/agent.yaml
   ```

4. **Paste the output** as your first message in Gemini, Claude, or
   Copilot. That's it — you're running constrained.

When your task changes, update the `task` field and re-render. When
you switch modes mid-session (say, from `reasoning` into
`generating-code`), re-render and paste the update as a mode switch.

## Quick start: Drive path (no coding required)

1. Open the constraint-kit shared Drive folder (link maintained by
   your team lead — ask if you don't have it).
2. Copy the session starter template that matches your role.
3. Fill in your project, current task, and any background context.
4. Attach the filled-in document to a new Gemini or Claude session.

No installation, no command line, no GitHub account needed.

## Who each path is for

**Engineers** — writing code, infrastructure, or automation, with
consistent conventions, TDD discipline, and documented decisions
along the way.

**Researchers** — scoping inquiries, structuring arguments, producing
papers or briefs without unsupported claims or scope drift.

**Writers** — producing documents of any kind with consistent
structure, audience fit, and readability standards.

**Product owners** — defining features, stories, and acceptance
criteria with complete requirements and clear scope.

If you're not sure which role fits, pick the closest match — you can
layer in extra skills with `task_skills` later without switching
roles.

## What's actually in the library

You don't need to memorize this, but it helps to know it's here:

- **Roles** set your skill baseline (`engineer`, `researcher`,
  `writer`, `product-owner`).
- **Skills** are single-concern constraint documents — things like
  `test-driven-development`, `decision-records`, or `plain-language`.
  Each one addresses exactly one concern, so you can mix and match
  without inheriting rules you don't want.
- **Bundles** are pre-packaged groups of skills for a common
  situation, like `new-feature-design` or `document-drafting`.

The full current list of each lives in the top-level
[`README.md`](../README.md) and in `registry.yaml` — that's the
source of truth, so this guide won't duplicate it and risk going
stale.

## Where to go next

- **Day-to-day usage patterns** (updating tasks, switching modes,
  suppressing skills you don't need): see the how-to guide
  (`docs/HOW_TO_USE_GITHUB.md` for the repo path,
  `docs/HOW_TO_USE_DRIVE.md` for the Drive path).
- **Command and schema reference**: `docs/AUTOMATION_REFERENCE.md`.
- **Contributing a new skill or role**: `docs/HOW_TO_CONTRIBUTE.md`.
- **Why constraint-kit exists and what it's built on**: the
  Philosophy and Acknowledgments sections of the top-level
  [`README.md`](../README.md).

If something in this guide doesn't match what you're seeing, the
schema files under `schema/` are the ground truth — file an issue
(`.github/ISSUE_TEMPLATE/bug-report.md`) if the docs and the schema
have drifted apart.
