"""Every template and example description cloudflow carries is one its code reads (spec 005).

The 51 came from csis-sandbox-configs, repaired first where they could not be
read. Each is checked against cloudflow's own schema, written from its code
(``tools/configs_schema.py``), by the rules in ``tools/schema_check.py``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from schema_check import NEW_MODEL_TEMPLATE, check_cluster, check_job

UNIT = Path(__file__).resolve().parents[1]
EXAMPLES = UNIT / "examples" / "configs"
CATALOGUE = EXAMPLES / "catalogue.json"
SCHEMA = UNIT / "schema"


def files() -> list[str]:
    return sorted(
        path.relative_to(EXAMPLES).as_posix()
        for path in EXAMPLES.rglob("*")
        if path.is_file() and path != CATALOGUE
    )


def recorded() -> dict[str, dict[str, str]]:
    return json.loads(CATALOGUE.read_text())


def status_of(description: dict[str, Any]) -> str:
    if "platform" in description:
        return check_cluster(description, json.loads((SCHEMA / "clusters.json").read_text()))
    return check_job(description, json.loads((SCHEMA / "jobs.json").read_text()))


def test_the_catalogue_lists_every_file() -> None:
    assert set(files()) == set(recorded())


def test_cloudflow_carries_the_templates_and_examples() -> None:
    roles = [entry["role"] for entry in recorded().values()]
    assert roles.count("template") == 3
    assert roles.count("example") == 48


@pytest.mark.parametrize("path", files())
def test_a_description_is_one_cloudflow_reads(path: str) -> None:
    status = status_of(json.loads((EXAMPLES / path).read_text()))
    entry = recorded()[path]
    assert status == entry["status"]
    assert status == "ok" or (status == NEW_MODEL_TEMPLATE and entry["role"] == "template"), status


def test_the_cluster_template_a_new_site_copies_has_a_table_name() -> None:
    template = json.loads((EXAMPLES / "cluster.configs" / "template.ioos").read_text())
    assert template["table_name"]
