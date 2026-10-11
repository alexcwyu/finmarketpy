__author__ = 'saeedamen'

import importlib

_LAZY_IMPORTS = {
    "DataVendor":         ("findatapy.market.datavendor",         "DataVendor"),
    "IOEngine":           ("findatapy.market.ioengine",           "IOEngine"),
    "SpeedCache":         ("findatapy.market.ioengine",           "SpeedCache"),
    "Market":             ("findatapy.market.market",             "Market"),
    "FXVolFactory":       ("findatapy.market.market",             "FXVolFactory"),
    "FXCrossFactory":     ("findatapy.market.market",             "FXCrossFactory"),
    "FXConv":             ("findatapy.market.market",             "FXConv"),
    "RatesFactory":       ("findatapy.market.market",             "RatesFactory"),
    "MarketDataGenerator":("findatapy.market.marketdatagenerator","MarketDataGenerator"),
    "MarketDataRequest":  ("findatapy.market.marketdatarequest",  "MarketDataRequest"),
}

# don't include DataVendorBBG, in case users haven't installed blpapi


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
