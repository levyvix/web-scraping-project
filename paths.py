import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
CONTAINER_ROOT = Path("/app")


def uses_container_paths() -> bool:
    return CONTAINER_ROOT.is_dir() and os.access(CONTAINER_ROOT, os.W_OK)


def output_directory() -> Path:
    root = CONTAINER_ROOT if uses_container_paths() else PROJECT_ROOT
    return root / "output"


def logs_directory() -> Path:
    root = CONTAINER_ROOT if uses_container_paths() else PROJECT_ROOT
    return root / "logs"
