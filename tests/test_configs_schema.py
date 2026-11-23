"""The schema cloudflow publishes, in schema/, is what its code reads, line for line (spec 005)."""

from __future__ import annotations

import json
from pathlib import Path

import configs_schema
import pytest

KINDS = ("required", "optional", "conditional")


def references(name: str) -> list[tuple[str, str]]:
    """Give (key, 'path:line') for every key of a written schema file."""
    found = json.loads((configs_schema.SCHEMA_DIR / name).read_text())
    entries = [found["common"], *(found.get("jobtypes") or found["platforms"]).values()]
    return [(key, ref) for entry in entries for kind in KINDS for key, ref in entry[kind].items()]


@pytest.mark.parametrize("name", ["jobs.json", "clusters.json"])
def test_the_written_schema_is_what_the_code_reads(name: str) -> None:
    written = (configs_schema.SCHEMA_DIR / name).read_text()
    assert written == configs_schema.schemas()[name], "run `just schema` and review the difference"


@pytest.mark.parametrize("name", ["jobs.json", "clusters.json"])
def test_every_line_named_reads_its_key(name: str) -> None:
    wrong: list[str] = []
    for key, ref in references(name):
        path, line = ref.rsplit(":", 1)
        text = Path(configs_schema.CODE / path).read_text().splitlines()[int(line) - 1]
        if f"'{key}'" not in text and f'"{key}"' not in text:
            wrong.append(f"{ref} does not read {key}: {text.strip()}")
    assert not wrong, wrong


def test_every_jobtype_of_the_factory_is_in_the_schema() -> None:
    jobs = configs_schema.job_schema()["jobtypes"]
    assert isinstance(jobs, dict)
    assert len(jobs) == 17  # pyright: ignore[reportUnknownArgumentType]
    assert {"romsforecast", "fvcomhindcast", "plotting", "ufs_regressiontest"} <= set(jobs)  # pyright: ignore[reportUnknownArgumentType]


def test_both_platforms_are_in_the_schema() -> None:
    platforms = configs_schema.cluster_schema()["platforms"]
    assert isinstance(platforms, dict)
    assert set(platforms) == {"AWS", "Local"}  # pyright: ignore[reportUnknownArgumentType]


def test_a_read_guarded_by_a_raise_stays_required() -> None:
    clusters = json.loads(configs_schema.schemas()["clusters.json"])
    assert "table_name" in clusters["platforms"]["AWS"]["required"]
    jobs = json.loads(configs_schema.schemas()["jobs.json"])
    # Required only for LiveOcean: the guard sits inside `if self.APP == "liveocean"`.
    assert "EXPNAME" in jobs["jobtypes"]["romshindcast"]["conditional"]
