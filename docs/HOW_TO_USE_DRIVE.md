# How to Use constraint-kit (Drive Path)

For researchers, writers, and anyone who works in Google Drive
rather than a code repository. No coding or GitHub knowledge required.

## What constraint-kit does

It gives your AI assistant a defined role, a current task, and a
set of behavioral constraints — so it stays focused and consistent
across sessions instead of drifting or making things up.

## Quick start

### 1. Get the shared Drive folder

Open the constraint-kit shared Drive folder and make a copy of the
session starter template that matches your work:

- **Researcher** — for papers, literature reviews, research briefs
- **Writer** — for guides, articles, technical docs, content
- **Product Owner** — for features, user stories, acceptance criteria

### 2. Create your project folder

In your own Drive, create a folder structure like this:

```

My Drive/
└── constraint-kit/
    ├── MY_PROJECTS.md          ← keep a list of your projects here
    └── projects/
        └── my-project-name/
            └── active-task.md  ← your filled-in template goes here

```

### 3. Fill in your active-task.md

Open your copy of the template and answer the questions:

- What kind of work is this?
- What are you working on right now?
- What do you need the AI to do?
- Who will read the output?
- What background does the AI need to know?

Save it in your project folder.

### 4. Start your AI session

In Gemini or Claude:
1. Start a new conversation
2. Attach your `active-task.md` file
3. Type: *"Please read the attached file and confirm you understand
   your role and constraints before we begin."*
4. Wait for the AI to confirm, then start your work

### 5. Switching modes mid-session

Your active-task.md has mode switch snippets at the bottom.
When you shift from thinking-through to writing, copy and paste
the relevant snippet into the chat.

### 6. Updating between sessions

Before your next session on the same project:
- Update "What you are working on now" if the task changed
- Add a line to Session History summarizing what was decided
- Re-attach the updated file at the start of the new session

You do not need to start from scratch each session — just keep
the file current and re-attach it.

## Managing multiple projects

Keep one `active-task.md` per project in its own folder.
Maintain `MY_PROJECTS.md` as a simple list so you can find them:

```

| Project              | Role       | Current Mode  | Last session |
|----------------------|------------|---------------|--------------|
| climate-paper        | Researcher | Collaborating | 2026-03-10   |
| q2-product-brief     | Writer     | Generating    | 2026-03-12   |

```

Switch projects by attaching a different `active-task.md`.
The AI has no memory between sessions — the file is the memory.

## When the AI starts ignoring your constraints

Context drift happens in long sessions. Signs:
- The AI stops asking clarifying questions
- It produces output without checking structure first
- It stops flagging assumptions

Fix: paste the mode switch snippet for your current mode.
This re-injects your constraints without starting a new session.

If drift is severe, start a fresh session and re-attach the file.

## Getting a pre-filled active-task.md

If you would prefer to have your session starter pre-filled with
the right skills for your role and task, contact a constraint-kit
curator with your filled-in `new-project-drive.md` template.
They will render a complete `active-task.md` for you.

Future: a Google Form will be available to request a rendered
session starter without needing to contact anyone.
