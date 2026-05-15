from __future__ import annotations

from sphinx_gherkin_feature.source import content_to_gherkin_source, ensure_final_newline


def test_content_to_gherkin_source_adds_final_newline() -> None:
    source = content_to_gherkin_source(
        [
            "Feature: Login",
            "  Scenario: Successful login",
            "    Given a user exists",
        ]
    )

    assert source == ("Feature: Login\n  Scenario: Successful login\n    Given a user exists\n")


def test_content_to_gherkin_source_does_not_add_extra_newline() -> None:
    source = content_to_gherkin_source(["Feature: Login", ""])

    assert source == "Feature: Login\n"


def test_ensure_final_newline_preserves_trailing_blank_lines() -> None:
    source = ensure_final_newline("Feature: Login\n\n")

    assert source == "Feature: Login\n\n"
