#!/usr/bin/env python3

"""
Cucumber Feature File Linter

This script checks Cucumber/Gherkin feature files for various formatting rules
using modular check components.
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from .gherkin_checks import (
    IndentationCheck,
    AndKeywordCheck,
    StepSeparationCheck,
    FeatureKeywordCheck,
    TagIndentationCheck,
    BackgroundOccurrenceCheck,
    WhitespaceCheck,
    KeywordDescriptionCheck,
    StepBlockSeparationCheck,
    FreeDescriptionCheck,
    CommentSpacingCheck,
    StepKeywordRepetitionCheck,
    GivenEndingCheck,
    WhenThenSequenceCheck,
    ScenarioOutlineExamplesCheck,
    EmptyStepCheck,
)


class GherkinLint:
    """Encapsulates the linting logic for Gherkin feature files."""

    def __init__(self, indent_size: int, logger: logging.Logger):
        self.indent_size = indent_size
        self.logger = logger
        self.checks = []
        self._init_checks()

    def _init_checks(self):
        self.checks = []
        check_classes = [
            IndentationCheck,
            AndKeywordCheck,
            StepSeparationCheck,
            FeatureKeywordCheck,
            TagIndentationCheck,
            BackgroundOccurrenceCheck,
            WhitespaceCheck,
            KeywordDescriptionCheck,
            StepBlockSeparationCheck,
            FreeDescriptionCheck,
            CommentSpacingCheck,
            StepKeywordRepetitionCheck,
            GivenEndingCheck,
            WhenThenSequenceCheck,
            ScenarioOutlineExamplesCheck,
            EmptyStepCheck,
        ]
        for cls in check_classes:
            if cls.__name__ in ["IndentationCheck", "TagIndentationCheck", "FreeDescriptionCheck", "ScenarioOutlineExamplesCheck"]:
                instance = cls(indent_size=self.indent_size, logger=self.logger)
            else:
                instance = cls(logger=self.logger)
            self.checks.append(instance)

    @staticmethod
    def _split_feature_text(content: str) -> List[str]:
        """Split a feature string into physical lines while preserving line endings.

        Keeping line endings preserves the behaviour expected by existing checks.
        ``str.splitlines(keepends=True)`` also treats CRLF as one newline, which
        makes the string API safer for callers that pass Windows-style text.
        """
        return content.splitlines(keepends=True)

    def lint_lines(self, lines: List[str], source_name: str = "<string>") -> List[Dict]:
        """Lint already-split Gherkin lines.

        ``source_name`` is used only in diagnostics. It may be a filename, an
        in-memory document identifier, or the default ``"<string>"``.
        """
        self._init_checks()
        context = {"in_rule": False, "all_lines": lines}
        errors: List[Dict] = []

        for num, line in enumerate(lines, start=1):
            for check in self.checks:
                errors.extend(check.check(line, num, source_name, context))

        for check in self.checks:
            if hasattr(check, "check_end_of_file"):
                errors.extend(check.check_end_of_file(source_name))

        return errors

    def lint_text(self, content: str, source_name: str = "<string>") -> List[Dict]:
        """Lint Gherkin content provided as a string.

        This is the public string-based API for integrations such as Sphinx
        directives, editor plugins, tests, or web applications that already have
        the feature text in memory and should not need to write a temporary file.
        """
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        return self.lint_lines(self._split_feature_text(content), source_name)

    def lint_string(self, content: str, source_name: str = "<string>") -> List[Dict]:
        """Backward-compatible alias for callers that look for ``lint_string``."""
        return self.lint_text(content, source_name=source_name)

    def lint_file(self, path: Path) -> List[Dict]:
        content = path.read_text(encoding="utf-8")
        return self.lint_text(content, source_name=str(path))


class OutputManager:
    """Handles output to console and logfile with configurable verbosity."""

    def __init__(self, logfile: Optional[Path], verbosity: int):
        self.logfile = logfile
        self.logger = self._setup_logging(verbosity)

    def _setup_logging(self, verbosity: int) -> logging.Logger:
        logger = logging.getLogger("gherkin_linter")
        if verbosity >= 2:
            level = logging.DEBUG
        elif verbosity == 1:
            level = logging.INFO
        else:
            level = logging.WARNING
        logger.setLevel(level)
        logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(console_handler)

        if self.logfile:
            try:
                fh = logging.FileHandler(self.logfile, mode="w", encoding="utf-8")
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
                logger.addHandler(fh)
                logger.info(f"Logging output to file: {self.logfile}")
            except Exception as e:
                logger.error(f"Error creating log file {self.logfile}: {e}")
        return logger

    def print_results(self, source_name, errors: List[Dict]):
        if errors:
            # self.logger.warning(f"\nErrors in {source_name}:")
            for e in errors:
                self.logger.warning(f"{source_name}:{e['line']}: [{e['type']}] {e['message']}")
        else:
            self.logger.info(f"[OK] {source_name}: No linting errors found")

    def print_summary(self, total_errors: int, file_count: int):
        if total_errors > 0:
            self.logger.info(f"\nTotal: {total_errors} errors found in {file_count} file(s)")
        else:
            self.logger.info(f"\n[OK] All {file_count} files successfully linted, no errors found")


def main():
    parser = argparse.ArgumentParser(description="Gherkin Feature File Linter")
    parser.add_argument("files", nargs="+", type=Path, help="Paths to feature files")
    parser.add_argument("--indent-size", type=int, default=4, help="Indentation depth for Scenarios in Rules (default: 4)")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase output verbosity (use -vv for debug)")
    parser.add_argument("--logfile", type=Path, help="Path to log file for output")
    args = parser.parse_args()

    output_manager = OutputManager(logfile=args.logfile, verbosity=args.verbose)
    logger = output_manager.logger
    logger.info(f"Gherkin Feature File Linter started at {datetime.now():%Y-%m-%d %H:%M:%S}")
    logger.debug(f"Indentation depth: {args.indent_size}")
    logger.debug(f"Files to check: {len(args.files)}")

    linter = GherkinLint(indent_size=args.indent_size, logger=logger)
    total_errors = 0
    processed = 0

    for path in args.files:
        if not path.exists():
            logger.error(f"Error: File {path} does not exist")
            continue
        logger.debug(f"Linting file: {path}")
        errors = linter.lint_file(path)
        output_manager.print_results(path, errors)
        total_errors += len(errors)
        processed += 1

    output_manager.print_summary(total_errors, processed)
    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
