"""项目级共享常量——所有模块的"共同词汇表"。
放这里的标准:多模块共享(>=2 处用到) + 纯定义无逻辑 + 极少改动。本文件按需增长。
"""
from __future__ import annotations
from typing import Tuple

# —— 标注格式名(阶段 2:@register 要用,且会在多个 converter/CLI/测试复用)——
class AnnotationFormat:
    PASCAL_VOC = "pascal_voc"
    COCO       = "coco"
    YOLO       = "yolo"
    @classmethod
    def all(cls) -> Tuple[str, ...]:
        return cls.PASCAL_VOC, cls.COCO, cls.YOLO

# —— 任务类型(同上)——
class Task:
    DETECT  = "detect"
    SEGMENT = "segment"
    @classmethod
    def all(cls) -> Tuple[str, ...]:
        return cls.DETECT, cls.SEGMENT


DEFAULT_RANDOM_STATE = 1210

# —— 浮点容差(阶段 4)————————————————————————————————————————————
# 1.0 - 0.7 - 0.3 在浮点里不是 0,而是 5.55e-17。校验 test_rate >= 0 时用它吸收这种误差,
# 否则正常的 70/30 切分会被误判成"比例越界"。
RATE_EPSILON = 1e-6

class SplitStrategy:
    """train/val/test 划分策略名(阶段 4 随着撞墙②逐个长出来)。"""
    RANDOM = "random"                          # 纯随机:对稀有类不公平
    STRATIFIED = "stratified"                  # 主类别分层:稀有类不至于整体消失
    STRATIFIED_MULTILABEL = "stratified_multilabel"  # 多标签分层:连次要稀有类也照顾

    @classmethod
    def all(cls) -> Tuple[str, ...]:
        return cls.RANDOM, cls.STRATIFIED, cls.STRATIFIED_MULTILABEL

# --默认值(阶段4)------------------
DEFAULT_SPLIT_STRATEGY = SplitStrategy.RANDOM  # 不指定 --split-strategy 时的默认

# -- 类别平衡报告的判断阈值(阶段5)
CLASS_MIN_IMAGES_HARD = 2
CLASS_MIN_BOXES_WARN = 20
CLASS_MIN_BOX_SHARE = 0.01

