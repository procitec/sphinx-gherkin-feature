"""Sphinx extension for rendering and optionally writing Gherkin feature files."""

from __future__ import annotations

from typing import Any

from sphinx.application import Sphinx

from .domain import GherkinDomain
from .lexer import GherkinFeatureLexer
from .writer import write_feature_files

__version__ = "0.1.3"


def register_lexer(app: Sphinx) -> None:
    """Register the bundled Pygments lexer with Sphinx when configured."""
    if not app.config.gherkin_feature_highlight:
        return
    if not app.config.gherkin_feature_register_lexer:
        return

    aliases = list(app.config.gherkin_feature_lexer_aliases or [])
    language = app.config.gherkin_feature_pygments_language
    if language and language not in aliases:
        aliases.insert(0, language)

    for alias in aliases:
        app.add_lexer(alias, GherkinFeatureLexer)


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up the Sphinx extension."""
    app.require_sphinx("7.2")

    app.add_config_value(
        "gherkin_feature_filename_regex",
        r"^[a-z0-9_]+$",
        "env",
        types=[str],
        description="Regex for validating :filename: in gherkin:feature directives.",
    )
    app.add_config_value(
        "gherkin_feature_write_file",
        False,
        "env",
        types=[bool],
        description="Write collected Gherkin feature files into the build output directory.",
    )
    app.add_config_value(
        "gherkin_feature_output_dir",
        "gherkin",
        "env",
        types=[str],
        description=(
            "Directory for generated .feature files. Relative paths are resolved under "
            "the Sphinx builder output directory; absolute paths are used as provided."
        ),
    )
    app.add_config_value(
        "gherkin_feature_lint",
        False,
        "env",
        types=[bool],
        description="Run procitec/gherkin-lint for every gherkin:feature directive.",
    )
    app.add_config_value(
        "gherkin_feature_lint_indent_size",
        4,
        "env",
        types=[int],
        description="Indentation size passed to gherkin-lint when linting is enabled.",
    )
    app.add_config_value(
        "gherkin_feature_highlight",
        True,
        "env",
        types=[bool],
        description="Enable syntax highlighting for generated literal blocks.",
    )
    app.add_config_value(
        "gherkin_feature_pygments_language",
        "gherkin-feature",
        "env",
        types=[str],
        description=(
            "Language alias written to the rendered literal block. Use this to bind the "
            "directive to a custom or built-in Pygments lexer."
        ),
    )
    app.add_config_value(
        "gherkin_feature_register_lexer",
        True,
        "env",
        types=[bool],
        description="Register the bundled Gherkin Pygments lexer under the configured aliases.",
    )
    app.add_config_value(
        "gherkin_feature_lexer_aliases",
        ["gherkin-feature"],
        "env",
        types=[list, tuple],
        description="Aliases under which the bundled Gherkin lexer is registered.",
    )

    app.add_domain(GherkinDomain)
    app.connect("builder-inited", register_lexer)
    app.connect("build-finished", write_feature_files)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
