# cloudflow

A workflow system for running ocean and coastal models on cloud
compute. A workflow is a [Prefect](https://www.prefect.io/) flow that
starts a cluster of EC2 nodes, runs a model on it through a launcher
script and `mpirun`, optionally plots the output, and terminates the
nodes.

```sh
cloudflow <cluster description> <job description>
```

Both arguments are JSON files. The cluster description says which
nodes to start and where; the job description says which model to run
and with what. The kind of job (`JOBTYPE`) selects the flow.

## This is a copy

This directory is a copy made inside the Cloud-Sandbox repository, to
show cloudflow as a project that stands on its own. The files under
`src/`, `docs/`, `notebooks/`, `notes/`, `examples/`, `requirements/`,
`legacy/` and `legacy-tests/` come from the repository's `cloudflow/`
directory and a few root files. They are byte-identical to their
originals, except for seven files with small corrections that are kept
as patches. [../MAP.md](../MAP.md) lists every file, every correction,
what would still have to change, and how this project would be moved
to a repository of its own.

Do not edit the copied files here. Change the original and run
`just export cloudflow` at the repository root, or add a patch under
`../cloudflow.patches/`.

## Layout

| Path | What |
| --- | --- |
| `src/cloudflow/cluster/` | Starting and stopping compute nodes (`AWSCluster`, `LocalCluster`). The two Lambda functions that find and stop nodes left running are `csis-sandbox-terraform`'s since spec 003 (its `reaper/`) |
| `src/cloudflow/job/` | One class per kind of model run, and `templates/`, the model input files they fill in |
| `src/cloudflow/services/` | Storage: S3 and scratch disks |
| `src/cloudflow/utils/` | Shared helpers |
| `src/cloudflow/workflows/` | The flows and tasks, the `cloudflow` command (`workflow_main.py`), and the launcher scripts the tasks run |
| `tests/` | Tests that need no sandbox |
| `legacy-tests/` | The original test scripts; they drive a live sandbox |
| `docs/` | The original instructions and notes; `docs/sphinx/`, the API documentation's sources (stage 8) |
| `notebooks/`, `notes/`, `examples/` | Material that travels with the code and is not installed |
| `requirements/` | The original requirement lists, for reference |
| `legacy/` | The files that `pyproject.toml` replaces: the root `setup.py`, `setup-plotting.sh`, and `plotting-setup.py` (the original's `cloudflow/setup.py`) |

Plotting is part of the package, `src/cloudflow/plotting/`, imported as
`cloudflow.plotting`. From stage 2 until 2026-11-13 it was a second
project, `cloudflow-plotting`; it was folded back because the workflows
import it whenever they load and nothing else ever used it on its own.

## Working on it

```sh
just init        # create the environment, with every extra
just test        # lint, type-check, fast tests
just full-test   # also build the wheel and try it in an empty environment, and build the docs
just docs        # the API documentation, into docs/sphinx/build/html
```

The API documentation is built from the installed `cloudflow`. Its sources are copies; only `conf.py` is patched,
to find the modules there instead of through paths into the old
repository. Three of its pages name modules that no longer exist
(`nodeInfo`, `nosofs_qops`, `run_adnoc`); `tests/test_docs.py` holds the
build to exactly those three failures. The built HTML that Cloud-Sandbox
commits beside the sources is not copied: `just docs` makes it.

`just test` holds new files to the full lint and type-check rules. The
copied code is held to less: every file compiles, every module imports
(four are listed in `tests/test_modules.py` with the reason they
cannot), there are no undefined names, and every file the code looks
up beside itself is in the package.

## What it expects from its surroundings

cloudflow was written to run from a checkout on a sandbox head node,
and the copy still carries those assumptions. They are counted in
`tests/outward_references.json` and explained in
[../MAP.md](../MAP.md):

- AWS credentials, and a DynamoDB table named in the cluster
  description, in which started nodes are recorded.
- A shared filesystem with `/save` (model builds), `/com` (results)
  and `/ptmp` (scratch).
- Models installed where the launcher scripts look for them.
- Prefect. The provisioning scripts run a Prefect server on the head
  node for it.

## Optional extras

| Extra | For |
| --- | --- |
| `ssh` | `dask-ssh`, which the cluster tasks start |
| `examples` | `workflows/python_examples.py` |
| `notebook` | `utils/notebook.py` |

## Licence

BSD 3-Clause; see [LICENSE](LICENSE).
