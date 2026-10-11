__author__ = 'saeedamen'

import importlib

_LAZY_IMPORTS = {
    "Timezone":    ("findatapy.timeseries.timezone",     "Timezone"),
    "Calendar":    ("findatapy.timeseries.calendar",     "Calendar"),
    "Filter":      ("findatapy.timeseries.filter",       "Filter"),
    "Calculations":("findatapy.timeseries.calculations", "Calculations"),
    "DataQuality": ("findatapy.timeseries.dataquality",  "DataQuality"),
    "RetStats":    ("findatapy.timeseries.retstats",     "RetStats"),
}


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        module_path, class_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        globals()[name] = cls
        return cls
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return list(_LAZY_IMPORTS)
