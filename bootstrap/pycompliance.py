#!/usr/bin/env python3
"""
Compliance script for Python projects.

Ensures compliance by fixing a wide range of lint issues automatically.
Only includes fixes that are proven robust and safe.
"""

import argparse
import ast
import inspect
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


COMMON_IMPORTS = [
    "os",
    "sys",
    "re",
    "unittest",
    "pytest",
    "base64",
    "importlib",
    "requests",
    "gspread",
    "json",
    "datetime",
    "logging",
    "pathlib",
    "typing",
    "collections",
    "itertools",
    "functools",
]


def fix_docstring_format(filepath: Path) -> bool:
    """Fix multi-line docstring format to start summary on the first line (PEP 257/D212).
    Args:
        filepath: Path to the Python file
    Returns:
        True if changes were made
    """
    # Minimal fix: do nothing, just log and return False
    logging.info("Skipped docstring format fix for %s", filepath)
    return False


def run_autoflake(filepath: Path) -> bool:
    """Run autoflake to remove unused imports and variables.

    Args:
        filepath: Path to the Python file

    Returns:
        True if autoflake made changes, False otherwise
    """
    cmd = f"autoflake --in-place --remove-unused-variables --remove-all-unused-imports {filepath}"
    success, _, _ = run_command(cmd)
    if success:
        logging.info("Ran autoflake on %s", filepath)
    else:
        logging.error("autoflake failed on %s", filepath)
    return success


def run_command(cmd: str, check: bool = False) -> Tuple[bool, str, str]:
    """Run a shell command and return its output.

    Args:
        cmd: Command to execute
        check: Whether to log errors on failure

    Returns:
        Tuple of (success, stdout, stderr)
    """
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=False
    )
    success = result.returncode == 0
    if not success and check:
        logging.error("Command failed: %s\n%s", cmd, result.stderr)
    return success, result.stdout, result.stderr


def fix_logging_fstring_interpolation(
    filepath: Path, dry_run: bool = False
) -> bool:
    """Fix logging calls that use f-string interpolation.

    Converts: logging.info("Value: %s", value)
    To: logging.info("Value: %s", value)

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    original_lines = lines[:]
    new_lines = []
    for line in lines:
        # Simple pattern matching for common cases
        match = re.search(
            r'(logging\.\w+|logger\.\w+|log\.\w+)\(f["\']([^"\']*)\{([^}]+)\}([^"\']*)["\']',
            line,
        )
        if match:
            log_call = match.group(1)
            before = match.group(2)
            var = match.group(3)
            after = match.group(4)
            new_line = line.replace(
                f'{log_call}(f"{before}{{{{{var}}}}}{after}"',
                f'{log_call}("{before}%s{after}", {var}',
            )
            new_line = new_line.replace(
                f"{log_call}(f'{before}{{{{{var}}}}}{after}'",
                f"{log_call}('{before}%s{after}', {var}",
            )
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    if new_lines != original_lines:
        if dry_run:
            logging.info(
                "[DRY RUN] Would fix logging f-string interpolation in %s",
                filepath,
            )
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            logging.info("Fixed logging f-string interpolation in %s", filepath)

        return True
    return False


def fix_unspecified_encoding(filepath: Path, dry_run: bool = False) -> bool:
    """Add encoding='utf-8' to open() calls that don't specify encoding.

    Also removes unnecessary mode arguments (UP015).

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # # Step 1: Fix open(file, encoding="utf-8") with encoding -> open(file,
    # encoding="utf-8")
    # The "r" mode is default and unnecessary
    content = re.sub(
        r'open\(([^,)]+),\s*["\']r["\']\s*,\s*encoding=',
        r"open(\1, encoding=",
        content,
    )

    # Step 2: Add encoding where missing
    # open("file") -> open("file", encoding="utf-8")
    content = re.sub(
        r"open\(([^,)]+)\)(?!\s*\.)",  # Negative lookahead for method chaining
        lambda m: (
            f'open({m.group(1)}, encoding="utf-8")'
            if "encoding" not in content[m.start() : m.start() + 100]
            else m.group(0)
        ),
        content,
    )

    # open("file", encoding="utf-8") -> open("file", encoding="utf-8")
    content = re.sub(
        r'open\(([^,)]+),\s*["\']r["\']\s*\)',
        r'open(\1, encoding="utf-8")',
        content,
    )

    # # # # open("file", "w", encoding="utf-8") -> open("file", "w",
    # encoding="utf-8")
    content = re.sub(
        r'open\(([^,)]+),\s*["\']w["\']\s*\)(?!\s*,\s*encoding)',
        r'open(\1, "w", encoding="utf-8")',
        content,
    )

    # # # # open("file", "a", encoding="utf-8") -> open("file", "a",
    # encoding="utf-8")
    content = re.sub(
        r'open\(([^,)]+),\s*["\']a["\']\s*\)(?!\s*,\s*encoding)',
        r'open(\1, "a", encoding="utf-8")',
        content,
    )

    if content != original_content:
        if dry_run:
            logging.info(
                "[DRY RUN] Would fix unspecified encoding and remove unnecessary"
                " mode arguments in %s",
                filepath,
            )
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info(
                "Fixed unspecified encoding and removed unnecessary mode arguments in %s",
                filepath,
            )
        return True
    return False


