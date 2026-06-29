from pathlib import Path
from typing import List, Tuple

#找到workspace根目录
WORKSPACE_MARKER: str = ".odp-workspace"

def _find_workspace_root(start: Path,
                markers: Tuple[str, ...] = (WORKSPACE_MARKER,)
                ) -> Path:
    current = start.resolve()
    if current.is_file():
        current =current.parent
    for parent in [current, *current.parents]:
        for marker in markers:
            if (parent / marker).exists():
                return parent
    raise FileNotFoundError(f"找不到workspace marker文件（{markers}"
                                f"请确认仓库根目录已存在 {WORKSPACE_MARKER} 文件")

#计算ROOT_DIR位置
ROOT_DIR: Path = _find_workspace_root(Path(__file__))

#
APP_DIR: Path = ROOT_DIR / "apps" / "platform"

#
DATA_DIR: Path = ROOT_DIR / "data"
MODELS_DIR: Path = ROOT_DIR / "models"
RUNS_DIR: Path = ROOT_DIR / "runs"

#
PRETRAINED_MODELS_DIR: Path = MODELS_DIR / "pretrained"
TRAINED_MODELS_DIR: Path = MODELS_DIR / "trained"

#
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

#
CONFIGS_DIR: Path = APP_DIR / "configs"
LOGGING_DIR: Path = APP_DIR / "logging"
UNIT_TEST_DIR: Path = APP_DIR / "tests"

#顶层的文档目录
DOCS_DIR: Path = ROOT_DIR / "docs"

#工程基础
SCRIPTS_DIR: Path = ROOT_DIR / "scripts"

#对外暴露的要初始化的目录列表
def get_dirs_to_initialize() -> List[Path]:
    return [
        DATA_DIR,
        MODELS_DIR,
        RUNS_DIR,
        PRETRAINED_MODELS_DIR,
        TRAINED_MODELS_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        CONFIGS_DIR,
        LOGGING_DIR,
        UNIT_TEST_DIR,
        DOCS_DIR,
        SCRIPTS_DIR,
    ]

if __name__ == "__main__" :
    print(f"ROOT DIR (workspace) ={ROOT_DIR}")
    print(f"APP DIR = {APP_DIR}")
    print(f"DATA_DIR ={DATA_DIR}")
    print(f"MODELS_DIR = {MODELS_DIR}")
    print(f"RUNS_DIR = {RUNS_DIR}")
    print(f"PRETRAINED_MODELS_DIR = {PRETRAINED_MODELS_DIR}")
    print(f"TRAINED_MODELS_DIR = {TRAINED_MODELS_DIR}")
    print(f"RAW_DATA_DIR = {RAW_DATA_DIR}")
    print(f"PROCESSED_DATA_DIR = {PROCESSED_DATA_DIR}")
    print(f"CONFIGS_DIR = {CONFIGS_DIR}")
    print(f"LOGGING_DIR = {LOGGING_DIR}")
    print(f"UNIT_TEST_DIR = {UNIT_TEST_DIR}")
    for d in get_dirs_to_initialize():
        print(f"将要初始化的目录有 : {d.relative_to(ROOT_DIR)}")