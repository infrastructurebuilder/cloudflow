"""The API documentation builds from the installed packages.

The Sphinx sources under docs/sphinx/source/ are copies; only conf.py is
patched, to find the modules in the installed cloudflow instead of through
paths into the old repository. Three pages document modules
that no longer exist. The build is held to exactly those three failures.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
from support import PROJECT

SOURCE = PROJECT / "docs" / "sphinx" / "source"
MISSING = {"nodeInfo", "nosofs_qops", "run_adnoc"}


@pytest.mark.slow
def test_the_documentation_builds_and_only_the_known_pages_fail(tmp_path: Path) -> None:
    warnings = tmp_path / "warnings.txt"
    out = tmp_path / "html"
    command = [str(Path(sys.executable).parent / "sphinx-build"), "-b", "html", "-q", "-w", str(warnings)]
    done = subprocess.run([*command, str(SOURCE), str(out)], capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stdout + done.stderr
    failed = set(re.findall(r"failed to import '(\w+)'", warnings.read_text()))
    assert failed == MISSING, (
        f"newly failing: {sorted(failed - MISSING)}; now importing: {sorted(MISSING - failed)}"
    )
    documented = {
        page.stem: page.read_text().count('class="sig')
        for page in out.glob("*/*.html")
        if page.stem not in MISSING and page.stem not in {"modules", "genindex", "search"}
    }
    assert documented, "no module pages were written"
    empty = sorted(name for name, signatures in documented.items() if signatures == 0)
    assert not empty, f"pages with nothing documented: {empty}"
