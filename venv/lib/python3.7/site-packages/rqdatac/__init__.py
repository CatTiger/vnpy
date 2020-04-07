# -*- coding: utf-8 -*-
import importlib
import pkgutil
import warnings

warnings.filterwarnings("ignore", message="[.\n]*Pandas[.\n]*")
warnings.simplefilter(action="ignore", category=FutureWarning)
from .client import init, reset  # noqa
from ._version import __version__  # noqa


__all__ = ["__version__", "init", "reset"]


def __go():
    for loader, module_name, is_pkg in pkgutil.walk_packages(__path__, "rqdatac."):
        if module_name.startswith("rqdatac.services") and not is_pkg:
            importlib.import_module(module_name)


__go()

del __go
