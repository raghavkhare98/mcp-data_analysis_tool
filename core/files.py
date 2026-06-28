from pathlib import Path

import pandas as pd

from config import get_settings
from security.path_guard import ALLOWED_EXTENSIONS, validate_filename


def list_available_files() -> list[str]:
    settings = get_settings()
    return sorted(
        p.name
        for p in settings.staging_dir.iterdir()
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
    )


def load_dataframe(filename: str) -> pd.DataFrame:
    settings = get_settings()
    validate_filename(filename)

    path = settings.staging_dir / filename

    try:
        path.resolve().relative_to(settings.staging_dir)
    except ValueError:
        raise ValueError(f"Path traversal detected for: {filename!r}")

    if not path.exists():
        raise FileNotFoundError(f"File not found in staging: {filename!r}")

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise ValueError(
            f"File {filename!r} is {size_mb:.1f} MB, exceeds limit of {settings.max_file_size_mb} MB"
        )

    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path)
    elif ext == ".xlsx":
        return pd.read_excel(path, engine="openpyxl")
    elif ext == ".xls":
        return pd.read_excel(path, engine="xlrd")
    else:
        raise ValueError(f"Unsupported extension: {ext!r}")
