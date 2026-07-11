#!/usr/bin/env python3
"""
Batch compliance processor for Python projects.

Processes multiple Python files in a directory tree with parallel execution support.
"""

import argparse
import logging
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def find_python_files(
    directory: Path, exclude_patterns: Optional[List[str]] = None
) -> List[Path]:
    """
    Find all Python files in a directory tree.

    Args:
        directory: Root directory to search
        exclude_patterns: List of patterns to exclude (e.g., ['venv', '__pycache__', '.git'])

    Returns:
        List of Path objects for Python files
    """
    if exclude_patterns is None:
        exclude_patterns = [
            "venv",
            ".venv",
            "__pycache__",
            ".git",
            "build",
            "dist",
            ".eggs",
        ]

    python_files = []
    for path in directory.rglob("*.py"):
        # Check if any exclude pattern is in the path
        if any(pattern in str(path) for pattern in exclude_patterns):
            continue
        python_files.append(path)

    return python_files


def process_file(
    filepath: Path, max_line_length: int = 120
) -> tuple[Path, bool, str]:
    """
    Process a single Python file.

    Args:
        filepath: Path to Python file
        max_line_length: Maximum line length

    Returns:
        Tuple of (filepath, success, message)
    """

    cmd = [
        sys.executable,
        "bootstrap/pycompliance.py",
        str(filepath),
        str(max_line_length),
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, check=False
        )
        success = result.returncode == 0
        message = result.stdout if success else result.stderr
        return filepath, success, message
    except subprocess.TimeoutExpired:
        return filepath, False, "Timeout after 60 seconds"
    except Exception as e:
        return filepath, False, str(e)


def main() -> None:
    """Main entry point for batch compliance processor."""
    parser = argparse.ArgumentParser(
        description="Batch process Python files for compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory to process (searches recursively)",
    )
    parser.add_argument(
        "-l",
        "--line-length",
        type=int,
        default=120,
        help="Maximum line length (default: 120)",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=1,
        help="Number of parallel jobs (default: 1)",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        help="Additional patterns to exclude (can be specified multiple times)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show files that would be processed without processing them",
    )

    args = parser.parse_args()

    if not args.directory.exists():
        logging.error("Directory not found: %s", args.directory)
        sys.exit(1)

    if not args.directory.is_dir():
        logging.error("Not a directory: %s", args.directory)
        sys.exit(1)

    # Find Python files
    exclude_patterns = [
        "venv",
        ".venv",
        "__pycache__",
        ".git",
        "build",
        "dist",
        ".eggs",
    ]
    if args.exclude:
        exclude_patterns.extend(args.exclude)

    logging.info("Searching for Python files in %s", args.directory)
    python_files = find_python_files(args.directory, exclude_patterns)

    if not python_files:
        logging.warning("No Python files found")
        sys.exit(0)

    logging.info("Found %d Python files", len(python_files))

    if args.dry_run:
        for filepath in python_files:
            print(filepath)
        sys.exit(0)

    # Process files
    success_count = 0
    failure_count = 0

    if args.jobs == 1:
        # Serial processing
        for filepath in python_files:
            logging.info("Processing %s", filepath)
            _, success, message = process_file(filepath, args.line_length)
            if success:
                success_count += 1
            else:
                failure_count += 1
                logging.error("Failed to process %s: %s", filepath, message)
    else:
        # Parallel processing
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(
                    process_file, filepath, args.line_length
                ): filepath
                for filepath in python_files
            }

            for future in as_completed(futures):
                filepath = futures[future]
                try:
                    _, success, message = future.result()
                    if success:
                        success_count += 1
                        logging.info("✓ Processed %s", filepath)
                    else:
                        failure_count += 1
                        logging.error("✗ Failed %s: %s", filepath, message)
                except Exception as e:
                    failure_count += 1
                    logging.error("✗ Exception processing %s: %s", filepath, e)

    # Summary
    total = success_count + failure_count
    logging.info("\n" + "=" * 60)
    logging.info("Compliance processing complete")
    logging.info("Total files: %d", total)
    logging.info(
        "Success: %d (%.1f%%)",
        success_count,
        100 * success_count / total if total > 0 else 0,
    )
    logging.info(
        "Failed: %d (%.1f%%)",
        failure_count,
        100 * failure_count / total if total > 0 else 0,
    )
    logging.info("=" * 60)

    sys.exit(0 if failure_count == 0 else 1)


if __name__ == "__main__":
    main()
