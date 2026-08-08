# constraint-dev

Disciplined implementation bundle for GitHub Copilot (CLI, VS Code,
coding agent) and Claude Code. Executes plans written by the
**constraint-design** plugin (`.constraint-kit/plans/`), but the skills
stand alone too.

## Skills

| Skill | Purpose |
|---|---|
| `test-driven-development` | The red-green loop, tests at pre-agreed seams, anti-rationalization discipline |
| `subagent-driven-development` | Fresh implementer subagent per task, per-task reviews, ledger-tracked progress |
| `executing-plans` | Inline plan execution when subagents aren't available |
| `session-ledger` | Runtime discipline: session ledger, edit verification, loop detection, budget watch, clean wrap-up with lessons appended to `.constraint-kit/PROJECT.md` |
| `security-principles` | Secrets discipline (vault-first, least privilege, nothing leaks through logs/commits), security-by-design principles, risk-based finding classification |
| `requesting-code-review` | Dispatch a reviewer with precisely crafted context |
| `receiving-code-review` | Verify feedback before implementing; technical rigor over performative agreement |
| `finishing-a-development-branch` | Verify tests, choose merge/PR/discard, clean up workspaces |

Flow: plan → `subagent-driven-development` (or `executing-plans`) → uses
`test-driven-development` + `requesting-code-review` /
`receiving-code-review` per task → `finishing-a-development-branch`.
`session-ledger` runs throughout every implementation session;
`security-principles` activates whenever work touches credentials,
auth, or sensitive data.

Process artifacts (ledgers, briefs, review packages) live in the target
repo's `.constraint-kit/sdd/<plan>/` — git-ignored scratch, recoverable
from git history.

## Agents

- **conductor** — orchestrates subagent-driven development; never edits
  code itself.
- **implementer** — executes one task at a time with strict TDD.
- **reviewer** — reviews diffs for spec compliance and quality; changes
  nothing.

## Credits

Skills adapted from [obra/superpowers](https://github.com/obra/superpowers)
(`test-driven-development`, `subagent-driven-development`,
`executing-plans`, `requesting-code-review`, `receiving-code-review`,
`finishing-a-development-branch`) and
[mattpocock/skills](https://github.com/mattpocock/skills) (`tdd` — seams,
anti-patterns, mocking guidance). `session-ledger` is modernized from
constraint-kit's own pre-2.0 `session-hygiene` skill, its session
history re-homed from `agent-base.yaml` to `.constraint-kit/PROJECT.md`. `security-principles`
merges constraint-kit's pre-2.0 `security-compliance` skill with the
core principles of
[davila7/claude-code-templates](https://github.com/davila7/claude-code-templates)'
`security-compliance` skill. See each SKILL.md for details.
