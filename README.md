# sphinx-gherkin-feature

`sphinx-gherkin-feature` is a Sphinx extension for documenting complete Gherkin feature scripts and optionally writing those scripts as `.feature` files during the Sphinx build.

It provides the domain directive:

```rst
.. gherkin:feature::
   :filename: login

   Feature: Login

     Scenario: Successful login
       Given a user account exists
       When the user logs in
       Then the dashboard is shown
```

The directive body is rendered as a highlighted literal block. When file writing is enabled, the same body is also written as `login.feature`.

## Installation

This project is configured for [`uv`](https://docs.astral.sh/uv/).

For local development:

```bash
uv sync --group dev --group docs
```

The project pins `gherkin-lint` to the upstream GitHub release tag `v26.1.1` via `tool.uv.sources`:

```toml
[tool.uv.sources]
gherkin-lint = { git = "https://github.com/procitec/gherkin-lint.git", tag = "v26.1.1" }
```

For use in another uv-managed Sphinx project, add this package and the same source override for `gherkin-lint` in that project's `pyproject.toml`.

## Configuration

Add the extension to `conf.py`:

```python
extensions = ["sphinx_gherkin_feature"]
```

Available configuration values:

```python
# Validate :filename: values. The .feature suffix is not part of the option.
gherkin_feature_filename_regex = r"^[a-z0-9_]+$"

# Write feature files after successful builds.
gherkin_feature_write_file = False

# Where generated files are written.
# Relative paths are resolved below the Sphinx builder output directory.
# Absolute paths are used as configured.
gherkin_feature_output_dir = "gherkin"

# Lint integration with procitec/gherkin-lint v26.1.0.
gherkin_feature_lint = False
gherkin_feature_lint_indent_size = 4

# Optional Pygments highlighting integration.
gherkin_feature_highlight = True
gherkin_feature_pygments_language = "gherkin-feature"
gherkin_feature_register_lexer = True
gherkin_feature_lexer_aliases = ["gherkin-feature"]
```

## Writing feature files into a custom output directory

```python
extensions = ["sphinx_gherkin_feature"]

gherkin_feature_write_file = True
gherkin_feature_output_dir = "features"
```

With an HTML build, this writes files below:

```text
_build/html/features/
```

Absolute paths are also supported when the project explicitly wants generated files outside the builder output directory:

```python
gherkin_feature_output_dir = "/tmp/generated-features"
```

## Syntax highlighting

By default, the extension registers a bundled Pygments lexer under `gherkin-feature` and renders directive bodies with that language alias.

To use a different alias:

```python
gherkin_feature_pygments_language = "gherkin"
gherkin_feature_lexer_aliases = ["gherkin"]
```

To use a lexer supplied by another package, disable bundled registration and point the rendered literal block to that alias:

```python
gherkin_feature_register_lexer = False
gherkin_feature_pygments_language = "gherkin"
```

To disable highlighting entirely:

```python
gherkin_feature_highlight = False
```

## Linting

When `gherkin_feature_lint = True`, the extension imports the real upstream package:

```python
from gherkin_lint.gherkin_lint import GherkinLint
```

The Sphinx directive receives feature scripts as strings. The bridge therefore accepts strings and maps them to whatever API the installed upstream release exposes:

1. `lint_text(code, source_name=...)`, if present
2. `lint_string(code, source_name=...)`, if present
3. `lint_lines(lines, source_name=...)`, if present
4. `lint_file(path)` via a temporary `.feature` file

For `procitec/gherkin-lint` release `v26.1.1`, the file-based path is expected. No patched or vendored copy of `gherkin-lint` is used by this package.

## Development with uv

Create or update the local environment:

```bash
uv sync --group dev --group docs
```

Run tests:

```bash
uv run pytest
```

Run lint checks:

```bash
uv run ruff check src tests
```

Build the example documentation:

```bash
uv run sphinx-build -b html docs docs/_build/html
```

Build source distribution and wheel:

```bash
uv build
```

Create or refresh the lockfile when you want to commit a local dependency snapshot:

```bash
uv lock
```

Publish, after configuring credentials:

```bash
uv publish
```

## Project layout

```text
src/sphinx_gherkin_feature/
  __init__.py      Sphinx setup and config registration
  directives.py    gherkin:feature directive
  domain.py        gherkin domain
  lexer.py         bundled Pygments lexer
  lint.py          optional gherkin-lint bridge
  writer.py        build-finished file writer
```

## Optional gherkin-lint string API

`gherkin_feature_lint = True` integrates with `procitec/gherkin-lint`.

The preferred interface is now an in-memory API on `gherkin-lint`:

```python
errors = linter.lint_text(code, source_name="login.feature")
```

The Sphinx bridge calls `lint_text(...)` when available, then falls back to
`lint_string(...)`, and finally to the older `lint_file(...)` API via a temporary
`.feature` file. A proposed upstream patch for `gherkin-lint` is included in
`external/gherkin-lint-string-api/`.
