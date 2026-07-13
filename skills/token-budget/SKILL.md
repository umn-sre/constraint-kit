# Skill: Token Budget

## Purpose

Every session has a finite amount of context. Spend it carelessly —
full-file dumps for a five-line edit, re-reading the same file three
times, letting one giant task run until output starts truncating —
and the session degrades exactly when the constraints in this kit
matter most: near the end, when there's the least room left to
re-inject them. Managing the budget deliberately is what keeps a long
session as reliable at message 80 as it was at message 8.

## When This Skill Is Active

Any session, in any mode, but especially: sessions expected to run
long (multi-file refactors, iterative document drafts), sessions
involving large files or large tool outputs, and sessions where a
task is discovered mid-stream to be bigger than it first looked.

## Agent Behavior

**Reads — targeted, not total**

- Read the specific lines, function, or section relevant to the task
  instead of an entire large file, when a targeted read will do.
- Don't re-read a file that was already read earlier in the same
  session unless it may have changed since (e.g. after an edit was
  applied, or the user says they changed it externally).
- When a directory needs surveying, list it before reading individual
  files inside it, rather than opening every file to find the right
  one.

**Output — proportional, not exhaustive**

- Don't paste an entire file's contents back into the conversation to
  show a small change — show the diff, or the changed section with
  enough surrounding context to locate it.
- Summarize large tool outputs (long command output, big search
  result sets, long file listings) before continuing, rather than
  quoting them in full and reasoning on top of the quote.
- When the same information would otherwise be repeated across
  several turns, refer back to it instead of restating it.

**Task sizing — chunk explicitly, don't drift into it**

- If a task looks likely to exceed what one session can comfortably
  hold — a large multi-file migration, an exhaustive audit, a long
  generation task — say so up front and propose how it will be
  chunked, rather than starting in and discovering the problem
  halfway through.
- At a natural checkpoint in a long session (a phase complete, a
  major decision made), suggest recording a note in the project's
  `session_history` before continuing. This is the same mechanism
  `render.py` already supports for re-injecting prior context in the
  *next* session — using it well is what makes chunking actually work
  instead of just being a promise.
- If context pressure is visibly affecting quality — repeated
  clarifying questions the answer to which was already given,
  contradicting an earlier decision in the same session — that's the
  signal to close out the current chunk and hand off via
  `session_history`, not to push further into the same session.

## Anti-Patterns

- Do NOT paste an entire file when only a small section is relevant
  or changed
- Do NOT re-read a file multiple times in one session without a
  reason it may have changed
- Do NOT let a large task run unchunked until output starts
  truncating or quality visibly degrades
- Do NOT quote a long tool output in full when a summary would serve
  the same purpose
- Do NOT silently push through context pressure — surface it and
  propose a checkpoint

## Transition

At a checkpoint, hand off to `decision-records` if a non-obvious
chunking or scoping decision was made that the next session needs to
know about, or simply resume the mode-appropriate skill for the next
chunk of work.
