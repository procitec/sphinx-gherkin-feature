"""Write collected Gherkin feature scripts to disk."""

from __future__ import annotations

from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util import logging

from .source import ensure_final_newline

logger = logging.getLogger(__name__)


def resolve_feature_output_dir(outdir: str | Path, configured_output_dir: str) -> Path:
    """Resolve the configured feature output directory.

    Relative paths are resolved below the Sphinx builder output directory.
    Absolute paths are respected because this is an explicit project
    configuration choice.
    """
    configured = Path(configured_output_dir).expanduser()
    if configured.is_absolute():
        return configured
    return Path(outdir) / configured


def write_feature_files(app: Sphinx, exception: Exception | None) -> None:
    """Write collected feature files after a successful build."""
    if exception is not None:
        return
    if not app.config.gherkin_feature_write_file:
        return

    features = app.env.domaindata.get("gherkin", {}).get("features", {})
    if not features:
        return

    target_dir = resolve_feature_output_dir(
        app.outdir,
        app.config.gherkin_feature_output_dir,
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    for filename, item in sorted(features.items()):
        target = target_dir / f"{filename}.feature"
        target.write_text(ensure_final_newline(item["code"]), encoding="utf-8", newline="\n")
        logger.info("wrote Gherkin feature file %s", target)
