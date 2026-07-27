# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Neighbors is a Python library of functions for working with the segments of the TMT mirror.
A figure showing the mirror segments called Mirror.png is available in this directory.

* There are 492 hexagonal mirror segments. Each segment has 6 edges. 
* The segments are arranged in 6 sectors called A, B, C, D, E, and F in a counter-clockwise direction.
* Each sector has 82 segments.
* There is a hole in the center of the mirror with no segments.
* Segments are numbered 1 through 82.
* The segment numbers in each sector start at the center and increase with each ring. This numbering must be followed.
* A segment identifier is a combination of a sector letter and a segment number, e.g. `A1`, `B82`, `C42`, etc.
* Segments can also be given a number ranging from 1 to 492 that identifies the mirror location starting from A1=1 and ending with F82=492.
* Each segment has neighbor segments. 
* Based on its position in the mirror, a segment can have 3, 4, 5, or 6 neighbors.
* For instance, segment A15 has neighbors A10, A16, A22, A21, B27, and B20. But segment A77 has only 3 neighbors: A68, A69, and A78.

The following should be done:

* Create one or more data structures to model the mirror and its segments and segment neighbors.
* Create a function called 'neighbors' to return the neighbors of a segment given its identifier (i.e. A22). 
  The function takes a single segment identifier as input and returns a list of neighbor segment identifiers.

## Commands

# Python Package Management with uv

Use uv exclusively for Python package management in this project.

## Package Management Commands

- All Python dependencies **must be installed, synchronized, and locked** using uv
- Never use pip, pip-tools, poetry, or conda directly for dependency management

All commands must be run via `uv run`. Never call `python`, `pytest`, `ruff`, or other tools directly.

```bash
uv run pytest                   # run all tests
uv run pytest tests/test_foo.py # run a single test file
uv run ruff check .             # lint
uv run ruff check --fix .       # lint and auto-fix
uv run ruff format .            # format
uv run ruff format --check .    # check formatting
uv run ty check                 # type check (or: uv run mypy .)
uv run python -m module_name    # run a module
```

## Project Management

Uses `uv` exclusively — no pip, poetry, conda, or manual venv activation.

```bash
uv add <package>           # add dependency
uv add --dev <package>     # add dev dependency
uv remove <package>        # remove dependency
uv sync                    # sync environment
uv lock                    # update lockfile
```

Dependencies go in `pyproject.toml` (PEP 621). Never create `setup.py`, `setup.cfg`, or `requirements.txt`.

## Architecture

- Python 3.14, optimized for performance — use async/parallelism wherever possible
- Use uv to install the proper Python version in a virtual environment if not available.
- Apache Arrow for data serialization/transmission (docs: https://arrow.apache.org/docs/python/)
- Tests in `tests/` at project root, named `test_*.py`, no `__init__.py` needed

## Code Style

- ruff for linting and formatting (88 char line length, double quotes, spaces)
- Import sorting via ruff (`select = ["I"]`)
- No `# type: ignore` without an error code
- Configuration in `pyproject.toml` under `[tool.ruff]`
