import re
from pathlib import Path

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
_SAFE_NAME = re.compile(r"^[A-Za-z0-9_\-. ]+$")


def validate_filename(filename: str) -> str:
    """Raise ValueError if filename is unsafe; return the filename unchanged."""
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string")

    # Reject any path separators or null bytes
    if "/" in filename or "\\" in filename or "\x00" in filename:
        raise ValueError(f"Invalid filename: {filename!r}")

    # Only allow safe character set
    if not _SAFE_NAME.match(filename):
        raise ValueError(f"Invalid filename: {filename!r}")

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext!r}. Allowed: {sorted(ALLOWED_EXTENSIONS)}")

    return filename