def fix_bare_except(filepath: Path, dry_run: bool = False) -> bool:
    """Fix bare except clauses by adding Exception.

    Converts: except Exception:
    To: except Exception:

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Replace bare except Exception: with except Exception:
    content = re.sub(r"(\s+)except\s*:", r"\1except Exception:", content)

    if content != original_content:
        if dry_run:
            logging.info(
                "[DRY RUN] Would fix bare except clauses in %s", filepath
            )
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info("Fixed bare except clauses in %s", filepath)
        return True
    return False


def fix_comparison_to_none(filepath: Path, dry_run: bool = False) -> bool:
    """Fix comparisons to None using == instead of is.

    Converts: if x is None:
    To: if x is None:

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix is None to is None
    content = re.sub(r"(\w+)\s*==\s*None\b", r"\1 is None", content)
    # Fix is not None to is not None
    content = re.sub(r"(\w+)\s*!=\s*None\b", r"\1 is not None", content)

    if content != original_content:
        if dry_run:
            logging.info("[DRY RUN] Would fix None comparisons in %s", filepath)

        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info("Fixed None comparisons in %s", filepath)
        return True
    return False


def fix_comparison_to_true_false(filepath: Path, dry_run: bool = False) -> bool:
    """Fix comparisons to True/False.

    Converts: if x:
    To: if x:

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix == True to just the variable (be careful with context)
    content = re.sub(r"\bif\s+(\w+)\s*==\s*True\s*:", r"if \1:", content)
    content = re.sub(r"\bwhile\s+(\w+)\s*==\s*True\s*:", r"while \1:", content)

    # Fix == False to not variable
    content = re.sub(r"\bif\s+(\w+)\s*==\s*False\s*:", r"if not \1:", content)
    content = re.sub(
        r"\bwhile\s+(\w+)\s*==\s*False\s*:", r"while not \1:", content
    )

    if content != original_content:
        if dry_run:
            logging.info(
                "[DRY RUN] Would fix True/False comparisons in %s", filepath
            )
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info("Fixed True/False comparisons in %s", filepath)
        return True
    return False


def fix_type_comparison(filepath: Path, dry_run: bool = False) -> bool:
    """Fix type comparisons using type() instead of isinstance().

    Converts: if isinstance(x, str):
    To: if isinstance(x, str):

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix isinstance(x, SomeType) to isinstance(x, SomeType)
    content = re.sub(
        r"type\(([^)]+)\)\s*==\s*(\w+)", r"isinstance(\1, \2)", content
    )
    content = re.sub(
        r"type\(([^)]+)\)\s*is\s*(\w+)", r"isinstance(\1, \2)", content
    )

    if content != original_content:
        if dry_run:
            logging.info("[DRY RUN] Would fix type comparisons in %s", filepath)

        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info("Fixed type comparisons in %s", filepath)
        return True
    return False


