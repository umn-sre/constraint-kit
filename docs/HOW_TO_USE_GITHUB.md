# How to Use constraint-kit (Technical Path)

For engineers, developers, and anyone working in a code repository.

## What constraint-kit does

It gives your AI assistant a defined role, a current task, and a
set of behavioral constraints — and keeps those constraints active
across sessions so the AI does not drift away from your standards
over time.

## Quick start

### 1. Copy the bootstrap template into your project

```bash

mkdir -p .constraint-kit
cp path/to/constraint-kit/bootstrap/templates/new-project-repo.yaml \
   .constraint-kit/agent.yaml

```

### 2. Fill in agent.yaml

Open `.constraint-kit/agent.yaml` and fill in:

```yaml

project: my-project-name
role: engineer          # or: researcher, writer, product-owner
task: "What I am doing right now in 1-2 sentences."
mode: collaborating     # or: reasoning, generating-code, generating-doc, generating-structured
target: session-prompt  # or: copilot-instructions, active-task-md

```

See `registry.yaml` for all available roles, skills, and bundles.

### 3. Render your session starter

```bash

python path/to/constraint-kit/bootstrap/render.py .constraint-kit/agent.yaml

```

This prints a session starter block to stdout.

To write it to a file instead:

```bash

python render.py .constraint-kit/agent.yaml --write

# Writes to .constraint-kit/session-starter.md

```

To render as Copilot instructions:

```bash

python render.py .constraint-kit/agent.yaml --target copilot-instructions --write

# Writes to .github/copilot-instructions.md

```

## 4. Start your AI session

Paste the rendered session starter as your first message.
The AI now has your role, task, and constraints loaded.

### 5. Update when your task changes

Edit `.constraint-kit/agent.yaml`, change the `task` and `mode` fields,
re-run the renderer, paste the new starter.

## Switching modes mid-session

The rendered session starter includes mode switch snippets at the bottom.
When you shift from collaborating to generating, paste the relevant snippet.
This re-injects the right constraints without starting a new session.

## Adding skills beyond your role baseline

In `agent.yaml`:

```yaml

task_skills:
  - decision-records
  - research-brief

```

Re-render and re-paste.

## Using bundles

Bundles are named groups of skills for common workflows:

```yaml

bundles:
  - new-feature-design

```

See `registry.yaml` for all available bundles.

## Using a private extension

If your team maintains domain-specific skills in a private repo:

```yaml

extension: ../my-private-skills/constraint-kit.yaml

```

The renderer will load skills from the extension alongside the
constraint-kit library.

## List available roles, skills, and bundles

```bash

python render.py --list

```

## Where things live

```

.constraint-kit/
├── agent.yaml          ← your project config (edit this)
└── session-starter.md  ← rendered output (re-generate, do not edit)

```
