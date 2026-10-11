__author__ = 'saeedamen'

import importlib

_LAZY_IMPORTS = {
    "CacheManager":   ("findatapy.util.cachemanager",  "CacheManager"),
    "CommonMan":      ("findatapy.util.commonman",      "CommonMan"),
    "ConfigManager":  ("findatapy.util.configmanager",  "ConfigManager"),
    "DataConstants":  ("findatapy.util.dataconstants",  "DataConstants"),
    "FXConv":         ("findatapy.util.fxconv",         "FXConv"),
    "LoggerManager":  ("findatapy.util.loggermanager",  "LoggerManager"),
    "Singleton":      ("findatapy.util.singleton",      "Singleton"),
    "TickerFactory":  ("findatapy.util.tickerfactory",  "TickerFactory"),
    "Twitter":        ("findatapy.util.twitter",        "Twitter"),
    "SwimPool":       ("findatapy.util.swimpool",       "SwimPool"),
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