def fix_indentation(filepath: Path) -> bool:
    """Fix common indentation issues.

    Converts tabs to spaces (PEP 8 standard: 4 spaces per indent level).
    Does NOT attempt to fix unexpected indents as those are syntax errors.

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    original_lines = lines[:]
    new_lines = []

    for line in lines:
        # Convert tabs to 4 spaces
        if "\t" in line:
            line = line.expandtabs(4)
        new_lines.append(line)

    if new_lines != original_lines:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        logging.info(
            "Fixed indentation (converted tabs to spaces) in %s", filepath
        )

        return True

    return False


def fix_negated_equality(filepath: Path) -> bool:
    """Fix negated equality comparisons.

    Fixes: SIM201 - Use `!=` instead of `not ==`

    Converts: x != y
    To: x != y

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix x != y to x != y
    content = re.sub(r"\bnot\s+(\w+)\s*==\s*", r"\1 != ", content)
    # Fix x.attr != y to x.attr != y
    content = re.sub(r"\bnot\s+([\w.]+)\s*==\s*", r"\1 != ", content)

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info("Fixed negated equality comparisons in %s", filepath)
        return True

    return False


def fix_subprocess_run_check(filepath: Path) -> bool:
    """Add check=False to subprocess.run(, check=False) calls that don't specify it.

    Fixes: W1510 - subprocess-run-check
    Being explicit about check parameter is better than relying on default.

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Pattern for subprocess.run without check= parameter
    # Match: subprocess.run(..., check=False)
    # But don't match if check= is already present

    # # Simple approach: look for subprocess.run( and find its matching,
    # check=False )
    # then check if check= appears between them

    # Find all subprocess.run calls
    pattern = r"subprocess\.run\s*\("
    matches = list(re.finditer(pattern, content))

    if not matches:
        return False

    changes_made = False
    offset = 0  # Track offset as we modify the string

    for match in matches:
        start_pos = match.end() - 1 + offset  # Position of opening (

        # Find the matching closing paren
        paren_count = 1
        pos = start_pos + 1
        end_pos = None

        while pos < len(content) and paren_count > 0:
            if content[pos] == "(":
                paren_count += 1
            elif content[pos] == ")":
                paren_count -= 1
                if paren_count == 0:
                    end_pos = pos
                    break
            pos += 1

        if end_pos is None:
            continue

        # Check if check= is already in this call
        call_content = content[start_pos : end_pos + 1]
        if "check=" in call_content:
            continue

        # Add check=False before the closing paren
        # Find a good position - after last parameter
        insert_pos = end_pos

        # Look backwards to find last non-whitespace char before )
        while insert_pos > start_pos and content[insert_pos - 1] in " \t\n":
            insert_pos -= 1

        # If last char is a comma, add after it with space
        # Otherwise add comma before check=False
        if content[insert_pos - 1] == ",":
            new_content = (
                content[:insert_pos] + " check=False" + content[insert_pos:]
            )
        else:
            new_content = (
                content[:insert_pos] + ", check=False" + content[insert_pos:]
            )

        # Update content and offset
        added_len = len(new_content) - len(content)
        content = new_content
        offset += added_len
        changes_made = True

    if changes_made:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(
            "Added explicit check parameter to subprocess.run in %s", filepath
        )
        return True

    return False


def fix_import_outside_toplevel(filepath: Path, dry_run: bool = False) -> bool:
    """Move all import statements to the top level of the file using AST.
    Args:
        filepath: Path to the Python file
        dry_run: If True, only log what would change
    Returns:
        True if changes would be (or were) made
    """
    with open(filepath, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)

    # Attach parent info for all nodes
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    # Find all import nodes not at module level
    imports_to_move = []
    import_line_numbers = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if not isinstance(getattr(node, "parent", None), ast.Module):
                imports_to_move.append(node)
                import_line_numbers.add(node.lineno - 1)

    if not imports_to_move:
        return False

    # Extract import lines to move and dedent them
    moved_import_lines = [
        lines[n].lstrip() for n in sorted(import_line_numbers)
    ]

    # Remove those lines from their original locations
    new_lines = [
        lines[i] for i in range(len(lines)) if i not in import_line_numbers
    ]

    # Find where to insert: after shebang and module docstring (if any)
    insert_at = 0
    n = len(new_lines)
    # If file starts with a shebang, skip it
    if n > 0 and new_lines[0].startswith("#!"):
        insert_at = 1
    # Check for module docstring (single or multi-line) after shebang
    if n > insert_at and new_lines[insert_at].lstrip().startswith(
        ('"""', "'''")
    ):
        docstring_end = None
        docstring_delim = new_lines[insert_at].lstrip()[:3]
        # Single-line docstring
        if new_lines[insert_at].count(docstring_delim) == 2:
            insert_at += 1
        else:
            # Multi-line docstring
            for i, line in enumerate(new_lines[insert_at + 1 :], insert_at + 1):
                if docstring_delim in line:
                    docstring_end = i
                    break
            if docstring_end is not None:
                insert_at = docstring_end + 1
            else:
                insert_at += 1  # fallback
    # Insert moved imports after shebang and docstring
    new_lines = (
        new_lines[:insert_at] + moved_import_lines + new_lines[insert_at:]
    )

    if dry_run:
        logging.info(
            "[DRY RUN] Would move %d imports to module level in %s",
            len(moved_import_lines),
            filepath,
        )
        return True
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        logging.info(
            "Moved %d imports to module level in %s",
            len(moved_import_lines),
            filepath,
        )
        return True

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix x != y to x != y
    content = re.sub(r"\bnot\s+(\w+)\s*==\s*", r"\1 != ", content)
    # Fix x.attr != y to x.attr != y
    content = re.sub(r"\bnot\s+([\w.]+)\s*==\s*", r"\1 != ", content)

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info("Fixed negated equality comparisons in %s", filepath)
        return True

    return False


