# Python Compliance Script - Complete Automation Reference

## Overview

This document details every automated fix the compliance script performs
and indicates what can vs. cannot be fully automated.

## Fully Automated Fixes ✓

These issues are **completely automated** with no manual intervention needed:

### Import Management

- ✓ **Remove unused imports** - autoflake
- ✓ **Remove unused variables** - autoflake
- ✓ **Sort imports** - isort with black profile
- ✓ **Add missing common imports** - custom logic for stdlib modules
- ✓ **Remove duplicate imports** - autoflake

### Code Formatting

- ✓ **Fix line length violations** - black (wraps long lines)
- ✓ **Remove trailing whitespace** - custom logic
- ✓ **Ensure single final newline** - custom logic
- ✓ **Fix indentation** - black
- ✓ **Standardize quote usage** - black

### String & Encoding

- ✓ **Fix logging f-string interpolation** - converts to % formatting

  ```python
  # Before: logging.info(f"Value: {value}")
  # After:  logging.info("Value: %s", value)
  ```

- ✓ **Add encoding to open() calls** - adds encoding='utf-8'

  ```python
  # Before: open("file.txt", "r")
  # After:  open("file.txt", "r", encoding="utf-8")
  ```

- ✓ **Modernize string formatting** - converts % and .format() to f-strings (except logging)

  ```python
  # Before: "Hello %s" % name
  # After:  f"Hello {name}"
  ```

### Comparisons & Conditionals

- ✓ **Fix None comparisons** - use `is`/`is not` instead of `==`/`!=`

  ```python
  # Before: if x == None:
  # After:  if x is None:
  ```

- ✓ **Fix True/False comparisons** - simplify boolean checks

  ```python
  # Before: if x == True:
  # After:  if x:
  ```

- ✓ **Fix type comparisons** - use isinstance() instead of type()

  ```python
  # Before: if type(x) == str:
  # After:  if isinstance(x, str):
  ```

### Exception Handling

- ✓ **Fix bare except clauses** - add Exception type

  ```python
  # Before: except:
  # After:  except Exception:
  ```

### Code Structure

- ✓ **Remove unnecessary else after return** - flatten code structure

  ```python
  # Before:
  if condition:
      return value
  else:
      do_something()

  # After:
  if condition:
      return value
  do_something()
  ```

- ✓ **Fix redundant comprehensions** - remove unnecessary wrapping

  ```python
  # Before: list([x for x in items])
  # After:  [x for x in items]
  ```

### Documentation

- ✓ **Add module docstrings** - adds placeholder at top of file
- ✓ **Add function docstrings** - adds TODO placeholders for missing ones

## Partially Automated (Detection + Warnings) ⚠️

These issues are **detected** and **logged as warnings** but require manual fixes:

### Variable Issues

- ⚠️ **Undefined variables** - detects via AST analysis

  - Automatically fixes if in COMMON_IMPORTS list
  - Warns about others for manual review
  - Cannot auto-fix: typos, scope issues, complex flows

### Code Quality

- ⚠️ **Mutable default arguments** - detects but warns only

  ```python
  # Detected and warned:
  def func(x=[]):  # Mutable default!
      pass

  # Manual fix needed:
  def func(x=None):
      x = x if x is not None else []
  ```

## Cannot Be Automated ✗

These require human judgment and cannot be reliably automated:

### Semantic Issues

- ✗ **Incorrect logic** - requires understanding intent
- ✗ **Wrong algorithm** - needs domain knowledge
- ✗ **Security vulnerabilities** - context-dependent
- ✗ **Performance issues** - depends on use case

### Documentation Quality

- ✗ **Meaningful docstrings** - script adds placeholders only
- ✗ **Accurate type hints** - requires understanding data flow
- ✗ **Useful comments** - needs human insight

### Design Issues

- ✗ **Too many arguments** - needs refactoring judgment
- ✗ **Function too complex** - requires decomposition strategy
- ✗ **Poor naming** - needs semantic understanding
- ✗ **Circular imports** - requires architectural changes

### Business Logic

- ✗ **Edge case handling** - domain-specific
- ✗ **Error message clarity** - user-facing concerns
- ✗ **API compatibility** - requires version awareness

## Ruff/Pylint Rules Coverage

### Fully Covered (Automated)

| Ruff Code | Pylint Code | Description | Automation |
|-----------|-------------|-------------|------------|
| E501 | C0301 | Line too long | ✓ black |
| W291 | C0303 | Trailing whitespace | ✓ custom |
| W292 | C0304 | No newline at end of file | ✓ custom |
| F401 | W0611 | Unused import | ✓ autoflake |
| F841 | W0612 | Unused variable | ✓ autoflake |
| I001 | C0411 | Unsorted imports | ✓ isort |
| D100 | C0114 | Missing module docstring | ✓ custom |
| D103 | C0116 | Missing function docstring | ✓ custom |
| E711 | - | Comparison to None | ✓ custom |
| E712 | - | Comparison to True/False | ✓ custom |
| W605 | - | Invalid escape sequence | ✓ black |
| UP003 | - | Use UTF-8 encoding | ✓ custom |
| G001 | - | Logging f-string | ✓ custom |
| SIM102 | - | Unnecessary else after return | ✓ custom |
| C417 | - | Unnecessary list/set/dict call | ✓ custom |
| E722 | W0702 | Bare except | ✓ custom |
| E721 | - | Type comparison | ✓ custom |

