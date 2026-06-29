import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PPLATFORM_SOURCE = REPO_ROOT / "apps" / "platform" / "src"

sys.path.insert(0, str(PPLATFORM_SOURCE))

from od_platform.cli.init_project import initialize_project

if __name__ == "__main__":
    initialize_project()