# cloudflow: the workflow engine as an installable project.

set shell := ["bash", "-euo", "pipefail", "-c"]

# The import tests load every module, so the environment always has every extra.
run := "uv run --all-extras"

# List the targets.
default:
    @just --justfile {{ justfile() }} --list

# Create the environment and install the project, every extra and the development tools.
init:
    uv sync --all-extras

# Build the source distribution and the wheel into dist/.
build:
    uv build

# New files get the full rule set; copied code must have no syntax errors and no undefined names.
lint:
    {{ run }} ruff check tests
    {{ run }} ruff format --check tests
    {{ run }} ruff check --isolated --select E9,F63,F7,F82 src

# Type-check the new files; any error fails.
typecheck:
    {{ run }} pyright

# Lint, type-check and the fast tests.
test: lint typecheck
    {{ run }} pytest -q -m "not slow"

# Everything in test, then build the wheels and try them in an empty environment, and build the documentation.
full-test: test
    {{ run }} pytest -q -m slow

# Build the API documentation into docs/sphinx/build/html (stage 8).
docs:
    {{ run }} sphinx-build -b html docs/sphinx/source docs/sphinx/build/html

# Nothing is published from a copy inside Cloud-Sandbox.
release: full-test
    @echo "cloudflow: nothing to release from exportit/; see exportit/MAP.md"
