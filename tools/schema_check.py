"""Say whether cloudflow can read a job or cluster description, by the schema it publishes (spec 005).

The rules, in one place: a description's JOBTYPE (or platform) must be one
cloudflow knows, with its MODEL, and every key the schema marks required for
it must be there. One exception, the template for a model cloudflow has no
class for yet: its MODEL is ``MODEL_CLASS``, its JOBTYPE ends in
``_EXPERIMENT``, and its other keys are what an existing experiment type
requires (answered 2026-11-23).

Cloud-Sandbox copies this file, byte for byte, into csis-sandbox-configs'
tests/, whose site descriptions are held to the same rules, and checks that
the copy has not drifted.
"""

from __future__ import annotations

from typing import Any

NEW_MODEL = "MODEL_CLASS"
NEW_MODEL_TEMPLATE = "new-model template"


def missing_keys(description: dict[str, Any], entry: dict[str, Any], common: dict[str, Any]) -> list[str]:
    """List the required keys a description lacks."""
    required = {**common["required"], **entry["required"]}
    return sorted(key for key in required if key not in description)


def check_new_model_template(description: dict[str, Any], jobs: dict[str, Any]) -> str:
    """Check the template for a new model: its keys must be what an existing experiment type requires."""
    if not str(description.get("JOBTYPE", "")).endswith("_EXPERIMENT"):
        return f"MODEL {NEW_MODEL} needs a JOBTYPE ending in _EXPERIMENT"
    keys = set(description) - {"MODEL", "JOBTYPE", "APP"}
    fits = [
        name
        for name, entry in jobs["jobtypes"].items()
        if name.endswith("_experiment") and set(entry["required"]) - {"MODEL", "JOBTYPE"} == keys
    ]
    return (
        NEW_MODEL_TEMPLATE
        if fits
        else f"a new-model template whose keys no experiment type requires: {sorted(keys)}"
    )


def check_job(description: dict[str, Any], jobs: dict[str, Any]) -> str:
    """Say whether cloudflow can read a job description; ``jobs`` is schema/jobs.json."""
    if description.get("MODEL") == NEW_MODEL:
        return check_new_model_template(description, jobs)
    jobtype = description.get("JOBTYPE")
    entry = jobs["jobtypes"].get(jobtype)
    if entry is None:
        return f"unknown JOBTYPE {jobtype!r}"
    if description.get("MODEL") != entry["MODEL"]:
        return f"JOBTYPE {jobtype} needs MODEL {entry['MODEL']}, not {description.get('MODEL')!r}"
    missing = missing_keys(description, entry, jobs["common"])
    return f"missing {', '.join(missing)}" if missing else "ok"


def check_cluster(description: dict[str, Any], clusters: dict[str, Any]) -> str:
    """Say whether cloudflow can read a cluster description; ``clusters`` is schema/clusters.json."""
    platform = description.get("platform")
    entry = clusters["platforms"].get(platform)
    if entry is None:
        return f"unknown platform {platform!r}"
    missing = missing_keys(description, entry, clusters["common"])
    return f"missing {', '.join(missing)}" if missing else "ok"
