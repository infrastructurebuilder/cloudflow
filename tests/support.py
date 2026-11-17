"""What the tests share: where the package is, and how it is scanned.

Run as a script, this prints the outward references found in the package, in
the form of ``tests/outward_references.json``::

    uv run python tests/support.py > tests/outward_references.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import cloudflow

PROJECT = Path(__file__).resolve().parents[1]

# Ways in which the code reaches outside its own package. Each is something a
# real relocation has to remove or turn into configuration.
OUTWARD = {
    "sibling configuration by relative path": re.compile(r"\.\./(?:job|cluster)\.configs"),
    "the monorepo by name": re.compile(r"Cloud-Sandbox"),
    "a home directory": re.compile(r"/home/[A-Za-z0-9_-]+"),
    "sys.path changed at import": re.compile(r"sys\.path\.(?:append|insert)"),
}


def package_dir() -> Path:
    """Find the cloudflow package's directory: the one that holds the workflows."""
    for entry in cloudflow.__path__:
        if (Path(entry) / "workflows").is_dir():
            return Path(entry)
    raise AssertionError(f"no workflows directory in {list(cloudflow.__path__)}")


def python_files() -> list[Path]:
    """List every Python file in the package."""
    return sorted(package_dir().rglob("*.py"))


def module_name(path: Path) -> str | None:
    """Give the dotted name a file is imported by, or None if it has none."""
    parts = path.relative_to(package_dir()).with_suffix("").parts
    if all(part.isidentifier() for part in parts):
        return ".".join(("cloudflow", *parts))
    return None


def outward_references() -> dict[str, dict[str, int]]:
    """Count, per file, the references that leave the package."""
    found: dict[str, dict[str, int]] = {}
    root = package_dir()
    for path in sorted([*root.rglob("*.py"), *root.rglob("*.sh")]):
        text = path.read_text(errors="replace")
        counts = {label: len(pattern.findall(text)) for label, pattern in OUTWARD.items()}
        counts = {label: count for label, count in counts.items() if count}
        if counts:
            found[str(path.relative_to(root))] = counts
    return found


if __name__ == "__main__":
    json.dump(outward_references(), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
