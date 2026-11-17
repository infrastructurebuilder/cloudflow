from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from support import PROJECT, outward_references

BASELINE = PROJECT / "tests" / "outward_references.json"


def test_the_code_reaches_outside_only_where_it_is_known_to() -> None:
    """Hold the places where the package depends on its old surroundings.

    The baseline is the list of what a real relocation has to change. A new
    entry means a new dependency on the monorepo; a missing one means a
    dependency was removed and the baseline should be regenerated (see
    tests/support.py).
    """
    assert outward_references() == json.loads(BASELINE.read_text())


def test_the_command_explains_itself_when_given_nothing(tmp_path: Path) -> None:
    command = Path(sys.executable).parent / "cloudflow"
    done = subprocess.run([str(command)], cwd=tmp_path, capture_output=True, text=True, check=False)
    assert done.returncode == 1
    assert "cluster_config job_config" in done.stdout
