import shutil
from pathlib import Path

ORGANIZED_ROOT = Path(__file__).parent / "organized"


def organize_file(filepath: str | Path, category: str) -> Path:
    source = Path(filepath)
    dest_dir = ORGANIZED_ROOT / category
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / source.name

    if dest.exists():
        stem, suffix = source.stem, source.suffix
        for i in range(1, 10_000):
            candidate = dest_dir / f"{stem}_{i}{suffix}"
            if not candidate.exists():
                dest = candidate
                break

    shutil.move(str(source), dest)
    return dest
