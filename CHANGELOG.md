# Changelog


## 0.1.2

- Switched development workflow to `uv`.
- Added `[dependency-groups]` for development and documentation dependencies.
- Added `.python-version` and a `Makefile` with uv-based commands.
- Updated README commands from `pip`/`python -m` workflows to `uv` workflows.
- Added a temporary `requests<2.34` constraint to keep Sphinx builder imports working in the tested dependency set.

## 0.1.1

- Added a proposed `gherkin-lint` string API patch with `lint_text`, `lint_string`, and `lint_lines`.
- Updated the Sphinx lint bridge to prefer `lint_text(...)` over temporary files.
- Added lint bridge tests for string API and file fallback behavior.

## 0.1.0

- Initial project skeleton.
- Added `gherkin:feature` directive.
- Added configurable filename validation.
- Added optional `.feature` file generation.
- Added configurable output directory for generated files.
- Added optional Gherkin lint bridge.
- Added bundled configurable Pygments lexer integration.
