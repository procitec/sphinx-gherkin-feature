from __future__ import annotations

import importlib

import pytest

from sphinx_gherkin_feature.lint import _create_linter, _run_linter


class TextOnlyLinter:
    def __init__(self) -> None:
        self.called_with: tuple[str, str] | None = None

    def lint_text(self, content: str, source_name: str = "<string>"):
        self.called_with = (content, source_name)
        return [{"line": 1, "type": "demo", "message": "from text"}]


class FileFallbackLinter:
    def __init__(self) -> None:
        self.path_text: str | None = None

    def lint_file(self, path):
        self.path_text = path.read_text(encoding="utf-8")
        return [{"line": 1, "type": "demo", "message": str(path.name)}]


class FileAndTextLinter(FileFallbackLinter):
    def __init__(self) -> None:
        super().__init__()
        self.text_called = False

    def lint_text(self, content: str, source_name: str = "<string>"):
        self.text_called = True
        return [{"line": 1, "type": "demo", "message": "from text"}]

#
# def test_run_linter_uses_lint_file_when_available() -> None:
#     linter = FileAndTextLinter()
#
#     errors = _run_linter(linter, "Feature: Login\n", "login.feature")
#
#     assert errors == [{"line": 1, "type": "demo", "message": "login.feature"}]
#     assert linter.path_text == "Feature: Login\n"
#     assert not linter.text_called


def test_run_linter_keeps_text_fallback_for_text_only_linters() -> None:
    linter = TextOnlyLinter()

    errors = _run_linter(linter, "Feature: Login\n", "login.feature")

    assert errors == [{"line": 1, "type": "demo", "message": "from text"}]
    assert linter.called_with == ("Feature: Login\n", "login.feature")


def test_run_linter_file_api_gets_final_newline() -> None:
    linter = FileFallbackLinter()

    errors = _run_linter(linter, "Feature: Login", "login.feature")

    assert errors == [{"line": 1, "type": "demo", "message": "login.feature"}]
    assert linter.path_text == "Feature: Login\n"


def test_real_gherkin_lint_release_reports_invalid_feature_text() -> None:
    pytest.importorskip("gherkin_lint.gherkin_lint")

    module = importlib.import_module("gherkin_lint.gherkin_lint")
    assert hasattr(module, "GherkinLint")

    linter = _create_linter(indent_size=4)
    errors = _run_linter(
        linter,
        "Scenario: Missing feature keyword\nGiven\n",
        "invalid.feature",
    )

    assert errors
    assert all(hasattr(error, "get") or hasattr(error, "message") for error in errors)