### Partially Covered (Detected)

| Ruff Code | Pylint Code | Description | Automation |
|-----------|-------------|-------------|------------|
| F821 | E0602 | Undefined name | ⚠️ detect + warn |
| B006 | W0102 | Mutable default argument | ⚠️ detect + warn |

### Not Covered (Manual)

| Ruff Code | Pylint Code | Description | Why Manual? |
|-----------|-------------|-------------|-------------|
| C901 | R1260 | Function too complex | Needs refactoring judgment |
| PLR0913 | R0913 | Too many arguments | Design decision |
| PLR0912 | R0912 | Too many branches | Needs restructuring |
| N806 | C0103 | Invalid variable name | Semantic understanding |
| S105 | - | Hardcoded password | Context-dependent |
| S608 | - | SQL injection | Security analysis needed |

## Practical Automation Limits

### What We Can Achieve: ~85% Automation

Based on typical Python codebases:

**Fully Automated (60-70% of issues):**

- All formatting issues
- Import organization
- Simple structural improvements
- Obvious anti-patterns

**Semi-Automated (15-25% of issues):**

- Detection + warnings for review
- Suggestions for fixes
- Pattern identification

**Manual Required (10-15% of issues):**

- Design decisions
- Business logic
- Security concerns
- Semantic naming

### Typical Results on Real Code

After running the compliance script on a typical Python file:

```

Before:
- 50 lint issues from ruff
- 30 style issues from pylint
- 10 documentation warnings

After:
- 5-8 remaining issues (mostly design/logic)
- All formatting perfect
- All structural issues fixed
- Documentation stubs present

```

## Extending the Script

### Adding New Fixes

To add a new automated fix:

1. **Create a fix function:**

```python

def fix_new_issue(filepath: Path) -> bool:
    \"\"\"Fix the new issue.\"\"\"
    # Read file
    # Apply transformation
    # Write if changed
    # Return True if changed

```

1. **Add to compliance checks:**

```python

steps = [
    # ... existing steps ...
    ("Fix new issue", lambda: fix_new_issue(filepath)),
]

```

1. **Test thoroughly:**

```bash

# Test on sample files

python pycompliance_v2.py test_file.py

# Verify output

ruff check test_file.py

```

## Priority for New Automations

Focus on automations that are:
1. **Unambiguous** - single correct fix
2. **Safe** - won't break working code
3. **High-frequency** - common issues
4. **Low-complexity** - reliable detection

## Integration with Agents/AI

### What Agents Should Still Do

Even with comprehensive automation, agents are valuable for:

1. **Complex refactoring** - multi-file changes
2. **Algorithm optimization** - performance improvements
3. **Test generation** - comprehensive test coverage
4. **Documentation enrichment** - meaningful docstrings
5. **Architecture decisions** - design patterns

### Optimal Workflow

```

1. Run pycompliance_v2.py (automated fixes)
   ↓
2. Review remaining warnings
   ↓
3. Use agent for:
   - Complex issues
   - Design questions
   - Test coverage
   ↓
4. Final validation with ruff/pylint

```

## Performance Considerations

### Script Performance

On a typical Python file (300 lines):

- Runtime: 2-5 seconds
- Most time spent in: black > isort > autoflake

### Optimization Tips

```bash

# Parallel processing for multiple files

python batch_comply.py ./src -j 4

# Skip expensive checks if not needed

# Edit pycompliance_v2.py to comment out steps

# Cache results in CI/CD

# Only run on changed files

git diff --name-only | grep '\.py$' | xargs -I {} python pycompliance_v2.py {}

```

## Summary: Automation Coverage

| Category | Automation | Notes |
|----------|-----------|-------|
| Formatting | 100% | All handled by black |
| Imports | 95% | Except complex aliasing |
| Simple patterns | 90% | Most anti-patterns fixed |
| Documentation structure | 80% | Stubs only, content manual |
| Code quality | 70% | Detection > fixes |
| Logic/design | 0% | Requires human judgment |
| **Overall** | **~85%** | Of typical lint issues |

## Conclusion

The comprehensive compliance script automates the vast majority of mechanical
code quality issues, allowing developers and AI agents to focus on
higher-value activities like architecture, algorithms, and business logic.

For maximum productivity:

1. **Run automation first** - handles 85% of issues
2. **Review warnings** - address detected issues
3. **Use agents wisely** - for complex problems only
4. **Focus on semantics** - meaningful code, not just clean code
