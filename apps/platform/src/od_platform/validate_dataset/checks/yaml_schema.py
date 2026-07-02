#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :yaml_schema.py
# @Time      :2026/7/2 13:01:52
# @Author    :雨霓同学
# @Project   :ODPlatform
# @Function  :
"""
yaml_schema check: 验证数据集yaml文件的字段完整性和一致性

检查项：任何一项失败都要标记ERROR
    1. yaml文件存在而且要能解析
    2. yaml文件的顶层肯定是一个字典
    3. 包含nc字段，是正整数
    4. 包含names字段，是一个字符串列表，或者是一个字典
    5. nc字段的值等于names字段中元素个数
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple
import yaml  # pip install pyyaml
from polars.expr import name

from od_platform.validate_dataset.registry import (check, CheckContext, CheckResult, CheckSeverity)
@check("yaml_schema")
def validate_yaml_schema(ctx: CheckContext) -> CheckResult:
    yaml_path = ctx.yaml_path
    # 第一项检查，文件不存在
    if not yaml_path.exists():
        return CheckResult(
            name = "yaml_schema",
            severity = CheckSeverity.ERROR,
            summary = f"yaml文件不存在: {yaml_path}",
            details = {"reason": "file_not_found","yaml_path": str(yaml_path)}
        )

    # 第二项检查： 解析失败
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return CheckResult(
            name = "yaml_schema",
            severity = CheckSeverity.ERROR,
            summary = f"yaml文件解析失败: {e}",
            details = {"reason": "parse_error", "yaml_path": str(yaml_path), "parseer_error": str(e)}
        )
    except OSError as e:
        return CheckResult(
            name = "yaml_schema",
            severity = CheckSeverity.ERROR,
            summary = f"yaml文件读取失败: {e}",
            details = {"reason": "read_error", "yaml_path": str(yaml_path), "os_error": str(e)}
        )
    # 第三项检查：顶层是否是字典
    if not isinstance(cfg, dict):
        return CheckResult(
            name = "yaml_schema",
            severity = CheckSeverity.ERROR,
            summary = f"yaml文件的顶层不是字典: {type(cfg).__name__}",
            details = {"reason": "not_dict","actual_type": str(type(cfg).__name__)}
        )
    # 第四-六项检查
    problems : List[str] = []
    nc =cfg.get("nc")
    if not isinstance(nc, int) or nc <= 0:
        problems.append(f"nc字段不存在或者不是正整数: {nc}")
        nc = None # 防止下面继续检查
    names_raw = cfg.get("names")
    names_counts, names_problem = _validate_names(names_raw)
    if names_problem:
        problems.append(names_problem)

    if nc is not None and names_counts is not None and nc != names_counts:
        problems.append(f"nc字段的值({nc})与names字段中元素个数({names_counts})不相等")

    if problems:
        return CheckResult(
            name = "yaml_schema",
            severity = CheckSeverity.ERROR,
            summary = f"yaml文件字段不一致：{len(problems)}处问题",
            details = {"reason": "field_inconsistency", "problems": problems,
                    "nc": nc, "names_count": names_counts}
        )

    return CheckResult(
        name = "yaml_schema",
        severity = CheckSeverity.INFO,
        summary = f"yaml文件字段一致,(nc={nc}, names_count={names_counts})",
        details = {"nc": nc, "names_count": names_counts}
    )

def _validate_names(names_raw: Any) -> Tuple[Any, str]:
    if isinstance(names_raw, list):
        if not names_raw:
            return None, "names 是空列表"
        if not all(isinstance(n, str) and n for n in names_raw):
            return None, "names 列表中包含非字符串元素"
        return len(names_raw), ""

    if isinstance(names_raw, dict):
        if not names_raw:
            return None, "names 是空字典"
        if not all(isinstance(k, int)  for k in names_raw.keys()):
            return None, "names 字典的键必须是int类型"
        if not all(isinstance(n, str) and n for n in names_raw.values()):
            return None, "names 字典的值必须是字符串类型"
        return len(names_raw), ""
    return  None, f"names 不是合法的列表或字典： {type(names_raw).__name__}"
