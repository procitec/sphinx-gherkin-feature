from __future__ import annotations

import pytest

from sphinx_gherkin_feature.directives import validate_feature_filename


@pytest.mark.parametrize("filename", ["login", "checkout_1", "a0_b1"])
def test_validate_feature_filename_accepts_default_allowed_names(filename: str) -> None:
    validate_feature_filename(filename, r"^[a-z0-9_]+$")


@pytest.mark.parametrize("filename", ["Login", "login-feature", "login.feature", "../login", ""])
def test_validate_feature_filename_rejects_default_disallowed_names(filename: str) -> None:
    with pytest.raises(ValueError):
        validate_feature_filename(filename, r"^[a-z0-9_]+$")
