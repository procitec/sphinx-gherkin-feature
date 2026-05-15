from __future__ import annotations

from sphinx_gherkin_feature.lint import _run_linter


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


def test_run_linter_prefers_lint_text() -> None:
    linter = TextOnlyLinter()

    errors = _run_linter(linter, "Feature: Login\n", "login.feature")

    assert errors == [{"line": 1, "type": "demo", "message": "from text"}]
    assert linter.called_with == ("Feature: Login\n", "login.feature")


def test_run_linter_keeps_lint_file_fallback() -> None:
    linter = FileFallbackLinter()

    errors = _run_linter(linter, "Feature: Login\n", "login.feature")

    assert errors == [{"line": 1, "type": "demo", "message": "login.feature"}]
    assert linter.path_text == "Feature: Login\n"
