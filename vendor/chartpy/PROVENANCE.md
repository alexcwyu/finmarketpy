# chartpy UTC compatibility source

Upstream: https://github.com/cuemacro/chartpy

PyPI release 0.1.16. Source archive https://files.pythonhosted.org/packages/c5/d2/dda06ca67c3e8b9064bc0fa69eb32a56a6d2f078ec2102f680d03ade9f51/chartpy-0.1.16.tar.gz

Verified SHA256 `b94c1143d145380057a1a4d8a608661ad63bc5695c7a106444e5bb8e9cfd9eb7`; original license and package data retained.

Only deprecated datetime.datetime.utcnow calls are replaced by timezone-aware UTC constructors followed by replace(tzinfo=None), preserving naive UTC. The same deprecation remains in upstream master https://raw.githubusercontent.com/cuemacro/chartpy/master/chartpy/style.py when checked on 2026-10-12. Local version 0.1.16+ayu1.

Patched files: src/chartpy/style.py. Refresh from a verified upstream sdist and retire this path source when upstream releases the fix. Finmarketpy's existing complete suite verifies the integration; no new tests are copied or added.
