"""Derive, from cloudflow's code, the keys it reads from job and cluster descriptions.

A job description is the JSON file that ``JobFactory.job()`` reads; its
``MODEL`` and ``JOBTYPE`` pick a class, and that class's ``parseConfig()``
reads the rest. A cluster description is read by ``ClusterFactory.cluster()``;
its ``platform`` picks ``AWSCluster`` or ``LocalCluster``.

Each key is recorded with the line that reads it, as ``path:line``, the path
being the package's own (``cloudflow/job/...``), read from this repository's
``src/``. A key is *required* when it is read as ``cfDict['KEY']`` with
nothing around it that would survive its absence. It is *optional* when it
is read with ``cfDict.get()``, inside a ``try`` that catches ``KeyError``, or
under ``if 'KEY' in cfDict`` (unless that ``if`` raises when the key is
missing, which makes it required again). It is *conditional* when the read sits
under some other ``if``: then whether it is needed depends on other values,
and the check treats it as optional.

The result is published in ``schema/``, checked against the code by
``tests/test_configs_schema.py``; ``tests/test_examples.py`` holds the
descriptions in ``examples/configs/`` to it. ``just schema`` writes it again.
Written in Cloud-Sandbox's exportit/tools/ until spec 005 (2026-11-23) moved
it here, beside the code it reads; Cloud-Sandbox copies the schema, and
``schema_check.py``, into csis-sandbox-configs and checks the copies.

Usage::

    configs_schema.py            print both schemas
    configs_schema.py --write    write them into schema/
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "src"
"""Where cloudflow's code is read from: this repository, whose ``src/cloudflow/`` is the package."""
JOB_DIR = Path("cloudflow/job")
CLUSTER_DIR = Path("cloudflow/cluster")
SCHEMA_DIR = ROOT / "schema"
DICT_NAMES = {"cfDict", "cfdict"}
CATCHES_KEYERROR = {"KeyError", "LookupError", "Exception", "BaseException"}

Reads = dict[str, dict[str, str]]
"""kind ('required', 'optional', 'conditional') -> key -> 'path:line'"""


def where(path: Path, node: ast.AST) -> str:
    """Give ``path:line`` for a node."""
    return f"{path.as_posix()}:{getattr(node, 'lineno', 0)}"


def parents_of(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    """Map every node to the node that contains it."""
    found: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            found[child] = node
    return found


def handler_catches_keyerror(handler: ast.ExceptHandler) -> bool:
    """Say whether an ``except`` clause would catch a missing key."""
    if handler.type is None:
        return True
    types = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
    return any(isinstance(item, ast.Name) and item.id in CATCHES_KEYERROR for item in types)


def tests_presence(test: ast.expr, key: str) -> bool:
    """Say whether an ``if`` test checks ``'key' in <dict>``."""
    for node in ast.walk(test):
        if (
            isinstance(node, ast.Compare)
            and isinstance(node.left, ast.Constant)
            and node.left.value == key
            and any(isinstance(op, ast.In) for op in node.ops)
        ):
            return True
    return False


def classify(node: ast.AST, key: str, parents: dict[ast.AST, ast.AST]) -> str:
    """Say whether a ``cfDict['key']`` read is required, optional or conditional."""
    kind = "required"
    child = node
    while child in parents:
        parent = parents[child]
        if (
            isinstance(parent, ast.Try)
            and child in parent.body
            and any(handler_catches_keyerror(handler) for handler in parent.handlers)
        ):
            return "optional"
        if isinstance(parent, ast.If) and child is not parent.test:
            if tests_presence(parent.test, key):
                # `if 'KEY' in cfDict: ... else: raise` does not make the key
                # optional; an `if` further out may still make it conditional.
                if not any(isinstance(item, ast.Raise) for item in parent.orelse):
                    return "optional"
            else:
                kind = "conditional"
        if isinstance(parent, ast.FunctionDef | ast.AsyncFunctionDef):
            break
        child = parent
    return kind


def dict_reads(path: Path) -> Reads:
    """List the keys a file reads from a description, by kind."""
    tree = ast.parse((CODE / path).read_text())
    parents = parents_of(tree)
    reads: Reads = {"required": {}, "optional": {}, "conditional": {}}

    def note(kind: str, key: str, node: ast.AST) -> None:
        # The first read of a key decides; a weaker later read does not.
        for seen in reads.values():
            if key in seen:
                return
        reads[kind][key] = where(path, node)

    for node in sorted(ast.walk(tree), key=lambda item: getattr(item, "lineno", 0)):
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.ctx, ast.Load)
            and isinstance(node.value, ast.Name)
            and node.value.id in DICT_NAMES
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            note(classify(node, node.slice.value, parents), node.slice.value, node)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in DICT_NAMES
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            note("optional", node.args[0].value, node)
    return reads


