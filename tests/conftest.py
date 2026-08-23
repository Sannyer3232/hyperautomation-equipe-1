import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
HYPER_DIR = ROOT_DIR / "HyperAutomation"
SOURCE_DIR = HYPER_DIR / "source"
RESOURCES_DIR = HYPER_DIR / "resources"

for p in [str(ROOT_DIR), str(HYPER_DIR), str(SOURCE_DIR), str(RESOURCES_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)
