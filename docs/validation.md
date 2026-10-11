# Validation evidence: finmarketpy

Run date: 2026-10-12. Branch: `feature/ayu_develop`. Interpreter: `3.14.8 (main, Oct  9 2026, 15:11:09) [Clang 22.1.3 ]`.

| Check | Result |
|---|---|
| lock | passed |
| sync | passed |
| compile | passed |
| build | passed |
| tests | passed |

## Current result and compatibility decisions

- The complete supplied tests pass with current scientific dependencies.
- findatapy 0.1.42 and chartpy 0.1.16 still use deprecated UTC constructors upstream. Verified licensed local sources preserve naive-UTC results and have documented hashes, refresh/retirement instructions and original licenses.
- Chartpy imports Plotly private OHLC machinery removed in Plotly6; Plotly>=5.24.1,<6 is the proven compatible range.
- The source archive includes vendor sources; uv sources select them. Ordinary wheel installers do not interpret tool.uv.sources, so use the documented uv checkout/sdist workflow to reproduce these patches.

Current unresolved checks:

All supplied checks recorded below passed.

## Latest full-suite output

```text
$ uv run --no-sync python -m pytest
.....                                                                    [100%]
5 passed in 8.18s

```

## Exact commands and exit codes

Unsuccessful rows are retained as historical compatibility attempts; they are not claims that a current passing check remains blocked. Source-build probes use isolated temporary copies to preserve the selected repository environment.

| Command | Exit | Seconds | Evidence |
|---|---:|---:|---|
| `uv lock --upgrade --python 3.15` | 0 | 0.86 | [check record](maintenance/index.html) |
| `uv sync --all-extras --all-groups --python 3.15 --no-build --no-install-project` | 2 | 2.95 | [check record](maintenance/index.html) |
| `uv lock --upgrade --python 3.14` | 0 | 0.4 | [check record](maintenance/index.html) |
| `uv sync --all-extras --all-groups --python 3.14 --no-build --no-install-project` | 2 | 0.05 | [check record](maintenance/index.html) |
| `uv sync --all-extras --all-groups --python 3.14` | 0 | 3.36 | [check record](maintenance/index.html) |
| `uv build --python 3.14` | 0 | 0.98 | [check record](maintenance/index.html) |
| `/Users/alex/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14 -m compileall -q src` | 0 | 0.08 | [check record](maintenance/index.html) |
| `uv run --no-sync python -m pytest` | 2 | 13.42 | [check record](maintenance/index.html) |
| `uv lock --upgrade --python 3.14` | 0 | 0.7 | [check record](maintenance/index.html) |
| `uv sync --all-extras --all-groups --python 3.14` | 0 | 0.88 | [check record](maintenance/index.html) |
| `uv run --no-sync python -m pytest` | 0 | 12.56 | [check record](maintenance/index.html) |
| `uv run --no-sync python -m compileall -q src` | 0 | 0.12 | [check record](maintenance/index.html) |
| `uv build --python 3.14` | 0 | 1.04 | [check record](maintenance/index.html) |
| `uv run --no-sync python -c import sys,importlib.metadata,json; print(sys.version); print(json.dumps({d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},indent=2,sort_keys=True))` | 0 | 0.23 | [check record](maintenance/index.html) |
| `uv sync --directory /tmp/trading-python315-probes/finmarketpy --all-extras --all-groups --python 3.15` | 1 | 136.76 | [check record](maintenance/index.html) |

The versions-final log records the exact interpreter patch release and every installed dependency version. The machine-readable [verification record](maintenance/verification.json) includes branch/default ancestry, status, artifacts and unresolved checks.

## Dependency floor refresh

| Before | After |
|---|---|

The table records the initial metadata refresh. Later compatibility constraints and vendor sources are explained above and the final authoritative requirements are in [pyproject.toml](../pyproject.toml) and [uv.lock](../uv.lock). No test cases were added, removed or disabled. Existing deprecated-API cases retain their assertions while explicitly checking the documented warning.
