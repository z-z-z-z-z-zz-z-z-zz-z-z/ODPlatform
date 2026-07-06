import logging

from pathlib import Path
from od_platform.validate_dataset.registry import CheckContext, list_check_names
from od_platform.validate_dataset.service import run_all_checks
from od_platform.common.paths import LOGGING_DIR
from od_platform.common.logging_utils import get_logger
from od_platform.validate_dataset.snapshot import build_snapshot


get_logger(
    base_path=LOGGING_DIR,
    log_type="数据质检测试",
    temp_log=False,
)


print(f"已经注册的check: {list_check_names()}")

yaml_path = Path(r"E:\PYthon\PYcharm\workplace_py\ODPlatform\apps\platform\configs\datasets\rsod.yaml")
snap = build_snapshot(yaml_path, task_type="detect")
print(f"数据集: {yaml_path.name}")
print(f"task: {yaml_path.name}")
print(f"nc: {snap.nc}")
print(f"names: {snap.class_names}")
print(f"yaml数据: {snap.yaml_data}")
print(snap)


ctx = CheckContext(yaml_path=Path(r"E:\PYthon\PYcharm\workplace_py\ODPlatform\apps\platform\configs\datasets\rsod.yaml"))
results = run_all_checks(ctx)
for r in results:
    print(r.severity, r.name, '-', r.summary)
    if r.details.get('problems'):
        for p in r.details['problem']:
            print(f" - {p}")
