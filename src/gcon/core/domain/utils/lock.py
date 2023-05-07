from pathlib import Path

from gcon.settings import LOCK_FILE


def lock(
    base_dir: Path,
    step: str,
) -> bool:
    if not base_dir.is_dir():
        raise Exception(f"Invalid `base_dir`: {base_dir}")

    lock_file_path = base_dir.joinpath(LOCK_FILE.format(step=step))

    with lock_file_path.open("w") as lock:
        lock.write("1")
    return True


def has_lock(
    base_dir: Path,
    step: str,
) -> bool:
    if not base_dir.is_dir():
        return False

    content = 0
    lock_file_path = base_dir.joinpath(LOCK_FILE.format(step=step))

    if not lock_file_path.exists():
        return False

    with lock_file_path.open("r") as lock:
        content = int(lock.read())

    if content == 1:
        return True
    return False


# ------------------------------------------------------------------------------
# SETUP DEFAULT EXPORTS
# ------------------------------------------------------------------------------


__all__ = ["lock", "has_lock"]
