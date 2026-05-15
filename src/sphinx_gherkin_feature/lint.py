"""Integration with procitec/gherkin-lint."""

from __future__ import annotations

import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from sphinx.util import logging

from .source import ensure_final_newline

logger = logging.getLogger(__name__)


def _error_value(error: Any, name: str, default: str = "?") -> str:
    if isinstance(error, dict):
        return str(error.get(name, default))
    return str(getattr(error, name, default))


def _error_message(error: Any) -> str:
    if isinstance(error, dict):
        return str(error.get("message", error))
    return str(getattr(error, "message", error))


def _create_linter(indent_size: int) -> Any:
    """Create the real procitec/gherkin-lint linter instance."""
    from gherkin_lint.gherkin_lint import GherkinLint

    try:
        return GherkinLint(indent_size=indent_size, logger=logger)
    except TypeError:
        return GherkinLint(indent_size=indent_size)


def _call_lint_text(linter: Any, code: str, filename: str) -> list[Any]:
    try:
        return list(linter.lint_text(code, source_name=filename))
    except TypeError:
        return list(linter.lint_text(code, filename))


def _call_lint_string(linter: Any, code: str, filename: str) -> list[Any]:
    try:
        return list(linter.lint_string(code, source_name=filename))
    except TypeError:
        return list(linter.lint_string(code, filename))


def _call_lint_lines(linter: Any, lines: Sequence[str], filename: str) -> list[Any]:
    try:
        return list(linter.lint_lines(lines, source_name=filename))
    except TypeError:
        return list(linter.lint_lines(lines, filename))


def _call_lint_file(linter: Any, code: str, filename: str) -> list[Any]:
    """Run file-based gherkin-lint APIs against a temporary feature file.

    procitec/gherkin-lint v26.1.0 exposes a file-oriented API. The Sphinx
    directive still receives its content as an in-memory string, so this bridge
    keeps string-based use possible without vendoring or patching upstream code.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / filename
        path.write_text(ensure_final_newline(code), encoding="utf-8", newline="\n")
        return list(linter.lint_file(path))


def _split_lines_preserving_endings(code: str) -> list[str]:
    """Split code the same way the upstream file-based linter does."""
    lines: list[str] = []
    buf = ""
    for ch in code:
        buf += ch
        if ch in ("\n", "\r"):
            lines.append(buf)
            buf = ""
    if buf:
        lines.append(buf)
    return lines


def _run_linter(linter: Any, code: str, filename: str) -> list[Any]:
    """Run gherkin-lint for an in-memory feature script.

    The bridge uses the real installed ``gherkin_lint`` package. If a release
    exposes ``lint_file``, the bridge writes a temporary ``.feature`` file and
    calls that file-based API. In-memory APIs remain as fallbacks for other
    releases or test doubles that do not expose ``lint_file``.
    """
    if hasattr(linter, "lint_text"):
        return _call_lint_text(linter, code, filename)

    if hasattr(linter, "lint_string"):
        return _call_lint_string(linter, code, filename)

    if hasattr(linter, "lint_lines"):
        return _call_lint_lines(linter, _split_lines_preserving_endings(code), filename)

    if hasattr(linter, "lint_file"):
        return _call_lint_file(linter, code, filename)

    raise TypeError("gherkin-lint exposes no supported linting API")


def lint_gherkin(
    *,
    code: str,
    filename: str,
    indent_size: int,
    location: tuple[str, int | None],
) -> None:
    """Run gherkin-lint and report all findings as Sphinx warnings."""
    try:
        linter = _create_linter(indent_size)
    except Exception as exc:
        logger.warning(
            "gherkin_feature_lint is enabled, but gherkin-lint could not be imported: %s",
            exc,
            location=location,
        )
        return

    code = ensure_final_newline(code)

    try:
        errors = _run_linter(linter, code, filename)
    except Exception as exc:
        logger.warning(
            "gherkin-lint failed for %s: %s",
            filename,
            exc,
            location=location,
        )
        return

    for error in errors:
        logger.warning(
            "Gherkin lint: %s:%s: [%s] %s",
            filename,
            _error_value(error, "line"),
            _error_value(error, "type", "lint"),
            _error_message(error),
            location=location,
        )
