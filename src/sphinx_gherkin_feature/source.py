"""Helpers for creating canonical Gherkin source text."""

from __future__ import annotations

from collections.abc import Sequence


def ensure_final_newline(source: str) -> str:
    """Return source text with exactly the existing content plus a final LF.

    Gherkin linters commonly expect feature files to end with a newline. This
    helper does not strip trailing whitespace or blank lines; it only appends a
    line-feed character when one is missing.
    """
    if source.endswith("\n"):
        return source
    return f"{source}\n"


def content_to_gherkin_source(content: Sequence[str]) -> str:
    """Convert directive content lines into canonical Gherkin source text."""
    return ensure_final_newline("\n".join(content))