def compared_constants(test: ast.expr, name: str) -> list[str]:
    """Give the strings that ``name`` is compared with (``==``) in an ``if`` test."""
    found: list[str] = []
    for node in ast.walk(test):
        if (
            isinstance(node, ast.Compare)
            and isinstance(node.left, ast.Name)
            and node.left.id == name
            and len(node.ops) == 1
            and isinstance(node.ops[0], ast.Eq)
            and isinstance(node.comparators[0], ast.Constant)
            and isinstance(node.comparators[0].value, str)
        ):
            found.append(node.comparators[0].value)
    return found


def created_class(body: list[ast.stmt], variable: str) -> ast.Call | None:
    """Find ``<variable> = SomeClass(...)`` among statements, or nested in them (a ``try``)."""
    for statement in (node for item in body for node in ast.walk(item)):
        if (
            isinstance(statement, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == variable for target in statement.targets)
            and isinstance(statement.value, ast.Call)
            and isinstance(statement.value.func, ast.Name)
        ):
            return statement.value
    return None


def if_chain(statement: ast.If) -> list[ast.If]:
    """Flatten ``if ... elif ... elif`` into its branches."""
    chain = [statement]
    while len(chain[-1].orelse) == 1 and isinstance(chain[-1].orelse[0], ast.If):
        chain.append(chain[-1].orelse[0])
    return chain


def factory_choices(
    path: Path, selector: str, inner: str | None, variable: str
) -> list[tuple[str, str, str]]:
    """Read a factory's dispatch: (selector value, inner value, class name).

    ``JobFactory`` chooses on ``model``, then on ``jobtype``;
    ``ClusterFactory`` on ``provider`` alone (inner is None, given as '').
    """
    tree = ast.parse((CODE / path).read_text())
    choices: list[tuple[str, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If) or not compared_constants(node.test, selector):
            continue
        if node in {
            branch for top in ast.walk(tree) if isinstance(top, ast.If) for branch in if_chain(top)[1:]
        }:
            continue
        for outer in if_chain(node):
            for value in compared_constants(outer.test, selector):
                if inner is None:
                    call = created_class(outer.body, variable)
                    if call is not None and isinstance(call.func, ast.Name):
                        choices.append((value, "", call.func.id))
                    continue
                for statement in outer.body:
                    if not isinstance(statement, ast.If):
                        continue
                    for branch in if_chain(statement):
                        call = created_class(branch.body, variable)
                        if call is None or not isinstance(call.func, ast.Name):
                            continue
                        choices.extend(
                            (value, kind, call.func.id) for kind in compared_constants(branch.test, inner)
                        )
    return choices


def job_schema() -> dict[str, object]:
    """Give the schema of job descriptions."""
    factory = JOB_DIR / "JobFactory.py"
    common = dict_reads(factory)
    jobtypes: dict[str, object] = {}
    for model, jobtype, cls in sorted(factory_choices(factory, "model", "jobtype", "newjob")):
        path = JOB_DIR / f"{cls}.py"
        reads = dict_reads(path)
        jobtypes[jobtype] = {"MODEL": model, "class": cls, "file": path.as_posix(), **reads}
    return {
        "about": "Keys cloudflow reads from a job description. Written by exportit/tools/configs_schema.py.",
        "read_by": factory.as_posix(),
        "common": common,
        "jobtypes": jobtypes,
    }


def cluster_schema() -> dict[str, object]:
    """Give the schema of cluster descriptions."""
    factory = CLUSTER_DIR / "ClusterFactory.py"
    platforms: dict[str, object] = {}
    for platform, _, cls in sorted(factory_choices(factory, "provider", None, "newcluster")):
        path = CLUSTER_DIR / f"{cls}.py"
        platforms[platform] = {"class": cls, "file": path.as_posix(), **dict_reads(path)}
    return {
        "about": "Keys cloudflow reads from a cluster description. Written by exportit/tools/configs_schema.py.",  # noqa: E501
        "read_by": factory.as_posix(),
        "common": dict_reads(factory),
        "platforms": platforms,
    }


def schemas() -> dict[str, str]:
    """Give each schema file's name and its text."""
    return {
        "jobs.json": json.dumps(job_schema(), indent=2) + "\n",
        "clusters.json": json.dumps(cluster_schema(), indent=2) + "\n",
    }


def main(argv: list[str]) -> int:
    """Print the schemas, or write them with --write."""
    if argv not in ([], ["--write"]):
        print(__doc__, file=sys.stderr)
        return 2
    for name, text in schemas().items():
        if argv:
            target = SCHEMA_DIR / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
            print(f"wrote {target.relative_to(ROOT)}")
        else:
            print(f"== {name}\n{text}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
