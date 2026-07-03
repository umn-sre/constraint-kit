# Superpowers Skills

> Superpowers is a core skills library for AI coding agents: TDD, debugging, collaboration patterns, and proven techniques.
> Repository: https://github.com/obra/superpowers

## Available Skills

### brainstorming
You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.

### dispatching-parallel-agents
Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies.

### executing-plans
Use when you have a written implementation plan to execute in a separate session with review checkpoints.

### finishing-a-development-branch
Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup.

### receiving-code-review
Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation.

### requesting-code-review
Use when completing tasks, implementing major features, or before merging to verify work meets requirements.

### subagent-driven-development
Use when executing implementation plans with independent tasks in the current session. Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

### systematic-debugging
Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes. Four phases: Root Cause Investigation → Pattern Analysis → Hypothesis and Testing → Implementation.

### test-driven-development
Use when implementing any feature or bugfix, before writing implementation code. Write the test first. Watch it fail. Write minimal code to pass. No production code without a failing test first.

### using-git-worktrees
Use when starting any new development work to ensure an isolated workspace. Creates or verifies a git worktree for feature development.

### using-superpowers
Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions.

### verification-before-completion
Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always.

### writing-plans
Use when you have a spec or requirements for a multi-step task, before touching code. Write comprehensive implementation plans assuming the engineer has zero context.

### writing-skills
Use when creating new skills or modifying existing ones. Skills are code that shapes agent behavior, not prose.

## How to Use

1. **Automatic Triggering**: When the user's request matches a skill's description, invoke the skill automatically.
2. **Manual Request**: If the user explicitly asks to use a skill, invoke it immediately.
3. **Always Check**: If there's even a 1% chance a skill might apply, invoke it to check.

## Skill Priority

When multiple skills could apply:
1. Process skills first (brainstorming, systematic-debugging) - these determine HOW to approach the task
2. Implementation skills second (writing-plans, test-driven-development) - these guide execution

## Integration with Superpowers

**Core workflow:**
1. Start with `using-superpowers` to understand how to use skills
2. Use `brainstorming` for creative/planning work
3. Use `writing-plans` to create implementation plans
4. Use `subagent-driven-development` or `executing-plans` to implement
5. Use `test-driven-development` during implementation
6. Use `systematic-debugging` for any issues
7. Use `verification-before-completion` before claiming success
8. Use `requesting-code-review` or `finishing-a-development-branch` to complete

**Critical rules:**
- NO production code without TDD (test-driven-development)
- NO fixes without root cause investigation (systematic-debugging)
- NO completion claims without fresh verification (verification-before-completion)
- Always use brainstorming before creative work
