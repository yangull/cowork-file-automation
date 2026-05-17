import pytest
from pathlib import Path
import organizer


@pytest.fixture
def tmp_organized(tmp_path, monkeypatch):
    organized = tmp_path / "organized"
    monkeypatch.setattr(organizer, "ORGANIZED_ROOT", organized)
    return organized


def make_source(tmp_path: Path, name: str = "file.txt", content: str = "data") -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_moves_file_to_category_subfolder(tmp_path, tmp_organized):
    source = make_source(tmp_path)
    dest = organizer.organize_file(source, "cv")
    assert dest == tmp_organized / "cv" / "file.txt"
    assert dest.exists()


def test_source_file_is_removed(tmp_path, tmp_organized):
    source = make_source(tmp_path)
    organizer.organize_file(source, "invoice")
    assert not source.exists()


def test_creates_category_subfolder(tmp_path, tmp_organized):
    source = make_source(tmp_path)
    organizer.organize_file(source, "job_description")
    assert (tmp_organized / "job_description").is_dir()


def test_preserves_file_content(tmp_path, tmp_organized):
    source = make_source(tmp_path, content="hello world")
    dest = organizer.organize_file(source, "other")
    assert dest.read_text() == "hello world"


def test_collision_renames_with_suffix(tmp_path, tmp_organized):
    s1 = make_source(tmp_path, "report.txt", "first")
    s2 = tmp_path / "copy"
    s2.mkdir()
    s2 = s2 / "report.txt"
    s2.write_text("second")

    d1 = organizer.organize_file(s1, "cv")
    d2 = organizer.organize_file(s2, "cv")

    assert d1 == tmp_organized / "cv" / "report.txt"
    assert d2 == tmp_organized / "cv" / "report_1.txt"
    assert d1.read_text() == "first"
    assert d2.read_text() == "second"


def test_collision_increments_until_free(tmp_path, tmp_organized):
    # Pre-populate report.txt and report_1.txt so the third gets report_2.txt
    category_dir = tmp_organized / "cv"
    category_dir.mkdir(parents=True)
    (category_dir / "report.txt").write_text("existing")
    (category_dir / "report_1.txt").write_text("existing")

    source = make_source(tmp_path, "report.txt", "new")
    dest = organizer.organize_file(source, "cv")
    assert dest == tmp_organized / "cv" / "report_2.txt"


def test_accepts_string_filepath(tmp_path, tmp_organized):
    source = make_source(tmp_path, "doc.txt")
    dest = organizer.organize_file(str(source), "image")
    assert dest.exists()


def test_returns_path_object(tmp_path, tmp_organized):
    source = make_source(tmp_path)
    dest = organizer.organize_file(source, "other")
    assert isinstance(dest, Path)