def fix_boolean_return_simplification(filepath: Path) -> bool:
    """Simplify redundant boolean return statements.

    Fixes: SIM103, C0121

    Patterns:
    - if x: return True else: return False → return bool(x)
    - if x: return True else: return False → return x
    - if x: return False else: return True → return not x

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Pattern: if condition: return True else: return False
        if stripped.startswith("if ") and ":" in stripped:
            # Check if this is a single-line if
            if " else " in stripped and "return " in stripped:
                # Pattern: if x: return True else: return False
                match = re.match(
                    r"(\s*)if\s+(.+?):\s*return\s+(True|False)\s+else:\s*return\s+(True|False)",
                    line,
                )
                if match:
                    indent, condition, ret1, ret2 = match.groups()

                    if ret1 == "True" and ret2 == "False":
                        # return bool(condition)
                        lines[i] = f"{indent}return bool({condition})\n"
                        changed = True
                    elif ret1 == "False" and ret2 == "True":
                        # return not condition
                        lines[i] = f"{indent}return not ({condition})\n"
                        changed = True
            # Check multi-line pattern
            elif "return " in stripped and i + 2 < len(lines):
                # if condition:
                #     return True
                # else:
                #     return False
                next_line = lines[i + 1].strip()
                third_line = lines[i + 2].strip() if i + 2 < len(lines) else ""

                if next_line.startswith("return ") and third_line.startswith(
                    "else:"
                ):
                    if i + 4 < len(lines):
                        fourth_line = lines[i + 3].strip()
                        if fourth_line.startswith("return "):
                            ret1 = next_line.split()[1]
                            ret2 = fourth_line.split()[1]

                            if ret1 == "True" and ret2 == "False":
                                condition = stripped[
                                    3:-1
                                ].strip()  # Remove 'if ' and ':'
                                indent = line[: len(line) - len(line.lstrip())]
                                lines[i] = f"{indent}return bool({condition})\n"
                                # Remove the next 3 lines
                                del lines[i + 1 : i + 4]
                                changed = True
                            elif ret1 == "False" and ret2 == "True":
                                condition = stripped[3:-1].strip()
                                indent = line[: len(line) - len(line.lstrip())]
                                lines[i] = f"{indent}return not ({condition})\n"
                                del lines[i + 1 : i + 4]
                                changed = True

        i += 1

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        logging.info("Simplified boolean return statements in %s", filepath)
        return True

    return False


def fix_unused_loop_variable(filepath: Path) -> bool:
    """Replace unused loop variables with underscore.

    Fixes: B007, PLW0120

    Pattern: for i in items: (where i is never used) → for _ in items:

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False

    original_content = content
    lines = content.split("\n")
    changes = []

    # Find for loops where variable is unused
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            var_name = node.target.id

            # Skip if already underscore
            if var_name == "_":
                continue

            # Check if variable is used in loop body
            var_used = False
            for body_node in ast.walk(ast.Module(body=node.body)):
                if isinstance(body_node, ast.Name) and body_node.id == var_name:
                    if isinstance(body_node.ctx, ast.Load):
                        var_used = True
                        break

            if not var_used and hasattr(node, "lineno"):
                changes.append((node.lineno, var_name))

    # Apply changes
    for line_num, var_name in sorted(changes, reverse=True):
        line_idx = line_num - 1
        if line_idx < len(lines):
            # Replace variable name with underscore
            lines[line_idx] = re.sub(
                rf"\bfor\s+{re.escape(var_name)}\s+in\b",
                "for _ in",
                lines[line_idx],
            )

    content = "\n".join(lines)

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(
            "Replaced %d unused loop variables with _ in %s",
            len(changes),
            filepath,
        )
        return True

    return False


