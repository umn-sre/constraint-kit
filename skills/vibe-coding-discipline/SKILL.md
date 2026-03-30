# Skill: Vibe-Coding Discipline

## Purpose

Prevent workslop: code that looks correct but violates project
standards, ignores established patterns, introduces unapproved
dependencies, cannot be verified, or asserts the existence of
APIs and methods that have not been confirmed. Apply at the start
of any code generation session where the project has established
conventions.

## When This Skill Is Active

Any code generation session — greenfield, brownfield, or debugging —
where the project has existing modules, approved dependencies,
linting rules, or testing requirements that generated code must
comply with. Especially important when the codebase has a patterns
file, pyproject.toml constraints, or an approved library list.

## Agent Behavior

- Read existing modules in the relevant package or directory before
  writing any new code. Match function signatures, docstring style,
  import order, error handling, and module structure to what already
  exists.
- State the test for any new function before writing the function.
  Do not propose a function that cannot be tested without a live
  network connection or external service unless dependency injection
  is explicitly designed in.
- Do not use any API, method, or library function that cannot be
  confirmed to exist in the approved dependencies. If uncertain,
  say so explicitly and ask before proceeding.
- Do not add a dependency not present in the project's approved
  list. Name the dependency, explain why it is needed, and wait
  for explicit approval before writing any code that requires it.
- Use only approved wrappers and utilities. If the project has an
  approved HTTP client, logger, or config loader, use those — do
  not import the underlying library directly.
- When debugging, diagnose the actual cause before writing a fix.
  Do not use bare exception handlers to mask errors. If the root
  cause is unclear from provided evidence, say so and ask.
- Do not introduce a code pattern — error handling style, logging
  approach, configuration method — that has no precedent in the
  existing codebase without flagging it as a new pattern and
  getting confirmation.

## Anti-Patterns

- Writing a new function before reading the module it will live in.
- Using `except Exception: pass` or any bare exception swallowing
  to hide an error rather than fix it.
- Hardcoding credentials, hostnames, URLs, or any value that
  belongs in configuration.
- Using `print()` instead of the project's approved logger.
- Importing `httpx`, `aiohttp`, `urllib3`, or any unapproved HTTP
  library when an approved wrapper exists.
- Inventing a response schema for an external API without
  confirming it from provided documentation.
- Proposing a function and then noting "you'll need to mock this
  for testing" without providing the mock or redesigning for
  testability.
- Adding a new top-level dependency without approval, even if
  it is widely used and well-regarded.

## Transition

Do not generate code until the function's test approach has been
stated. Do not use an external API response field until its
structure has been confirmed from provided documentation or a
sample response. Do not proceed past a dependency question until
the user has explicitly approved or rejected the dependency.
