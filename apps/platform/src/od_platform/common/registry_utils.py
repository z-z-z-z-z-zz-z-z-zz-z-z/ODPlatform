from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType

def import_submodules(package: ModuleType) -> None :
    """
    import package下所有非下划线的子模块，触发其中的@register装饰器，实现自动注册机制
    """

    for m in pkgutil.iter_modules(package.__path__):
        if not m.name.startswith("_"):
            importlib.import_module(f"{package.__name__}.{m.name}")