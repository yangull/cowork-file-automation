import time
from pathlib import Path

from pypdf import PdfReader
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

from classifier import classify_file
from organizer import organize_file

WATCH_DIR = Path(__file__).parent / "watch"
_STABLE_POLLS = 3       # consecutive same-size reads required
_POLL_INTERVAL = 0.2    # seconds between size checks


def _wait_until_written(path: Path) -> None:
    """Block until the file size stops changing across consecutive polls."""
    last_size = -1
    stable = 0
    while stable < _STABLE_POLLS:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            size = -1
        if size != -1 and size == last_size:
            stable += 1
        else:
            stable = 0
            last_size = size
        time.sleep(_POLL_INTERVAL)


def _read_text(path: Path) -> str | None:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


class FileOrganiserHandler(FileSystemEventHandler):
    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return

        path = Path(event.src_path)
        _wait_until_written(path)
        content = _read_text(path)

        if content is None:
            print(f"[skip]  {path.name} — binary file")
            return

        category = classify_file(path.name, content)
        dest = organize_file(path, category)
        print(f"[done]  {path.name} → {category} → {dest}")


def start() -> None:
    WATCH_DIR.mkdir(exist_ok=True)
    handler = FileOrganiserHandler()
    observer = Observer()
    observer.schedule(handler, str(WATCH_DIR), recursive=False)
    observer.start()
    print(f"Watching {WATCH_DIR} ...")
    try:
        while observer.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
