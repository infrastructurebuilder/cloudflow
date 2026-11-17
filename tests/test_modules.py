from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
from support import module_name, package_dir, python_files

# Modules that cannot be imported as they stand, and why. Each is a defect or a
# script in the copied code; the list shrinks as the originals are corrected.
NOT_IMPORTABLE = {
    "cloudflow.cluster.lambda_identify_zombies": "an AWS Lambda handler: it reads TABLE_NAME, "
    "AWS_REGION and ORG_MAX_MINUTES from the environment when it is loaded",
    "cloudflow.cluster.lambda_terminate_zombies": "an AWS Lambda handler: it reads TABLE_NAME, "
    "AWS_REGION and ORG_MAX_MINUTES from the environment when it is loaded",
    "cloudflow.plotting.hlfs": "an exported notebook: it runs main('hlfs.config') when it is loaded",
    "cloudflow.utils.testutils": "imports modelUtil as a top-level module, which resolves only "
    "when the working directory is utils/",
    "cloudflow.workflows.scripts.random_ofs": "a script: it reads /com/nos/current.fcst when it is loaded",
}

MODULES = [name for name in map(module_name, python_files()) if name]
IMPORTABLE = [name for name in MODULES if name not in NOT_IMPORTABLE]


def relative(path: Path) -> str:
    return str(path.relative_to(package_dir()))


@pytest.mark.parametrize("path", python_files(), ids=relative)
def test_file_compiles(path: Path) -> None:
    compile(path.read_text(), str(path), "exec")


def test_files_without_a_module_name_are_all_archived() -> None:
    unnamed = [path for path in python_files() if module_name(path) is None]
    assert unnamed, "the archived workflows have dots in their file names"
    assert all(relative(path).startswith("workflows/archived/") for path in unnamed)


@pytest.mark.parametrize("name", IMPORTABLE)
def test_module_imports(name: str) -> None:
    importlib.import_module(name)


def test_the_exceptions_name_real_modules() -> None:
    assert set(NOT_IMPORTABLE) <= set(MODULES)


@pytest.mark.parametrize("name", sorted(NOT_IMPORTABLE))
def test_a_listed_exception_still_fails(name: str, tmp_path: Path) -> None:
    lambda_settings = {"TABLE_NAME", "AWS_REGION", "ORG_MAX_MINUTES"}
    env = {key: value for key, value in os.environ.items() if key not in lambda_settings}
    done = subprocess.run(
        [sys.executable, "-c", f"import {name}"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode != 0, f"{name} imports now: remove it from NOT_IMPORTABLE"
