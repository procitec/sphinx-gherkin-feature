from __future__ import annotations

from pathlib import Path

from sphinx_gherkin_feature.writer import resolve_feature_output_dir


def test_relative_output_dir_is_resolved_under_builder_outdir(tmp_path: Path) -> None:
    actual = resolve_feature_output_dir(tmp_path / "html", "features")
    assert actual == tmp_path / "html" / "features"


def test_absolute_output_dir_is_used_as_configured(tmp_path: Path) -> None:
    configured = tmp_path / "generated"
    assert resolve_feature_output_dir(tmp_path / "html", str(configured)) == configured