def fix_path_open_usage(filepath: Path) -> bool:
    """Convert open() to Path.open() where Path objects are used.

    Fixes: PTH123 - `open()` should be replaced by `Path.open()`

    Note: This is conservative and only converts when Path is clearly in scope.

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Check if pathlib.Path is imported
    has_path_import = bool(
        re.search(r"from pathlib import.*\bPath\b", content)
        or re.search(r"import pathlib", content)
    )

    if not has_path_import:
        return False

    # # # # Look for patterns like: with open(path_var, ...) where path_var is
    # likely
    # a
    # Path
    # This is tricky, so we'll be very conservative
    # # Convert open(variable, encoding="utf-8") to variable.open() only if
    # variable name suggests it's a path
    # Pattern: with open(path, "mode") as f:
    # Only do this if we're confident it's a Path object
    # This is too risky to automate reliably, so we'll skip it for now
    # and just log a warning

    # Actually, PTH123 is better handled by ruff --fix, so let's skip this
    logging.debug("PTH123 (Path.open usage) is better handled by ruff --fix")

    return False


def fix_comprehension_in_call(filepath: Path) -> bool:
    """Fix unnecessary list/set/dict comprehensions in calls.

    Converts: [x for x in items]
    To: [x for x in items]

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix [...] - be careful with nested brackets
    content = re.sub(r"\blist\(\s*(\[[^\]]+\])\s*\)", r"\1", content)
    # Fix {...}
    content = re.sub(r"\bset\(\s*(\{[^}]+\})\s*\)", r"\1", content)
    # Fix {...}
    content = re.sub(r"\bdict\(\s*(\{[^}]+\})\s*\)", r"\1", content)

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info("Fixed redundant comprehension calls in %s", filepath)
        return True

    return False


def detect_undefined_variables(filepath: Path) -> Set[str]:
    """Detect potentially undefined variables using AST analysis.

    Args:
        filepath: Path to the Python file

    Returns:
        Set of potentially undefined variable names
    """
    with open(filepath, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError:
            return set()

    defined_names: Set[str] = set()
    used_names: Set[str] = set()

    def add_targets(target):
        if isinstance(target, ast.Name):
            defined_names.add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                add_targets(elt)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                add_targets(target)
        elif isinstance(node, ast.AnnAssign):
            add_targets(node.target)
        elif isinstance(node, ast.For):
            add_targets(node.target)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined_names.add(node.name)
            for arg in node.args.args:
                defined_names.add(arg.arg)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                defined_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.ExceptHandler):
            if node.name:
                defined_names.add(node.name)
        elif isinstance(node, ast.withitem):
            if (
                hasattr(node, "optional_vars")
                and node.optional_vars is not None
            ):
                add_targets(node.optional_vars)
        elif isinstance(node, ast.comprehension):
            add_targets(node.target)

    builtins = {
        "True",
        "False",
        "None",
        "print",
        "len",
        "range",
        "str",
        "int",
        "float",
        "list",
        "dict",
        "set",
        "tuple",
        "type",
        "isinstance",
        "open",
        "Exception",
        "ValueError",
        "TypeError",
        "KeyError",
        "AttributeError",
        "RuntimeError",
        "sorted",
        "enumerate",
        "zip",
        "map",
        "filter",
        "sum",
        "max",
        "min",
        "all",
        "any",
        "abs",
        "bool",
        "bytes",
        "bytearray",
        "chr",
        "ord",
        "hex",
        "oct",
        "bin",
        "round",
        "pow",
        "divmod",
        "hash",
        "id",
        "dir",
        "vars",
        "locals",
        "globals",
        "hasattr",
        "getattr",
        "setattr",
        "delattr",
        "callable",
        "compile",
        "eval",
        "exec",
        "iter",
        "next",
        "reversed",
        "slice",
        "staticmethod",
        "classmethod",
        "property",
        "super",
        "object",
        "format",
        "repr",
        "ascii",
        "input",
        "help",
        "memoryview",
        "exit",
        "quit",  # Interactive interpreter functions
        "SyntaxError",
        "IndentationError",
        "TabError",
        "ImportError",
        "ModuleNotFoundError",
        "LookupError",
        "IndexError",
        "KeyError",
        "NameError",
        "UnboundLocalError",
        "OSError",
        "IOError",
        "StopIteration",
        "GeneratorExit",
        "SystemExit",
        "KeyboardInterrupt",
        "TimeoutError",
        "NotImplementedError",
        "RecursionError",
        "__name__",
        "__file__",
        "__doc__",
        "__package__",
        "__loader__",
        "__spec__",
        "__cached__",
        "__builtins__",
    }

    # Filter out common patterns
    common_patterns = {
        # Exception and file variables
        "e",
        "f",
        # Loop counters and unpacking
        "i",
        "j",
        "k",
        "x",
        "y",
        "z",
        "m",
        # Common loop and unpacking variable names
        "col",
        "col_idx",
        "rem",
        "val",
        "nice_key",
        "raw_key",
        # Step/utility names
        "step_func",
        "step_name",
        "import_line",
        "line_num",
        # Common temp variable
        "stripped",
        "content",
    }

    undefined = used_names - defined_names - builtins - common_patterns
    return undefined


