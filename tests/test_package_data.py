from __future__ import annotations

import os
import re
from importlib.metadata import entry_points
from pathlib import Path

import pytest
from support import package_dir, python_files

# The code finds launchers, helper scripts and templates beside itself, through
# a module-level `curdir`. This is every such reference that is not commented out.
BESIDE_ITSELF = re.compile(r"^[^#\n]*\{curdir\}/([A-Za-z0-9_./-]+)", re.MULTILINE)

# References that do not resolve inside the package, and why.
NOT_IN_THE_PACKAGE = {
    "workflows/../dist/": "push_pyEnv uploads any source distribution it finds in a dist/ "
    "directory beside the package; none is shipped",
}


def references() -> list[tuple[str, Path]]:
    found: set[tuple[str, Path]] = set()
    root = package_dir()
    for path in python_files():
        if "archived" in path.parts:
            continue
        for match in BESIDE_ITSELF.finditer(path.read_text()):
            label = f"{path.parent.relative_to(root)}/{match.group(1)}"
            found.add((label, path.parent / match.group(1)))
    return sorted(found)


REFERENCES = references()


def test_the_scan_finds_the_launchers() -> None:
    labels = {label for label, _ in REFERENCES}
    assert "workflows/fcst_launcher.sh" in labels
    assert "job/templates" in labels


@pytest.mark.parametrize(("label", "target"), REFERENCES, ids=[label for label, _ in REFERENCES])
def test_a_file_looked_up_beside_the_code_is_there(label: str, target: Path) -> None:
    if label in NOT_IN_THE_PACKAGE:
        assert not target.exists(), f"{label} exists now: remove it from NOT_IN_THE_PACKAGE"
        return
    assert target.exists()
    if target.suffix == ".sh":
        assert os.access(target, os.X_OK), f"{label} is run directly and must be executable"


def test_the_exceptions_are_real_references() -> None:
    assert set(NOT_IN_THE_PACKAGE) <= {label for label, _ in REFERENCES}


def test_the_input_templates_are_present() -> None:
    templates = [path for path in (package_dir() / "job" / "templates").iterdir() if path.is_file()]
    assert len(templates) == 44


def test_the_command_is_registered() -> None:
    (command,) = entry_points(group="console_scripts", name="cloudflow")
    assert command.value == "cloudflow.workflows.workflow_main:main"
    assert callable(command.load())
