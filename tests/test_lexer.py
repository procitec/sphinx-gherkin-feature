from __future__ import annotations

from pygments import highlight
from pygments.formatters import HtmlFormatter

from sphinx_gherkin_feature.lexer import GherkinFeatureLexer


def test_gherkin_feature_lexer_smoke() -> None:
    code = (
        "Feature: Login\n\n"
        "  @smoke\n"
        "  Scenario: Successful login\n"
        "    Given a user exists\n"
        "    When the user logs in\n"
        "    Then the dashboard is shown\n"
    )

    html = highlight(code, GherkinFeatureLexer(), HtmlFormatter(nowrap=True))

    assert "Feature" in html
    assert "Scenario" in html
    assert "@smoke" in html
