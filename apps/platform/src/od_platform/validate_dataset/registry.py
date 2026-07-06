from __future__ import annotations
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


# 1.CheckSeverity - 严重程度
class CheckSeverity:
    INFO = "INFO"  # 告知级别：工程上知道，不阻塞
    WARNING = "WARNING"  # 关注级别： 能继续，需要人工review
    ERROR = "ERROR"  # 阻塞级别 CI 必须听， 训练绝对不能继续
    PASS = "PASS"  # 通过

    _ORDER = {INFO: 1, WARNING: 2, ERROR: 3, PASS: 0, }

    @classmethod
    def rank(cls, level: str) -> int:
        return cls._ORDER.get(level, 0)


# 2.CheckResult - 单个check的统一返回类型

@dataclass
class CheckResult:
    name: str
    severity: str
    summary: str  # 一句话总结， 供终端日志 / 报告的头部使用。 给人看
    details: Dict[str, Any] = field(default_factory=dict)  # $ 结构化u详情字典 -json报告 给机器看

    @property
    def passed(self) -> bool:
        return self.severity in (CheckSeverity.PASS, CheckSeverity.INFO)


@dataclass
class CheckContext:
    """check函数的入参： 所有check函数的前面都在这"""
    yaml_path: Path
    snapshot: "DatasetSnapShot"


@dataclass(frozen=True)
class CheckEntry:
    """注册表中的一条记录。frozen-注册后不可改"""
    name: str
    func: Callable[[CheckContext], CheckResult]


# 模块级别的注册表
_REGISTRY: Dict[str, CheckEntry] = {}


def check(name: str) -> Callable:
    def decorator(func: Callable[[CheckContext], CheckResult]) -> Callable:
        if name in _REGISTRY:
            raise ValueError(
                f"check {name} 重复注册-第二次出现在 {func.__module__},{func.__name__}"
            )
        _REGISTRY[name] = CheckEntry(name=name, func=func)
        return func
    return decorator


# 自动import - 加薪的check不改框架代码的物理基础
_LAZY_INITIALIZED = False


def _lazy_init() -> None:
    """
    扫描check/*.py 自动触发@registry
    跳过 _开头的私有领域
    标志位放在import全部成功【之后】-- 任何import 失败都不污染状态，下次可重试
    """
    global _LAZY_INITIALIZED
    if _LAZY_INITIALIZED:
        return
    from od_platform.validate_dataset import checks
    from od_platform.common.registry_utils import import_submodules
    import_submodules(checks)
    _LAZY_INITIALIZED = True


# 定义查询的API
def get_all_checks() -> List[CheckEntry]:
    """返回全部注册的check"""
    _lazy_init()
    return list(_REGISTRY.values())


def get_check(name: str) -> CheckEntry:
    _lazy_init()
    if name not in _REGISTRY:
        raise ValueError(f"check {name} 未注册-已经注册的检查有: {list(_REGISTRY)}")
    return _REGISTRY[name]


def list_check_names() -> List[str]:
    """返回已注册的名字列表"""
    _lazy_init()
    return list(_REGISTRY.keys())
