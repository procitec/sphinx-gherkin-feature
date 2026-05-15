.PHONY: sync test lint docs build clean

sync:
	uv sync --group dev --group docs

test:
	uv run pytest

lint:
	uv run ruff check src tests

docs:
	uv run sphinx-build -b html docs docs/_build/html

build:
	uv build

clean:
	rm -rf .pytest_cache .ruff_cache build dist docs/_build *.egg-info src/*.egg-info
