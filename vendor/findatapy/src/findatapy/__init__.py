__author__ = 'saeedamen'

import importlib

_LAZY_IMPORTS = {
    "market":     ("findatapy.market",     None),
    "timeseries": ("findatapy.timeseries", None),
    "util":       ("findatapy.util",       None),
}


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        module_path, _ = _LAZY_IMPORTS[name]
        mod = importlib.import_module(module_path)
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return list(_LAZY_IMPORTS)
