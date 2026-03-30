# How to Use Multiple AI Surfaces with constraint-kit

This guide explains how to coordinate two AI surfaces in a single
project using constraint-kit. It covers splitting work between a
**supervisor** agent (design, architecture, recovery) and an
**implementer** agent (code generation), rendering session starters
for each, and best practices for reliable multi-surface workflows.

For the rationale behind this pattern and the failure modes it
addresses, see `docs/Multiple_AI_Surfaces.md`.

---

## 1. Why Use Multiple AI Surfaces?

Complex projects benefit from using the right AI for each phase:

- **Browser-based AI (Gemini):** Best for design, architecture, and
  reasoning. Longer context window, better for structured dialogue
  and cross-session continuity. This is the **supervisor** surface.
- **In-editor AI (Copilot Chat):** Best for code generation and
  file-specific implementation. Direct file context via `#file`
  references, incremental generation. This is the **implementer**
  surface.

The **supervisor** drives design decisions, produces decision
records, and handles recovery when files are corrupted. The
**implementer** executes approved designs against real source files.
Splitting these roles, with clear session boundaries and a portable
constraint document, reduces context drift and improves reliability.

---

## 2. Prerequisites

- Python 3, `pyyaml`, `jinja2` installed
- constraint-kit cloned or installed
- Project repo initialized with `.constraint-kit/agent.yaml`

---

## 3. Example Use Cases

Each example walks through the full cycle: supervisor session
(Gemini), handoff, and implementer session (Copilot). The scenarios
map to the three cases described in `docs/Multiple_AI_Surfaces.md`.

The examples deliberately vary how skills are loaded to illustrate
the available patterns:

- **Example A** uses `bundles:` only — the simplest way to load a
  named group of skills for a common workflow.
- **Example B** uses `bundles:` extended with `task_skills:` — when
  a bundle covers most of what you need but the session requires one
  additional skill.
- **Example C** uses `task_skills:` only — when no bundle is a
  close fit and you want to load skills individually.

See `registry.yaml` for all available bundles and skills.

---

### Example A: Adding a Cross-Cutting Feature to Existing Modules

**Scenario:** A new capability needs to be wired consistently across
several existing modules — not as a greenfield class, but integrated
into existing call sites without disrupting what already works. The
supervisor designs the interface and records decisions before any
code is written. The implementer wires one module per session.

#### Supervisor session (Gemini) — design phase

**`.constraint-kit/agent-supervisor.yaml`**
```yaml
project: my-project
role: engineer
mode: reasoning
task: >
  Read helpers.py and the three existing modules. Answer: what is
  the correct integration point in each module? Produce a
  configuration artifact (feature_dimensions.yaml) and record the
  interface decision as DR-001 before any code is written.
target: session-prompt
bundles:
  - engineering-decision
session_history:
  - "2026-03-10: Project initialized. Feature scope confirmed."
  - "2026-03-10: No design decisions recorded yet."
```

```bash
python render.py .constraint-kit/agent-supervisor.yaml \
  --target session-prompt --write
# Writes to: .constraint-kit/session-starter.md
```

**Session notes:**
- Paste `.constraint-kit/session-starter.md` as your first Gemini
  message.
- Ask Gemini to read the relevant files and answer the integration
  questions before proposing anything. Do not let it jump to
  generating wiring code in this session.
- Exit condition: `feature_dimensions.yaml` committed, DR-001
  written, `session_history` updated.

**Update `agent-supervisor.yaml` before closing:**
```yaml
session_history:
  - "2026-03-10: Project initialized. Feature scope confirmed."
  - "2026-03-10: DR-001 approved. Interface defined in feature_dimensions.yaml."
```

#### Handoff

Update `.constraint-kit/agent-implementer.yaml` with the approved
task and the current session history. Re-render before opening
Copilot.

#### Implementer session (Copilot) — wiring phase

**`.constraint-kit/agent-implementer.yaml`**
```yaml
project: my-project
role: engineer
mode: generating-code
task: >
  Wire the approved interface into module_a.py per DR-001 and
  feature_dimensions.yaml. Reference those files directly. Do not
  modify helpers.py or other modules in this session.
target: copilot-instructions
session_history:
  - "2026-03-10: DR-001 approved. Interface defined in feature_dimensions.yaml."
  - "2026-03-10: module_a.py is the first wiring target."
```

```bash
python render.py .constraint-kit/agent-implementer.yaml \
  --target copilot-instructions --write
# Writes to: .github/copilot-instructions.md
# Copilot auto-loads this file — no paste required.
```

**Session notes:**
- Use `#file` to reference `module_a.py`, `helpers.py`, and
  `feature_dimensions.yaml` at session start.
- Ask Copilot to read the files and confirm the integration point
  before proposing any changes.
- Run `py_compile` and `ruff check` after every write. Do not
  proceed to the next module until this one passes clean.
- Exit condition: `module_a.py` committed clean. Repeat this session
  for each remaining module, updating `task` each time.