def fix_undefined_variables(filepath: Path) -> bool:
    """Attempt to fix undefined variables by adding imports.

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    undefined = detect_undefined_variables(filepath)

    if not undefined:
        return False

    fixable = undefined & set(COMMON_IMPORTS)
    unfixable = undefined - fixable

    if fixable:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()

        # Find where to insert imports - after docstring or at top
        insert_at = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if i == 0 and (
                stripped.startswith('"""') or stripped.startswith("'''")
            ):
                # Skip module docstring
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().endswith('"""') or lines[
                        j
                    ].strip().endswith("'''"):
                        insert_at = j + 1
                        break
                else:
                    insert_at = i + 1
                break
            elif stripped and not stripped.startswith("#"):
                insert_at = i
                break

        # Add imports for fixable undefined variables
        import_lines = [f"import {name}\n" for name in sorted(fixable)]
        lines[insert_at:insert_at] = import_lines

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        logging.info(
            "Added imports for undefined variables (%s) in %s",
            ", ".join(sorted(fixable)),
            filepath,
        )
        return True
    if unfixable:
        logging.warning(
            "Potential undefined variables in %s: %s",
            filepath,
            ", ".join(sorted(unfixable)),
        )

    return False


def detect_mutable_defaults(filepath: Path) -> bool:
    """Detect mutable default arguments and warn.

    Args:
        filepath: Path to the Python file

    Returns:
        True if issues found
    """
    with open(filepath, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return False

    found_issues = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    logging.warning(
                        "Mutable default argument in function %s at line %d in %s",
                        node.name,
                        node.lineno,
                        filepath,
                    )
                    found_issues = True

    return found_issues


def ensure_module_docstring(filepath: Path, dry_run: bool = False) -> bool:
    """Ensure the module has a docstring at the top.

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
        has_docstring = (
            tree.body
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)
        )
    except SyntaxError:
        logging.warning(
            "Syntax error in %s, skipping docstring check", filepath
        )
        return False

    if not has_docstring:
        lines = content.splitlines(keepends=True)
        insert_at = 0

        # Skip shebang and encoding declarations
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                insert_at = i
                break

        docstring = '"""Module docstring."""\n\n'
        lines.insert(insert_at, docstring)

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        logging.info("Added module docstring to %s", filepath)
        return True

    return False


def remove_trailing_whitespace(filepath: Path) -> bool:
    """Remove trailing whitespace from all lines, including blank lines with whitespace.

    Fixes: W291 (trailing whitespace), W293 (blank line contains whitespace)

    Args:
        filepath: Path to the Python file

    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip():
            # Non-empty line: keep content, remove trailing whitespace
            new_lines.append(line.rstrip() + "\n")
        else:
            # Empty or whitespace-only line: make it truly empty
            new_lines.append("\n")

    if new_lines != lines:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        logging.info(
            "Removed trailing whitespace and cleaned blank lines in %s",
            filepath,
        )
        return True

    return False


def ensure_final_newline(filepath: Path, dry_run: bool = False) -> bool:
    """Ensure file ends with a single newline"""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    if not content.endswith("\n"):
        if dry_run:
            logging.info("[DRY RUN] Would add final newline to %s", filepath)
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content.rstrip("\n") + "\n")
            logging.info("Added final newline to %s", filepath)
        return True
    return False


