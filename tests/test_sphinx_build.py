from __future__ import annotations

from pathlib import Path

import pytest


def test_sphinx_build_writes_feature_file(tmp_path: Path) -> None:
    sphinx_application = pytest.importorskip("sphinx.application")
    Sphinx = sphinx_application.Sphinx

    srcdir = tmp_path / "src"
    outdir = tmp_path / "out"
    doctreedir = tmp_path / "doctrees"
    srcdir.mkdir()

    (srcdir / "conf.py").write_text(
        "extensions = ['sphinx_gherkin_feature']\n"
        "gherkin_feature_write_file = True\n"
        "gherkin_feature_output_dir = 'features'\n",
        encoding="utf-8",
    )
    (srcdir / "index.rst").write_text(
        "Example\n=======\n\n"
        ".. gherkin:feature::\n"
        "   :filename: login\n\n"
        "   Feature: Login\n\n"
        "     Scenario: Successful login\n"
        "       Given a user exists\n",
        encoding="utf-8",
    )

    app = Sphinx(
        srcdir=str(srcdir),
        confdir=str(srcdir),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername="html",
        warningiserror=True,
        freshenv=True,
    )
    app.build()

    generated = outdir / "features" / "login.feature"
    generated_text = generated.read_text(encoding="utf-8")
    assert generated_text.startswith("Feature: Login")
    assert generated_text.endswith("\n")


def test_sphinx_build_lints_feature_with_added_final_newline(tmp_path: Path) -> None:
    pytest.importorskip("gherkin_lint.gherkin_lint")
    sphinx_application = pytest.importorskip("sphinx.application")
    Sphinx = sphinx_application.Sphinx

    srcdir = tmp_path / "src"
    outdir = tmp_path / "out"
    doctreedir = tmp_path / "doctrees"
    srcdir.mkdir()

    (srcdir / "conf.py").write_text(
        "extensions = ['sphinx_gherkin_feature']\ngherkin_feature_lint = True\n",
        encoding="utf-8",
    )
    (srcdir / "index.rst").write_text(
        "Example\n=======\n\n"
        ".. gherkin:feature::\n"
        "   :filename: login\n\n"
        "   Feature: Login\n\n"
        "     Scenario: Successful login\n"
        "       Given a user exists",
        encoding="utf-8",
    )

    app = Sphinx(
        srcdir=str(srcdir),
        confdir=str(srcdir),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername="html",
        warningiserror=True,
        freshenv=True,
    )
    app.build()