---

### Example B: Refactoring Shared Infrastructure Under Active Use

**Scenario:** A shared helper module (`helpers.py`) used by multiple
callers needs its signatures updated — new patterns introduced, old
ones deprecated — without breaking existing callers. The supervisor
inventories call sites and records the deprecation plan. The
implementer updates one call site per session.

#### Supervisor session (Gemini) — inventory and decision phase

**`.constraint-kit/agent-supervisor.yaml`**
```yaml
project: my-project
role: engineer
mode: collaborating
task: >
  Read helpers.py and all files that import it. Produce a call site
  inventory table: file, function called, arguments passed. Identify
  which call sites will break under the new signature. Record the
  deprecation and migration plan as DR-002. Do not write any
  implementation code in this session.
target: session-prompt
bundles:
  - engineering-decision
task_skills:
  - systematic-debugging
session_history:
  - "2026-03-11: Refactor scope identified. helpers.py signature change approved."
  - "2026-03-11: Call site inventory not yet complete."
```

```bash
python render.py .constraint-kit/agent-supervisor.yaml \
  --target session-prompt --write
# Writes to: .constraint-kit/session-starter.md
```

**Session notes:**
- Paste `.constraint-kit/session-starter.md` as your first Gemini
  message.
- Provide Gemini with the list of files that import `helpers.py`.
  Ask it to produce the inventory table before any analysis.
- Confirm the inventory is complete and accurate before asking for
  DR-002. A wrong inventory produces a wrong decision record.
- Exit condition: call site inventory committed as
  `docs/callsite-inventory.md`, DR-002 written, `session_history`
  updated.

**Update `agent-supervisor.yaml` before closing:**
```yaml
session_history:
  - "2026-03-11: Refactor scope identified. helpers.py signature change approved."
  - "2026-03-11: DR-002 approved. 4 call sites identified, migration order recorded."
```

#### Handoff

Update `.constraint-kit/agent-implementer.yaml` with the first
call site as the task target. Re-render before opening Copilot.

#### Implementer session (Copilot) — call site update phase

**`.constraint-kit/agent-implementer.yaml`**
```yaml
project: my-project
role: engineer
mode: generating-code
task: >
  Update the call site in service_a.py to use the new helpers.py
  signature per DR-002 and docs/callsite-inventory.md. Do not update
  helpers.py itself or any other call site in this session.
target: copilot-instructions
session_history:
  - "2026-03-11: DR-002 approved. 4 call sites identified, migration order recorded."
  - "2026-03-11: service_a.py is call site 1 of 4."
```

```bash
python render.py .constraint-kit/agent-implementer.yaml \
  --target copilot-instructions --write
# Writes to: .github/copilot-instructions.md
```

**Session notes:**
- Use `#file` to reference `service_a.py`, `helpers.py`, and
  `docs/callsite-inventory.md`.
- Ask Copilot to confirm the current call signature in `service_a.py`
  before proposing any changes.
- Run `py_compile` and `ruff check` after the change. Run the
  existing test suite if available.
- Exit condition: `service_a.py` committed clean. Update `task` and
  `session_history` for the next call site and re-render before the
  next session.

---

### Example C: Incident Response Runbook Authoring

**Scenario:** A novel incident has occurred. A new runbook needs to
be authored quickly against an established schema and validated
against the existing runbook corpus before use. The supervisor
synthesizes the incident timeline into a runbook structure. The
implementer generates the runbook against the schema.

#### Supervisor session (Gemini) — synthesis phase

**`.constraint-kit/agent-supervisor.yaml`**
```yaml
project: my-project
role: engineer
mode: reasoning
task: >
  Read the incident timeline in docs/incident-2026-03-12.md and two
  existing runbooks for structural reference. Identify the key
  response steps and decision points. Map them to runbook section
  structure using runbooks/TEMPLATE.yaml as the schema. Produce a
  structured outline only — do not generate the runbook itself.
target: session-prompt
task_skills:
  - research-brief
  - document-structure
session_history:
  - "2026-03-12: Incident postmortem complete. Timeline committed."
  - "2026-03-12: Runbook outline not yet started."
```

```bash
python render.py .constraint-kit/agent-supervisor.yaml \
  --target session-prompt --write
# Writes to: .constraint-kit/session-starter.md
```

**Session notes:**
- Paste `.constraint-kit/session-starter.md` as your first Gemini
  message.
- Provide the incident timeline and two reference runbooks. Ask
  Gemini to read all three before producing the outline.
- The outline is the exit artifact, not the runbook itself. Keeping
  synthesis and generation in separate sessions prevents the agent
  from producing a runbook that looks correct but contains subtle
  schema violations.
- Exit condition: outline committed as
  `docs/runbook-outline-2026-03-12.md`, `session_history` updated.

**Update `agent-supervisor.yaml` before closing:**
```yaml
session_history:
  - "2026-03-12: Incident postmortem complete. Timeline committed."
  - "2026-03-12: Runbook outline approved. Committed as docs/runbook-outline-2026-03-12.md."
```

