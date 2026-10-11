# findatapy compatibility source

Upstream: https://github.com/cuemacro/findatapy

Current PyPI release: 0.1.42. Original source archive: https://files.pythonhosted.org/packages/a3/5c/cc6d2d87ae1e7695239ea8f91c6d5b60e031bffeefc601dfe9274b0c72b6/findatapy-0.1.42.tar.gz

SHA256: `58c572d25bbb366761b5aef8f101f02887ccee0a2d8a54b81ca5e9043d12bf4b`. The archive digest was verified before copying the package and upstream license. No upstream tests are copied or altered.

The local distribution version is `0.1.42+ayu1`. The `src/findatapy` namespace and package data are preserved. Only deprecated UTC constructors are replaced with timezone-aware UTC constructors followed by `replace(tzinfo=None)`, preserving the original naive-UTC return convention. A compatibility pyproject selects Hatch and preserves published runtime dependencies.

Patched files:

- `src/findatapy/timeseries/filter.py`
- `src/findatapy/market/marketdatagenerator.py`
- `src/findatapy/market/datavendorbbg.py`
- `src/findatapy/market/ioengine.py`
- `src/findatapy/market/marketdatarequest.py`

To refresh: download the next upstream source distribution, verify the PyPI SHA256, apply the recorded UTC replacements only if still necessary, review the diff and rerun finmarketpy's complete existing tests. Retire this vendor source after an upstream release incorporates the fixes.
