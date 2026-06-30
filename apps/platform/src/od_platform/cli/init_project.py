#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :init_project.py
# @Time      :2026/6/29 14:29:08
# @Author    :雨霓同学
# @Project   :ODPlatform
# @Function  :初始化脚本
import logging
from pathlib import Path
from typing import  List

from od_platform.common.paths import ROOT_DIR, get_dirs_to_initialize, LOGGING_DIR,RAW_DATA_DIR
from od_platform.common.logging_utils import get_logger
from od_platform.common.string_utils import format_table_row, format_table_separator
from od_platform.common.performance_utils import time_it
from od_platform.common.system_utils import log_device_info

LINE_WIDTH = 60
logger = logging.getLogger(__name__)

def _check_raw_data_status() -> List[str]:
    raw_status: List[str] = []
    rel_raw = RAW_DATA_DIR.relative_to(ROOT_DIR)

    if not RAW_DATA_DIR.exists():
        logger.warning(f"原始数据目录不存在: {rel_raw}，请在该目录下放置原始数据文件")
        raw_status.append(f"{rel_raw}不存在，-> 请创建并放入数据")
    elif not any(RAW_DATA_DIR.iterdir()):
        logger.warning(f"原始数据目录为空: {rel_raw}，请在该目录下放置原始数据文件"
                    f"预期的组织形式为：\n"
                    f"  {rel_raw}/<数据集名称>/\n"
                    f"  ├───images\n"
                    f"  └───annotations")
        raw_status.append(f"{rel_raw}为空，-> 请创建并放入至少一个数据集")
    else:
        sub_dirs = [p for p in RAW_DATA_DIR.iterdir() if p.is_dir()]
        logger.info(f"检测到原始数据目录: {rel_raw}，共有{len(sub_dirs)}个数据集文件夹")
        raw_status.append(f"{rel_raw}存在，包含{len(sub_dirs)}个数据集")
        for sub in sorted(sub_dirs):
            raw_status.append(f"   {sub.name}")
    return raw_status


@time_it(iterations=1, name="项目初始化",logger_instance=logger)
def initialize_project() -> None:
    """
    初始化项目
    """
    logger = get_logger(
        base_path=LOGGING_DIR,
        log_type="init_project",
        temp_log=False,
    )

    log_device_info(target_logger=logger)
    logger.info("开始初始化项目核心目录".center(LINE_WIDTH, '='))
    print(f"项目根目录: {ROOT_DIR}")

    created: List[Path] = []
    existed: List[Path] = []

    for d in get_dirs_to_initialize():
        rel = d.relative_to(ROOT_DIR)
        if d.exists():
            logger.info(f"目录已存在: {rel}")
            existed.append(d)
        else:
            try:
                d.mkdir(parents=True, exist_ok=True)
                created.append(d)
                logger.info(f"成功创建目录: {rel}")
            except OSError as e:
                logger.error(f"创建目录失败: {rel}: {e}")
                raise SystemExit(1) from e

    raw_status = _check_raw_data_status()

    logger.info("初始化汇总".center(LINE_WIDTH, '='))
    widths = [30, 12]
    aligns = ["left", "right"]
    logger.info(format_table_row(["目录", "状态"], widths, aligns))
    logger.info(format_table_separator(widths))
    for d in created:
        logger.info(format_table_row([str(d.relative_to(ROOT_DIR)), "已创建"], widths, aligns))
    for d in existed:
        logger.info(format_table_row([str(d.relative_to(ROOT_DIR)), "已存在"], widths, aligns))
    logger.info("-" * LINE_WIDTH)

if __name__ == "__main__":

    initialize_project()

