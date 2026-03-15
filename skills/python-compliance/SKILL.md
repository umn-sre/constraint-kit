# Skill: Python Compliance

## Purpose

Mechanical code quality issues — formatting, imports, bare excepts,
missing docstrings — are noise that obscures real problems. Automating
them frees both human and agent attention for logic, architecture, and
business correctness. Roughly 85% of typical lint issues are mechanical
and can be fixed without human judgment.

## When This Skill Is Active

When writing, reviewing, or modifying any Python file in a
constraint-kit project or extension repo.

## Agent Behavior

### Before generating any Python code

Apply these constraints to every file produced. Do not generate
non-compliant code and expect the author to fix it.

### Fully automated — always apply

These are mechanical fixes with no ambiguity. Apply them in every
generated Python file:

**Imports**

- One import per line
- Stdlib imports first, then third-party, then local — blank line between groups
- No unused imports
- No duplicate imports
- Use `from pathlib import Path` not string manipulation for file paths

**Formatting**

- Max line length: 120 characters (black default)
- 4-space indentation — never tabs
- Trailing whitespace removed
- File ends with exactly one newline
- Quotes: double quotes by default (black standard)

**Docstrings**

- Every module must have a module docstring at the top
- Every public function must have a docstring
- Docstring summary on the first line (PEP 257 / D212)
- Args/Returns sections for functions with parameters

**Encoding**

- All `open()` calls must specify `encoding="utf-8"`
- Unnecessary mode argument `"r"` removed (`open(f)` not `open(f, "r")`)

**Exception handling**

```python

# Never

except:

# Always

except Exception:

# Or specific

except (ValueError, TypeError):

```

**Comparisons**

```python

# Never

if x == None:
if x == True:
if type(x) == str:
if not x == y:

# Always

if x is None:
if x:
if isinstance(x, str):
if x != y:

```

**Logging**

```python

# Never (G001 violation)

logging.info(f"Value: {value}")

# Always

logging.info("Value: %s", value)

```

**Subprocess**

```python

# Always include check=False explicitly (or True if appropriate)

subprocess.run(cmd, shell=True, capture_output=True,
               text=True, check=False)

```

## Detected — flag and ask

These require judgment — detect them and flag before proceeding:

- Mutable default arguments (`def func(x=[])`)
- Undefined variables caught by AST analysis
- Functions over 50 lines — suggest decomposition

### Running compliance locally

```bash

# Fix a single file

python bootstrap/pycompliance.py myfile.py

# Dry run — preview changes without writing

python bootstrap/pycompliance.py myfile.py --dry-run

# Fix an entire directory (parallel)

python bootstrap/batch_comply.py src/ -j 4

# Ruff check after pycompliance

ruff check myfile.py

# Full pipeline

python bootstrap/pycompliance.py myfile.py && ruff check myfile.py

```

## What pycompliance does NOT fix

Do not expect automation to handle these — they require judgment:

- Incorrect logic or wrong algorithms
- Security vulnerabilities
- Function complexity or argument count
- Meaningful docstring content (only stubs are generated)
- Circular imports
- Type hint accuracy

## Anti-Patterns

- Do NOT generate a `bare except:` — always specify `except Exception:`
  or a more specific type
- Do NOT use f-strings in logging calls — use `%s` formatting
- Do NOT open files without `encoding="utf-8"`
- Do NOT compare to `None` with `==` — use `is None`
- Do NOT write code and declare it compliant without running
  `pycompliance.py` and `ruff check`
- Do NOT generate placeholder docstrings (`"""Module docstring."""`)
  and leave them — fill in actual content
- Do NOT import modules at function scope — all imports belong at
  the top of the file

## Transition

After Python compliance is confirmed:

- Run `ruff check` as a final gate before committing
- For test coverage: hand off to `test-driven-development`
- For debugging issues found during compliance: hand off to
  `systematic-debugging`
- For operational readiness of runbooks: hand off to `sre-conventions`
