"""Sphinx domain for Gherkin directives."""

from __future__ import annotations

from typing import Any

from sphinx.domains import Domain

from .directives import FeatureDirective


class GherkinDomain(Domain):
    """The ``gherkin`` domain."""

    name = "gherkin"
    label = "Gherkin"

    directives = {
        "feature": FeatureDirective,
    }
    roles: dict[str, Any] = {}
    initial_data: dict[str, Any] = {
        "features": {},
    }

    def clear_doc(self, docname: str) -> None:
        features = self.data.setdefault("features", {})
        for filename in list(features):
            if features[filename].get("docname") == docname:
                del features[filename]

    def merge_domaindata(self, docnames: list[str], otherdata: dict[str, Any]) -> None:
        features = self.data.setdefault("features", {})
        for filename, item in otherdata.get("features", {}).items():
            if item.get("docname") in docnames:
                features[filename] = item
