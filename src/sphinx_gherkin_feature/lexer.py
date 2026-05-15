"""Bundled Pygments lexer for Gherkin feature files."""

from __future__ import annotations

import re

from pygments.lexer import RegexLexer, bygroups
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text

KEYWORD_RE = (
    r"^(\s*)((?:Feature|Background|Rule|Example|Scenario|"
    r"Scenario Outline|Scenario Template|Examples):)(.*)$"
)


class GherkinFeatureLexer(RegexLexer):
    """A compact lexer for common Gherkin feature syntax."""

    name = "Gherkin Feature"
    aliases = ["gherkin-feature"]
    filenames = ["*.feature"]
    flags = re.MULTILINE

    tokens = {
        "root": [
            (r"^\s*#.*$", Comment.Single),
            (r"(@[A-Za-z0-9_:\-.]+)", Name.Decorator),
            (
                KEYWORD_RE,
                bygroups(Text, Keyword.Namespace, Text),
            ),
            (
                r"^(\s*)((?:Given|When|Then|And|But)\b|\*)(.*)$",
                bygroups(Text, Keyword, Text),
            ),
            (r"(<[^>\n]+>)", Name.Variable),
            (r"(\|)", Punctuation),
            (r"\b\d+(?:\.\d+)?\b", Number),
            (r'"[^"\n]*"', String.Double),
            (r"'[^'\n]*'", String.Single),
            (r"[:=]", Operator),
            (r"\s+", Text),
            (r".", Text),
        ]
    }
