"""
Comprehensive compliance script for Markdown documents.

Enforces strict Markdown lint rules with native auto-fixes. Reads configuration
from .markdownlintrc (JSON/YAML) or pyproject.toml [tool.mdcompliance]. Falls
back to built-in strict defaults when no config file is found.

Usage:
    python mdcompliance.py <file.md> [--max-line-length 100] [--check]
    python mdcompliance.py docs/          # process directory recursively
    python mdcompliance.py --help
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml  # type: ignore[import]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# _TOML_AVAILABLE = False
# try:
#     import tomllib  # stdlib since Python 3.11
#     _TOML_AVAILABLE = True
# except ImportError:
#     try:
#         import tomli as tomllib  # type: ignore[no-redef]  # noqa: F811
#         _TOML_AVAILABLE = True
#     except ImportError:
#         pass
import tomllib  # stdlib since Python 3.11
_TOML_AVAILABLE = True

_YAML_AVAILABLE = False
try:
    import yaml  # type: ignore[import]  # noqa: F811
    _YAML_AVAILABLE = True
except ImportError:
    pass


@dataclass
class MdConfig:
    """Runtime configuration merged from defaults + config file + CLI flags."""

    # Line length
    max_line_length: int = 100
    # Allow longer lines that are bare URLs (no surrounding text)
    allow_long_urls: bool = True

    # Heading rules
    require_h1: bool = True
    require_heading_progression: bool = True  # no skipping levels
    heading_style: str = "atx"  # "atx" (# style) or "setext"

    # Blank lines around headings
    blanks_around_headings: int = 1  # blank lines before AND after

    # Blank lines around fenced code blocks
    blanks_around_fences: int = 1

    # Blank lines around block quotes
    blanks_around_blockquotes: int = 1

    # List indentation (spaces per level)
    list_indent: int = 2

    # Wrap continuation lines at list indent
    wrap_list_continuations: bool = True

    # Trailing whitespace
    no_trailing_spaces: bool = True

    # Trailing punctuation in headings
    no_trailing_punctuation_in_headings: bool = True
    # Characters that are not allowed at end of headings
    heading_no_trailing_chars: str = ".,;:!?"

    # Multiple blank lines → collapse to one
    max_consecutive_blanks: int = 1

    # No horizontal rules (--- / *** / ___) used as document separators
    no_hr: bool = True

    # File must end with a single newline
    final_newline: bool = True

    # No bare URLs (must be in angle brackets or link syntax)
    no_bare_urls: bool = False  # warn only by default; noisy in real docs

    # Ordered list items must use 1. 2. 3. (not all 1.)
    ordered_list_style: str = "ordered"  # "ordered" | "one" | "any"

    # Unordered list marker consistency: "-", "*", "+" or "consistent"
    unordered_list_marker: str = "consistent"

    # No emphasis used as a heading substitute (bold/italic on its own line)
    no_emphasis_as_heading: bool = True

    # Code block language tag required
    fenced_code_language: bool = False  # informational only

    # Rules to skip entirely (markdownlint rule IDs, e.g. ["MD013"])
    disable: List[str] = field(default_factory=list)


def _load_markdownlintrc(path: Path) -> Dict:
    """Load .markdownlintrc — accepts JSON or YAML."""
    text = path.read_text(encoding="utf-8").strip()
    # Try JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    if _YAML_AVAILABLE:
        try:
            data = yaml.safe_load(text)
            if isinstance(data, dict):
                return data
        except yaml.YAMLError:
            pass
    log.warning("Could not parse %s as JSON or YAML — using defaults.", path)
    return {}


def _load_pyproject(path: Path) -> Dict:
    """Load [tool.mdcompliance] section from pyproject.toml."""
    if not _TOML_AVAILABLE:
        log.warning(
            "tomllib/tomli not available; cannot read pyproject.toml."
            " Install tomli for Python < 3.11."
        )
        return {}
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    return data.get("tool", {}).get("mdcompliance", {})


def load_config(search_dir: Path) -> MdConfig:
    """
    Search upward from search_dir for .markdownlintrc or pyproject.toml and
    merge found settings into MdConfig. Built-in strict defaults are the base.
    """
    cfg = MdConfig()
    raw: Dict = {}

    for directory in [search_dir, *search_dir.parents]:
        rc = directory / ".markdownlintrc"
        if rc.exists():
            raw = _load_markdownlintrc(rc)
            log.info("Config loaded from %s", rc)
            break
        toml = directory / "pyproject.toml"
        if toml.exists():
            candidate = _load_pyproject(toml)
            if candidate:
                raw = candidate
                log.info("Config loaded from %s [tool.mdcompliance]", toml)
                break

    # Map raw keys onto the dataclass (best-effort, unknown keys are ignored)
    field_names = {f.name for f in cfg.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    for key, value in raw.items():
        # markdownlint uses MD013.line_length style; support flat keys too
        if key in field_names:
            setattr(cfg, key, value)

    # markdownlint-compatible shorthand overrides
    if "MD013" in raw and isinstance(raw["MD013"], dict):
        cfg.max_line_length = raw["MD013"].get(
            "line_length", cfg.max_line_length
        )
    if "default" in raw and raw["default"] is False:
        # User opted out of everything — respect it but warn
        log.warning(
            "Config sets default=false. All rules disabled except"
            " those explicitly enabled."
        )

    return cfg


# ---------------------------------------------------------------------------
# Violation dataclass
# ---------------------------------------------------------------------------


@dataclass
class Violation:
    """A single lint finding."""

    rule: str
    line: int
    message: str
    fixable: bool = True

    def __str__(self) -> str:
        fix_tag = "[auto-fix]" if self.fixable else "[manual]"
        return f"  Line {self.line:4d}  {self.rule}  {fix_tag}  {self.message}"


# ---------------------------------------------------------------------------
# Detection functions  (return list of Violations)
# ---------------------------------------------------------------------------


def detect_line_length(lines: List[str], cfg: MdConfig) -> List[Violation]:
    """MD013 — line length."""
    if "MD013" in cfg.disable:
        return []
    violations = []
    for i, line in enumerate(lines, 1):
        stripped = line.rstrip("\n")
        if len(stripped) > cfg.max_line_length:
            if cfg.allow_long_urls:
                # Bare URL line: http... with no surrounding prose
                if re.match(r"^\s*<?https?://\S+>?\s*$", stripped):
                    continue
                # Markdown link: [text](url) where url alone is long
                if re.match(r"^\s*\[.*?\]\(https?://\S+\)\s*$", stripped):
                    continue
            violations.append(
                Violation(
                    "MD013",
                    i,
                    f"Line length {len(stripped)} exceeds {cfg.max_line_length}",
                    fixable=False,  # wrapping prose is risky to auto-fix
                )
            )
    return violations


def detect_heading_progression(
    lines: List[str], cfg: MdConfig
) -> List[Violation]:
    """MD001 — heading level should increment by one at a time."""
    if "MD001" in cfg.disable or not cfg.require_heading_progression:
        return []
    violations = []
    prev_level = 0
    for i, line in enumerate(lines, 1):
        m = re.match(r"^(#{1,6})\s", line)
        if m:
            level = len(m.group(1))
            if prev_level > 0 and level > prev_level + 1:
                violations.append(
                    Violation(
                        "MD001",
                        i,
                        f"Heading jumped from H{prev_level} to H{level}"
                        f" (skipped level(s))",
                        fixable=True,
                    )
                )
            prev_level = level
    return violations


def detect_first_heading_h1(lines: List[str], cfg: MdConfig) -> List[Violation]:
    """MD002 — first heading must be H1."""
    if "MD002" in cfg.disable or not cfg.require_h1:
        return []
    for i, line in enumerate(lines, 1):
        if re.match(r"^#{1,6}\s", line):
            if not line.startswith("# "):
                return [
                    Violation(
                        "MD002",
                        i,
                        "First heading is not H1",
                        fixable=False,
                    )
                ]
            return []
    return []


def detect_heading_style(lines: List[str], cfg: MdConfig) -> List[Violation]:
    """MD003 — heading style consistency (ATX vs setext)."""
    if "MD003" in cfg.disable:
        return []
    violations = []
    setext_underlines = re.compile(r"^[=\-]{2,}\s*$")
    for i, line in enumerate(lines, 1):
        if (
            i > 1
            and setext_underlines.match(line)
            and cfg.heading_style == "atx"
        ):
            violations.append(
                Violation(
                    "MD003",
                    i,
                    "Setext-style heading found; use ATX style (# Heading)",
                    fixable=True,
                )
            )
    return violations


def detect_trailing_spaces(lines: List[str], cfg: MdConfig) -> List[Violation]:
    """MD009 — trailing spaces."""
    if "MD009" in cfg.disable or not cfg.no_trailing_spaces:
        return []
    violations = []
    for i, line in enumerate(lines, 1):
        stripped = line.rstrip("\n")
        if stripped != stripped.rstrip():
            violations.append(
                Violation("MD009", i, "Trailing spaces", fixable=True)
            )
    return violations


def detect_multiple_blanks(lines: List[str], cfg: MdConfig) -> List[Violation]:
    """MD012 — multiple consecutive blank lines."""
    if "MD012" in cfg.disable:
        return []
    violations = []
    blank_run = 0
    for i, line in enumerate(lines, 1):
        if line.strip() == "":
            blank_run += 1
            if blank_run > cfg.max_consecutive_blanks:
                violations.append(
                    Violation(
                        "MD012",
                        i,
                        f"Multiple consecutive blank lines"
                        f" (max {cfg.max_consecutive_blanks})",
                        fixable=True,
                    )
                )
        else:
            blank_run = 0
    return violations


def detect_horizontal_rules(lines: List[str], cfg: MdConfig) -> List[Violation]:
    """MD035 / custom — no horizontal rules used as document separators."""
    if "MD035" in cfg.disable or not cfg.no_hr:
        return []
    hr_pattern = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
    violations = []
    for i, line in enumerate(lines, 1):
        if hr_pattern.match(line):
            violations.append(
                Violation(
                    "MD035",
                    i,
                    "Horizontal rule used as document separator",
                    fixable=True,
                )
            )
    return violations


def detect_heading_trailing_punctuation(
    lines: List[str], cfg: MdConfig
) -> List[Violation]:
    """MD026 — no trailing punctuation in headings."""
    if "MD026" in cfg.disable or not cfg.no_trailing_punctuation_in_headings:
        return []
    bad_chars = set(cfg.heading_no_trailing_chars)
    violations = []
    for i, line in enumerate(lines, 1):
        m = re.match(r"^(#{1,6})\s+(.+)", line.rstrip())
        if m and m.group(2)[-1] in bad_chars:
            violations.append(
                Violation(
                    "MD026",
                    i,
                    f"Trailing punctuation '{m.group(2)[-1]}' in heading",
                    fixable=True,
                )
            )
    return violations


def detect_blanks_around_headings(
    lines: List[str], cfg: MdConfig
) -> List[Violation]:
    """MD022 — headings should be surrounded by blank lines."""
    if "MD022" in cfg.disable:
        return []
    violations = []
    n = len(lines)
    for i, line in enumerate(lines):
        if not re.match(r"^#{1,6}\s", line):
            continue
        lineno = i + 1
        # Check line before (skip if first line)
        if i > 0 and lines[i - 1].strip() != "":
            violations.append(
                Violation(
                    "MD022",
                    lineno,
                    "Heading must be preceded by a blank line",
                    fixable=True,
                )
            )
        # Check line after (skip if last line)
        if i < n - 1 and lines[i + 1].strip() != "":
            violations.append(
                Violation(
                    "MD022",
                    lineno,
                    "Heading must be followed by a blank line",
                    fixable=True,
                )
            )
    return violations


def detect_blanks_around_fences(
    lines: List[str], cfg: MdConfig
) -> List[Violation]:
    """MD031 — fenced code blocks surrounded by blank lines."""
    if "MD031" in cfg.disable:
        return []
    violations = []
    n = len(lines)
    fence_pat = re.compile(r"^(`{3,}|~{3,})")
    for i, line in enumerate(lines):
        if not fence_pat.match(line):
            continue
        lineno = i + 1
        if i > 0 and lines[i - 1].strip() != "":
            violations.append(
                Violation(
                    "MD031",
                    lineno,
                    "Fenced code block must be preceded by a blank line",
                    fixable=True,
                )
            )
        if i < n - 1 and lines[i + 1].strip() != "":
            violations.append(
                Violation(
                    "MD031",
                    lineno,
                    "Fenced code block must be followed by a blank line",
                    fixable=True,
                )
            )
    return violations


def detect_emphasis_as_heading(
    lines: List[str], cfg: MdConfig
) -> List[Violation]:
    """MD036 — emphasis used instead of a heading."""
    if "MD036" in cfg.disable or not cfg.no_emphasis_as_heading:
        return []
    # A line that is *only* bold/italic text (no other content)
    emphasis_only = re.compile(
        r"^\s*(\*{1,2}|_{1,2})[^*_\n]+(\*{1,2}|_{1,2})\s*$"
    )
    violations = []
    for i, line in enumerate(lines, 1):
        if emphasis_only.match(line):
            violations.append(
                Violation(
                    "MD036",
                    i,
                    "Emphasis used instead of a heading; use # syntax",
                    fixable=False,
                )
            )
    return violations


def detect_unordered_list_marker(
    lines: List[str], cfg: MdConfig
) -> List[Violation]:
    """MD004 — unordered list marker consistency."""
    if "MD004" in cfg.disable or cfg.unordered_list_marker == "any":
        return []
    list_pat = re.compile(r"^(\s*)([-*+])\s")
    violations = []
    expected: Optional[str] = (
        None
        if cfg.unordered_list_marker == "consistent"
        else cfg.unordered_list_marker
    )
    for i, line in enumerate(lines, 1):
        m = list_pat.match(line)
        if m:
            marker = m.group(2)
            if expected is None:
                expected = marker
            elif marker != expected:
                violations.append(
                    Violation(
                        "MD004",
                        i,
                        f"Unordered list marker '{marker}' inconsistent"
                        f" (expected '{expected}')",
                        fixable=True,
                    )
                )
    return violations


def detect_ordered_list_style(
    lines: List[str], cfg: MdConfig
) -> List[Violation]:
    """MD029 — ordered list item prefix."""
    if "MD029" in cfg.disable or cfg.ordered_list_style == "any":
        return []
    ol_pat = re.compile(r"^(\s*)(\d+)\.\s")
    violations = []
    counter: Dict[int, int] = {}  # indent_level -> expected_number
    for i, line in enumerate(lines, 1):
        m = ol_pat.match(line)
        if m:
            indent = len(m.group(1))
            actual = int(m.group(2))
            if cfg.ordered_list_style == "ordered":
                expected_n = counter.get(indent, 1)
                if actual != expected_n:
                    violations.append(
                        Violation(
                            "MD029",
                            i,
                            f"Ordered list item should be {expected_n},"
                            f" found {actual}",
                            fixable=True,
                        )
                    )
                counter[indent] = expected_n + 1
            elif cfg.ordered_list_style == "one" and actual != 1:
                violations.append(
                    Violation(
                        "MD029",
                        i,
                        f"Ordered list items should all use '1.' (found {actual}.)",
                        fixable=True,
                    )
                )
        else:
            # Reset counters for indent levels deeper than current
            if not re.match(r"^\s", line):
                counter.clear()
    return violations


def detect_no_final_newline(lines: List[str], cfg: MdConfig) -> List[Violation]:
    """MD047 — file should end with a single newline."""
    if "MD047" in cfg.disable or not cfg.final_newline:
        return []
    if not lines:
        return []
    if not lines[-1].endswith("\n"):
        return [
            Violation(
                "MD047",
                len(lines),
                "File must end with a newline",
                fixable=True,
            )
        ]
    return []


# ---------------------------------------------------------------------------
# Fix functions (return modified lines list)
# ---------------------------------------------------------------------------


def fix_trailing_spaces(lines: List[str]) -> List[str]:
    """Strip trailing whitespace from every line."""
    return [
        line.rstrip() + ("\n" if line.endswith("\n") else "") for line in lines
    ]


def fix_multiple_blanks(lines: List[str], max_blanks: int = 1) -> List[str]:
    """Collapse runs of more than max_blanks consecutive blank lines."""
    result: List[str] = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= max_blanks:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    return result


def fix_horizontal_rules(lines: List[str]) -> List[str]:
    """
    Remove horizontal rule lines.

    Horizontal rules used as document separators add visual noise without
    semantic value in ATX-heading structured documents. They are removed
    rather than converted to avoid inserting blank lines that could then
    trigger adjacent-blank violations.
    """
    hr_pattern = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
    return [line for line in lines if not hr_pattern.match(line)]


def fix_heading_trailing_punctuation(
    lines: List[str], bad_chars: str
) -> List[str]:
    """Strip disallowed trailing punctuation from headings."""
    bad_set = set(bad_chars)
    result = []
    for line in lines:
        m = re.match(r"^(#{1,6}\s+)(.+?)(\s*)(\n?)$", line)
        if m:
            prefix, text, ws, nl = m.groups()
            while text and text[-1] in bad_set:
                text = text[:-1]
            result.append(prefix + text + ws + nl)
        else:
            result.append(line)
    return result


def fix_blanks_around_headings(lines: List[str]) -> List[str]:
    """Ensure each ATX heading is surrounded by blank lines."""
    result: List[str] = []
    n = len(lines)
    for i, line in enumerate(lines):
        is_heading = bool(re.match(r"^#{1,6}\s", line))
        if is_heading:
            # Insert blank before if previous non-blank exists
            if result and result[-1].strip() != "":
                result.append("\n")
            result.append(line)
            # Peek ahead: insert blank after if next line is non-blank
            if i < n - 1 and lines[i + 1].strip() != "":
                result.append("\n")
        else:
            result.append(line)
    return result


def fix_blanks_around_fences(lines: List[str]) -> List[str]:
    """Ensure fenced code blocks are surrounded by blank lines."""
    fence_pat = re.compile(r"^(`{3,}|~{3,})")
    result: List[str] = []
    n = len(lines)
    for i, line in enumerate(lines):
        if fence_pat.match(line):
            if result and result[-1].strip() != "":
                result.append("\n")
            result.append(line)
            if i < n - 1 and lines[i + 1].strip() != "":
                result.append("\n")
        else:
            result.append(line)
    return result


def fix_setext_headings(lines: List[str]) -> List[str]:
    """
    Convert setext-style headings to ATX style.

    Setext uses an underline on the line following the heading text:

        My Heading
        ==========   → # My Heading

        Sub Heading
        -----------  → ## Sub Heading
    """
    result: List[str] = []
    i = 0
    while i < len(lines):
        if i + 1 < len(lines):
            current = lines[i].rstrip()
            nxt = lines[i + 1].rstrip()
            if re.match(r"^={2,}$", nxt) and current:
                result.append("# " + current + "\n")
                i += 2
                continue
            if re.match(r"^-{2,}$", nxt) and current:
                result.append("## " + current + "\n")
                i += 2
                continue
        result.append(lines[i])
        i += 1
    return result


def fix_heading_progression(lines: List[str]) -> List[str]:
    """
    Fix skipped heading levels by reducing the level to one past the previous.

    Example: H1 → H3 becomes H1 → H2.
    This is conservative: it only reduces the level, never promotes headings.
    """
    result: List[str] = []
    prev_level = 0
    for line in lines:
        m = re.match(r"^(#{1,6})(\s.+)$", line.rstrip("\n"))
        if m:
            level = len(m.group(1))
            rest = m.group(2)
            if prev_level > 0 and level > prev_level + 1:
                level = prev_level + 1
            prev_level = level
            result.append("#" * level + rest + "\n")
        else:
            result.append(line)
    return result


def fix_unordered_list_markers(lines: List[str], marker: str) -> List[str]:
    """Normalise all unordered list bullets to the same marker character."""
    list_pat = re.compile(r"^(\s*)([-*+])(\s.+)$")
    # Determine expected marker if "consistent" — use first found
    expected = marker
    if expected == "consistent":
        for line in lines:
            m = list_pat.match(line.rstrip("\n"))
            if m:
                expected = m.group(2)
                break
        if expected == "consistent":
            expected = "-"  # nothing found, default to dash

    result = []
    for line in lines:
        m = list_pat.match(line.rstrip("\n"))
        if m:
            result.append(m.group(1) + expected + m.group(3) + "\n")
        else:
            result.append(line)
    return result


def fix_ordered_list_numbering(
    lines: List[str], style: str = "ordered"
) -> List[str]:
    """Renumber ordered lists sequentially."""
    if style == "any":
        return lines
    ol_pat = re.compile(r"^(\s*)(\d+)(\.\s.+)$")
    result: List[str] = []
    counter: Dict[int, int] = {}
    for line in lines:
        m = ol_pat.match(line.rstrip("\n"))
        if m:
            indent = len(m.group(1))
            rest = m.group(3)
            if style == "one":
                new_n = 1
            else:  # ordered
                new_n = counter.get(indent, 1)
                counter[indent] = new_n + 1
            # Reset deeper indents when we see a shallower item
            for k in list(counter.keys()):
                if k > indent:
                    del counter[k]
            result.append(m.group(1) + str(new_n) + rest + "\n")
        else:
            if not re.match(r"^\s", line):
                counter.clear()
            result.append(line)
    return result


def fix_final_newline(lines: List[str]) -> List[str]:
    """Ensure the file ends with exactly one newline."""
    if not lines:
        return ["\n"]
    # Strip extra blank lines at end
    while len(lines) > 1 and lines[-1].strip() == "":
        lines = lines[:-1]
    if not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    return lines


# ---------------------------------------------------------------------------
# Main compliance pipeline
# ---------------------------------------------------------------------------


def run_checks(lines: List[str], cfg: MdConfig) -> List[Violation]:
    """Run all detectors and return a combined, sorted list of violations."""
    all_violations: List[Violation] = []
    detectors = [
        detect_trailing_spaces,
        detect_multiple_blanks,
        detect_horizontal_rules,
        detect_heading_trailing_punctuation,
        detect_blanks_around_headings,
        detect_blanks_around_fences,
        detect_line_length,
        detect_heading_progression,
        detect_first_heading_h1,
        detect_heading_style,
        detect_emphasis_as_heading,
        detect_unordered_list_marker,
        detect_ordered_list_style,
        detect_no_final_newline,
    ]
    for detector in detectors:
        try:
            all_violations.extend(detector(lines, cfg))
        except Exception as exc:
            log.error("Detector %s raised: %s", detector.__name__, exc)
    all_violations.sort(key=lambda v: v.line)
    return all_violations


def apply_fixes(lines: List[str], cfg: MdConfig) -> Tuple[List[str], int]:
    """
    Apply all auto-fixable transformations in a safe order.

    Returns the fixed lines and a count of fix passes applied.
    """
    fixes_applied = 0

    # Order matters: setext → ATX must happen before blanks-around-headings
    steps = [
        ("setext → ATX conversion", lambda ln: fix_setext_headings(ln)),
        (
            "heading progression",
            lambda ln: (
                fix_heading_progression(ln)
                if cfg.require_heading_progression
                else ln
            ),
        ),
        (
            "trailing punctuation in headings",
            lambda ln: (
                fix_heading_trailing_punctuation(
                    ln, cfg.heading_no_trailing_chars
                )
                if cfg.no_trailing_punctuation_in_headings
                else ln
            ),
        ),
        (
            "horizontal rules",
            lambda ln: fix_horizontal_rules(ln) if cfg.no_hr else ln,
        ),
        (
            "blanks around headings",
            lambda ln: fix_blanks_around_headings(ln),
        ),
        (
            "blanks around fences",
            lambda ln: fix_blanks_around_fences(ln),
        ),
        (
            "unordered list markers",
            lambda ln: fix_unordered_list_markers(
                ln, cfg.unordered_list_marker
            ),
        ),
        (
            "ordered list numbering",
            lambda ln: fix_ordered_list_numbering(ln, cfg.ordered_list_style),
        ),
        (
            "collapse multiple blank lines",
            lambda ln: fix_multiple_blanks(ln, cfg.max_consecutive_blanks),
        ),
        (
            "trailing spaces",
            lambda ln: (
                fix_trailing_spaces(ln) if cfg.no_trailing_spaces else ln
            ),
        ),
        (
            "final newline",
            lambda ln: fix_final_newline(ln) if cfg.final_newline else ln,
        ),
    ]

    for step_name, step_fn in steps:
        try:
            new_lines = step_fn(lines)
            if new_lines != lines:
                log.info("  ✓ Applied fix: %s", step_name)
                fixes_applied += 1
            lines = new_lines
        except Exception as exc:
            log.error("Fix step '%s' failed: %s", step_name, exc)

    return lines, fixes_applied


def process_file(
    filepath: Path, cfg: MdConfig, check_only: bool = False
) -> Tuple[bool, List[Violation]]:
    """
    Process a single Markdown file.

    In check_only mode violations are reported but the file is not written.
    Returns (clean, violations).
    """
    log.info("=" * 60)
    log.info("Processing: %s", filepath)
    log.info("=" * 60)

    with open(filepath, encoding="utf-8") as fh:
        original_lines = fh.readlines()

    # --- Pre-fix violation report ---
    pre_violations = run_checks(original_lines, cfg)

    if not pre_violations:
        log.info("✓ No violations found in %s", filepath)
        return True, []

    log.info("Found %d violation(s):", len(pre_violations))
    for v in pre_violations:
        log.info("%s", v)

    if check_only:
        manual = [v for v in pre_violations if not v.fixable]
        if manual:
            log.warning(
                "%d violation(s) require manual correction.", len(manual)
            )

        return False, pre_violations

    # --- Backup ---
    backup = filepath.with_suffix(filepath.suffix + ".bak")
    backup.write_text("".join(original_lines), encoding="utf-8")
    log.info("Backup → %s", backup)

    # --- Apply fixes ---
    fixed_lines, n_fixes = apply_fixes(original_lines, cfg)

    # --- Post-fix violation report ---
    post_violations = run_checks(fixed_lines, cfg)
    remaining_auto = [v for v in post_violations if v.fixable]
    remaining_manual = [v for v in post_violations if not v.fixable]

    if remaining_auto:
        log.warning(
            "%d auto-fixable violation(s) remain after fixes"
            " (may require a second pass):",
            len(remaining_auto),
        )
        for v in remaining_auto:
            log.warning("%s", v)

    if remaining_manual:
        log.warning(
            "%d violation(s) require manual correction:", len(remaining_manual)
        )

        for v in remaining_manual:
            log.warning("%s", v)

    # Write fixed file
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.writelines(fixed_lines)

    log.info(
        "✓ %s updated (%d fix pass(es) applied, %d violation(s) remain).",
        filepath,
        n_fixes,
        len(post_violations),
    )
    return len(post_violations) == 0, post_violations


def process_directory(
    directory: Path, cfg: MdConfig, check_only: bool = False
) -> bool:
    """Recursively process all .md files under directory."""
    md_files = sorted(directory.rglob("*.md"))
    if not md_files:
        log.warning("No .md files found under %s", directory)
        return True

    all_clean = True
    for md_file in md_files:
        clean, _ = process_file(md_file, cfg, check_only=check_only)
        if not clean:
            all_clean = False
    return all_clean


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Markdown compliance auto-fixer (mdcompliance)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mdcompliance.py README.md
  python mdcompliance.py docs/ --check
  python mdcompliance.py README.md --max-line-length 80
  python mdcompliance.py README.md --no-hr --unordered-marker -
        """,
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Markdown file or directory to process",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report violations only; do not modify files",
    )
    parser.add_argument(
        "--max-line-length",
        type=int,
        default=None,
        metavar="N",
        help="Override maximum line length (default: 100)",
    )
    parser.add_argument(
        "--no-hr",
        action="store_true",
        default=None,
        help="Remove horizontal rules (document separators)",
    )
    parser.add_argument(
        "--unordered-marker",
        choices=["-", "*", "+", "consistent"],
        default=None,
        metavar="CHAR",
        help="Enforce unordered list marker (-|*|+|consistent)",
    )
    parser.add_argument(
        "--disable",
        nargs="*",
        metavar="RULE",
        help="Disable specific rules (e.g. --disable MD013 MD035)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for mdcompliance."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    target: Path = args.target
    if not target.exists():
        log.error("Target not found: %s", target)
        sys.exit(1)

    # Load config from file hierarchy
    search_dir = target if target.is_dir() else target.parent
    cfg = load_config(search_dir)

    # Apply CLI overrides
    if args.max_line_length is not None:
        cfg.max_line_length = args.max_line_length
    if args.no_hr:
        cfg.no_hr = True
    if args.unordered_marker is not None:
        cfg.unordered_list_marker = args.unordered_marker
    if args.disable:
        cfg.disable = args.disable

    log.info(
        "Config: max_line_length=%d, no_hr=%s, ul_marker=%s, disabled=%s",
        cfg.max_line_length,
        cfg.no_hr,
        cfg.unordered_list_marker,
        cfg.disable or "none",
    )

    if target.is_dir():
        clean = process_directory(target, cfg, check_only=args.check)
    else:
        if target.suffix.lower() not in (".md", ".markdown"):
            log.error(
                "File must be a Markdown file (.md / .markdown): %s", target
            )

            sys.exit(1)
        clean, _ = process_file(target, cfg, check_only=args.check)

    sys.exit(0 if clean else 1)


if __name__ == "__main__":
    main()