#### Handoff

Update `.constraint-kit/agent-implementer.yaml` with the generation
task and the outline as the authoritative input. Re-render before
opening Copilot.

#### Implementer session (Copilot) — generation phase

**`.constraint-kit/agent-implementer.yaml`**
```yaml
project: my-project
role: engineer
mode: generating-code
task: >
  Generate the incident response runbook from
  docs/runbook-outline-2026-03-12.md. Follow the schema in
  runbooks/TEMPLATE.yaml exactly. Validate output against the schema
  before declaring the session complete. Do not alter the outline or
  the template in this session.
target: copilot-instructions
session_history:
  - "2026-03-12: Runbook outline approved. Committed as docs/runbook-outline-2026-03-12.md."
  - "2026-03-12: Generating runbook against schema."
```

```bash
python render.py .constraint-kit/agent-implementer.yaml \
  --target copilot-instructions --write
# Writes to: .github/copilot-instructions.md
```

**Session notes:**
- Use `#file` to reference the outline, the template, and one
  existing runbook as a structural reference.
- Ask Copilot to read all three files and confirm it understands the
  required section structure before generating anything.
- After generation, run schema validation. If validation fails, use
  the error output to make targeted corrections — do not ask Copilot
  to "fix" the runbook freehand, as this tends to introduce new
  violations.
- Exit condition: runbook committed clean, schema validation passing.
  Switch back to the supervisor session (Gemini) for consistency
  review against the existing runbook corpus.

---

## 4. Render Session Starters for Each Surface

**For the supervisor (Gemini browser):**
```bash
python render.py .constraint-kit/agent-supervisor.yaml \
  --target session-prompt --write
# Writes to: .constraint-kit/session-starter.md
```
Paste the contents of `.constraint-kit/session-starter.md` as your
first message in the Gemini session.

**For the implementer (Copilot Chat):**
```bash
python render.py .constraint-kit/agent-implementer.yaml \
  --target copilot-instructions --write
# Writes to: .github/copilot-instructions.md
```
Copilot auto-loads `.github/copilot-instructions.md` for in-editor
sessions. No paste required.

---

## 5. Running Sessions and Switching Surfaces

The standard flow for a design-then-implement cycle:

1. **Supervisor session (Gemini):** Run the design phase. Record
   decisions. Update `session_history` in
   `.constraint-kit/agent-supervisor.yaml` with what was decided.

2. **Handoff:** Update `task` and `session_history` in
   `.constraint-kit/agent-implementer.yaml` to reflect the approved
   design. Re-render the implementer session starter.

3. **Implementer session (Copilot):** Execute the approved design.
   One file or function per session. Commit after each clean
   verification.

4. **Switch back if needed:** For review, recovery, or a new design
   decision, update `.constraint-kit/agent-supervisor.yaml`, re-render,
   and start a new Gemini session.

**The `task`, `mode`, and `session_history` fields must be updated
between phases.** The session history is the only mechanism that
carries decisions across surfaces. If it is not updated, the next
session starts without knowledge of what was decided.

---

## 6. Best Practices

- **Keep generating sessions short.** 90 minutes is a practical
  ceiling. Beyond that, context drift increases faster than the
  productivity gain justifies.
- **Commit between sessions, not within them.** Each session should
  produce one committed artifact. This keeps recovery paths clean.
- **Use tools for mechanical work.** `ruff --fix`, `isort`, and
  `py_compile` are more reliable than any agent for formatting,
  import ordering, and syntax validation. Run them after every write.
- **Never rely on AI memory between sessions.** The constraint
  document is the only cross-session memory. If it is not updated,
  the context is gone.
- **Paste the session starter at the start of every new session.**
  For Gemini, this is manual. For Copilot, the auto-loaded
  `copilot-instructions.md` handles it.

---

## 7. Troubleshooting and Recovery

**Context drift mid-session:** Re-paste the session starter into
the current chat. This re-injects constraints without requiring a
new session. If drift is severe, end the session, update the
`session_history` to note what happened, and start fresh.

**File corruption:** Switch to the supervisor session (Gemini).
Delete the corrupted file. Write a complete precise specification
from the decision records and session history, give it to a fresh
Gemini session, verify the output with `py_compile` and
`ruff check`, then apply. Do not attempt incremental recovery in
Copilot — the supervisor surface is better suited to holding full
design context during reconstruction.

**Decision re-litigation:** If a later session proposes something
that contradicts an earlier decision, the session history was not
updated after the earlier session. Update it now, re-render, and
restart.

---

## References

- `docs/Multiple_AI_Surfaces.md` — lessons learned and rationale
  for the multi-surface pattern
- `docs/HOW_TO_USE_GITHUB.md` — single-surface technical workflow
- `docs/HOW_TO_USE_DRIVE.md` — single-surface non-technical workflow
- `bootstrap/templates/new-project-repo.yaml` — agent YAML template