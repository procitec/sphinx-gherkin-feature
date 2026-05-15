# gherkin-lint string API patch

This directory contains the two relevant `gherkin-lint` files with a small API
extension for in-memory linting.

## New public API

```python
from gherkin_lint.gherkin_lint import GherkinLint

linter = GherkinLint(indent_size=4, logger=logger)
errors = linter.lint_text(
    "Feature: Login\n\n  Scenario: Successful login\n    Given a user exists\n",
    source_name="login.feature",
)
```

## Added methods

- `GherkinLint.lint_text(content: str, source_name: str = "<string>")`
- `GherkinLint.lint_string(content: str, source_name: str = "<string>")`
- `GherkinLint.lint_lines(lines: List[str], source_name: str = "<string>")`

`lint_file(path)` now delegates to `lint_text(...)`, so existing CLI and file-based
callers keep working.

The Sphinx extension in `src/sphinx_gherkin_feature/lint.py` prefers `lint_text`
and only falls back to the temporary-file bridge when an older `gherkin-lint`
version is installed.
