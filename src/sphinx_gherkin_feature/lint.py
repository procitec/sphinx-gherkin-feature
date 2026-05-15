"""Optional integration with procitec/gherkin-lint."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from sphinx.util import logging

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


def _call_lint_file(linter: Any, code: str, filename: str) -> list[Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / filename
        path.write_text(code, encoding="utf-8")
        return list(linter.lint_file(path))


def _run_linter(linter: Any, code: str, filename: str) -> list[Any]:
    """Run gherkin-lint, preferring the in-memory string interface.

    The preferred upstream API is ``GherkinLint.lint_text(content,
    source_name=...)``. ``lint_string`` and ``lint_file`` remain compatibility
    fallbacks so the Sphinx extension still works with older gherkin-lint
    versions.
    """
    if hasattr(linter, "lint_text"):
        return _call_lint_text(linter, code, filename)

    if hasattr(linter, "lint_string"):
        return _call_lint_string(linter, code, filename)

    if hasattr(linter, "lint_file"):
        return _call_lint_file(linter, code, filename)

    raise TypeError("gherkin-lint exposes neither lint_text, lint_string nor lint_file")


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