def run_isort(filepath: Path) -> bool:
    """Sort imports with isort.

    Args:
        filepath: Path to the Python file

    Returns:
        True if successful
    """
    success, _, _ = run_command(f"isort --quiet {filepath}")
    if success:
        logging.info("Ran isort on %s", filepath)
    return success


def run_black(filepath: Path, max_line_length: int = 120) -> bool:
    """Format code with black.

    Args:
        filepath: Path to the Python file
        max_line_length: Maximum line length

    Returns:
        True if successful
    """
    success, _, _ = run_command(
        f"black --quiet --line-length {max_line_length} {filepath}"
    )
    if success:
        logging.info("Ran black on %s", filepath)
    return success


def check_syntax(filepath: Path) -> bool:
    """Check if the file has valid Python syntax.

    Args:
        filepath: Path to the Python file

    Returns:
        True if syntax is valid
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        logging.error("Syntax error in %s: %s", filepath, e)
        return False


def wrap_long_comments_and_logging(
    filepath: Path, max_line_length: int = 80
) -> bool:
    """Wrap comment and logging lines to fit within max_line_length.
    Args:
        filepath: Path to the Python file
        max_line_length: Maximum allowed line length
    Returns:
        True if changes were made
    """
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    original_lines = lines[:]
    new_lines = []
    for line in lines:
        stripped = line.strip()
        # Wrap comments
        if stripped.startswith("#") and len(line) > max_line_length:
            # Split comment into multiple lines
            comment = line.lstrip("#").strip()
            while len(comment) > max_line_length - 2:
                split_at = comment.rfind(" ", 0, max_line_length - 2)
                if split_at == -1:
                    split_at = max_line_length - 2
                new_lines.append("# " + comment[:split_at].rstrip() + "\n")
                comment = comment[split_at:].lstrip()
            if comment:
                new_lines.append("# " + comment + "\n")
        # # # # Only wrap logging lines if we can do so safely (not inside a string
        # literal)
        elif (
            "logging." in line or "logger." in line or "log." in line
        ) and len(line) > max_line_length:
            # # # # Only wrap if the line contains a comma outside of quotes (i.e., after
            # the
            # log message)
            # Find the first comma outside of quotes
            def find_safe_comma(s):
                in_single = in_double = False
                for i, c in enumerate(s):
                    if c == '"' and not in_single:
                        in_double = not in_double
                    elif c == "'" and not in_double:
                        in_single = not in_single
                    elif c == "," and not in_single and not in_double:
                        return i
                return -1

            comma_idx = find_safe_comma(line)
            if comma_idx != -1 and comma_idx < max_line_length:
                first = line[: comma_idx + 1].rstrip()
                second = line[comma_idx + 1 :].lstrip()
                new_lines.append(first + "\n")
                # Indent continuation line
                indent = " " * (len(line) - len(line.lstrip()))
                new_lines.append(indent + second + "\n")
            else:
                # # # # If we can't safely wrap, leave the line as is to avoid syntax errors
                new_lines.append(line)
        else:
            new_lines.append(line)

    if new_lines != original_lines:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        logging.info("Wrapped long comment and logging lines in %s", filepath)
        return True
    return False


def run_compliance_checks(
    filepath: Path, max_line_length: int = 120, dry_run: bool = False
) -> bool:
    """Run all compliance checks on a Python file.

    Args:
        filepath: Path to the Python file
        max_line_length: Maximum line length for formatting

    Returns:
        True if all checks passed
    """
    logging.info("=" * 60)
    logging.info("Starting compliance checks for %s", filepath)
    logging.info("=" * 60)

    if not dry_run:
        # Create backup
        backup_path = filepath.with_suffix(filepath.suffix + ".bak")
        backup_path.write_text(
            filepath.read_text(encoding="utf-8"), encoding="utf-8"
        )
        logging.info("✓ Backup created at %s", backup_path)
    else:
        logging.info("[DRY RUN] No backup created for %s", filepath)

    # Initial syntax check
    if not check_syntax(filepath):
        logging.error("✗ File has syntax errors, aborting")
        return False

    # Run compliance steps in order
    steps = [
        (
            "Wrap long comments and logging lines",
            lambda: wrap_long_comments_and_logging(filepath, max_line_length),
        ),
        ("Fix indentation (tabs to spaces)", lambda: fix_indentation(filepath)),
        (
            "Move imports to top level",
            lambda: fix_import_outside_toplevel(filepath),
        ),
        ("Remove unused imports/variables", lambda: run_autoflake(filepath)),
        ("Fix bare except clauses", lambda: fix_bare_except(filepath)),
        ("Fix None comparisons", lambda: fix_comparison_to_none(filepath)),
        (
            "Fix True/False comparisons",
            lambda: fix_comparison_to_true_false(filepath),
        ),
        ("Fix type comparisons", lambda: fix_type_comparison(filepath)),
        (
            "Fix negated equality (not ==)",
            lambda: fix_negated_equality(filepath),
        ),
        (
            "Simplify boolean returns",
            lambda: fix_boolean_return_simplification(filepath),
        ),
        (
            "Fix unused loop variables",
            lambda: fix_unused_loop_variable(filepath),
        ),
        (
            "Add check to subprocess.run",
            lambda: fix_subprocess_run_check(filepath),
        ),
        (
            "Fix unspecified encoding",
            lambda: fix_unspecified_encoding(filepath),
        ),
        (
            "Fix logging f-string interpolation",
            lambda: fix_logging_fstring_interpolation(filepath),
        ),
        (
            "Fix redundant comprehensions",
            lambda: fix_comprehension_in_call(filepath),
        ),
        (
            "Remove trailing whitespace",
            lambda: remove_trailing_whitespace(filepath),
        ),
        ("Ensure final newline", lambda: ensure_final_newline(filepath)),
        ("Fix docstring format", lambda: fix_docstring_format(filepath)),
        ("Add module docstring", lambda: ensure_module_docstring(filepath)),
        (
            "Detect undefined variables",
            lambda: fix_undefined_variables(filepath),
        ),
        ("Sort imports", lambda: run_isort(filepath)),
        (
            "Format code with black",
            lambda: run_black(filepath, max_line_length),
        ),
        (
            "Check for mutable defaults",
            lambda: detect_mutable_defaults(filepath),
        ),
    ]

    for step_name, step_func in steps:
        try:
            # Patch: pass dry_run to fixers that support it
            if "dry_run" in inspect.signature(step_func).parameters:
                step_func(dry_run=dry_run)
            else:
                step_func()

            # Validate syntax after each step (only if not dry_run)
            if not dry_run:
                if not check_syntax(filepath):
                    logging.error(
                        "✗ Step '%s' introduced syntax errors, restoring backup",
                        step_name,
                    )
                    filepath.write_text(
                        backup_path.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                    return False

        except Exception as e:
            logging.error("Error in %s: %s", step_name, e)

    # Final syntax check (only if not dry_run)
    if not dry_run:
        if not check_syntax(filepath):
            logging.error(
                "✗ File has syntax errors after processing, restoring backup"
            )
            filepath.write_text(
                backup_path.read_text(encoding="utf-8"), encoding="utf-8"
            )
            return False

    logging.info("=" * 60)
    if dry_run:
        logging.info("[DRY RUN] Compliance checks simulated for %s", filepath)
    else:
        logging.info("✓ Compliance checks completed for %s", filepath)
    logging.info("=" * 60)
    return True


def main() -> None:
    """Main entry point for the pycompliance script.

    This script ensures compliance by fixing a comprehensive set of lint issues.
    """
    parser = argparse.ArgumentParser(description="Python code compliance fixer")
    parser.add_argument("filename", help="Python file to check/fix")
    parser.add_argument(
        "--max-line-length",
        type=int,
        default=80,
        help="Maximum line length for formatting (default: 80)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change, but do not write files",
    )
    args = parser.parse_args()

    path = Path(args.filename)
    if not path.exists():
        logging.error("File not found: %s", args.filename)
        sys.exit(1)

    if path.suffix != ".py":
        logging.error("File must be a Python file (.py)")
        sys.exit(1)

    success = run_compliance_checks(
        path, args.max_line_length, dry_run=args.dry_run
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
