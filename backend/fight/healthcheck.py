import sys
import time
from pathlib import Path

READY_FILE = Path("/tmp/oponia-fight.ready")
READY_MAX_AGE = 10


def mark_ready() -> None:
    READY_FILE.write_text(str(time.monotonic()))


def clear_ready() -> None:
    READY_FILE.unlink(missing_ok=True)


def is_ready() -> bool:
    try:
        age = time.monotonic() - float(READY_FILE.read_text())
    except (OSError, ValueError):
        return False
    return 0 <= age < READY_MAX_AGE


if __name__ == "__main__":
    sys.exit(0 if is_ready() else 1)
