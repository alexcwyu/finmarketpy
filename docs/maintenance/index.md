# finmarketpy: portable verification records

Full raw logs are retained in the workspace maintenance evidence, not distributed here. Hashes identify those original logs. A successful build or selected test subset does not imply a full test-suite pass. Commands containing <workspace> describe the original execution environment.

[Machine-readable records](verification.json) · [Repository validation summary](../validation.md)

## Executed commands

| Check | Exit | Duration | Command | Outcomes |
| --- | ---: | ---: | --- | --- |
| build | 0 | 0.98s | `uv build --python 3.14` | Successfully built dist/finmarketpy-0.11.19.tar.gz<br>Successfully built dist/finmarketpy-0.11.19-py3-none-any.whl |
| build-final | 0 | 1.04s | `uv build --python 3.14` | Successfully built dist/finmarketpy-0.11.19.tar.gz<br>Successfully built dist/finmarketpy-0.11.19-py3-none-any.whl |
| compile | 0 | 0.08s | `/Users/alex/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14 -m compileall -q src` | See exit status; no test-count assertion. |
| compile-final | 0 | 0.12s | `uv run --no-sync python -m compileall -q src` | See exit status; no test-count assertion. |
| lock-3.14 | 0 | 0.4s | `uv lock --upgrade --python 3.14` | See exit status; no test-count assertion. |
| lock-3.15 | 0 | 0.86s | `uv lock --upgrade --python 3.15` | See exit status; no test-count assertion. |
| lock-chartpy-compatibility | 0 | 0.7s | `uv lock --upgrade --python 3.14` | See exit status; no test-count assertion. |
| python315-source-probe | 1 | 136.76s | `uv sync --directory /tmp/trading-python315-probes/finmarketpy --all-extras --all-groups --python 3.15` | See exit status; no test-count assertion. |
| sync-3.14 | 0 | 3.36s | `uv sync --all-extras --all-groups --python 3.14` | See exit status; no test-count assertion. |
| sync-chartpy-compatibility | 0 | 0.88s | `uv sync --all-extras --all-groups --python 3.14` | See exit status; no test-count assertion. |
| tests | 2 | 13.42s | `uv run --no-sync python -m pytest` | See exit status; no test-count assertion. |
| tests-chartpy-compatibility | 0 | 12.56s | `uv run --no-sync python -m pytest` | 5 passed in 8.18s |
| versions-final | 0 | 0.23s | `uv run --no-sync python -c import sys,importlib.metadata,json; print(sys.version); print(json.dumps({d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},indent=2,sort_keys=True))` | See exit status; no test-count assertion. |
| wheel-probe-3.14 | 2 | 0.05s | `uv sync --all-extras --all-groups --python 3.14 --no-build --no-install-project` | See exit status; no test-count assertion. |
| wheel-probe-3.15 | 2 | 2.95s | `uv sync --all-extras --all-groups --python 3.15 --no-build --no-install-project` | See exit status; no test-count assertion. |
