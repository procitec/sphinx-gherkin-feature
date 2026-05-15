"""Directive implementation for ``gherkin:feature``."""

from __future__ import annotations

import re
from typing import Any

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

from .lint import lint_gherkin

logger = logging.getLogger(__name__)


def validate_feature_filename(filename: str, pattern: str) -> None:
    """Validate a feature filename against the configured regex.

    The filename intentionally excludes the ``.feature`` suffix. The suffix is
    added when files are written. The default regex allows lowercase ASCII
    letters, digits and underscores only.
    """
    if not filename:
        raise ValueError("filename must not be empty")
    if not re.fullmatch(pattern, filename):
        raise ValueError(f"filename {filename!r} does not match {pattern!r}")


def store_feature(env: Any, docname: str, filename: str, code: str, line: int | None) -> None:
    """Store a feature script in the Sphinx domain data."""
    data = env.domaindata.setdefault("gherkin", {})
    features = data.setdefault("features", {})

    if filename in features:
        previous_docname = features[filename].get("docname")
        logger.warning(
            "Duplicate gherkin feature filename %r; replacing definition from %s",
            filename,
            previous_docname,
            location=(docname, line),
        )

    features[filename] = {
        "docname": docname,
        "code": code,
        "line": line,
    }


class FeatureDirective(SphinxDirective):
    """Render a Gherkin feature script and optionally collect it for writing."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False

    option_spec = {
        "filename": directives.unchanged_required,
    }

    def run(self) -> list[nodes.Node]:
        filename = self.options.get("filename")
        if filename is None:
            raise self.error("Missing required option :filename:")

        pattern = self.config.gherkin_feature_filename_regex
        try:
            validate_feature_filename(filename, pattern)
        except ValueError as exc:
            raise self.error(str(exc)) from exc

        code = "\n".join(self.content)
        if not code.strip():
            raise self.error("gherkin:feature requires a non-empty script body")

        source, line = self.get_source_info()
        location = (source or self.env.docname, line or self.lineno)

        if self.config.gherkin_feature_lint:
            lint_gherkin(
                code=code,
                filename=f"{filename}.feature",
                indent_size=self.config.gherkin_feature_lint_indent_size,
                location=location,
            )

        if self.config.gherkin_feature_write_file:
            store_feature(
                env=self.env,
                docname=self.env.docname,
                filename=filename,
                code=code,
                line=line,
            )

        literal = nodes.literal_block(code, code)
        literal["language"] = (
            self.config.gherkin_feature_pygments_language
            if self.config.gherkin_feature_highlight
            else "text"
        )
        literal["classes"].append("gherkin-feature")
        literal.source = source
        literal.line = line

        return [literal]
