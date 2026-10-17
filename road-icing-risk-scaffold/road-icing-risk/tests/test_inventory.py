from pathlib import Path
from road_icing.data.inventory import scan_raw_directory


def test_scan_empty(tmp_path: Path):
    (tmp_path / "rwis").mkdir()
    (tmp_path / "rwis" / ".gitkeep").touch()
    result = scan_raw_directory(tmp_path)
    assert result["number_of_files"] == 0


def test_read_csv_header(tmp_path: Path):
    (tmp_path / "a.csv").write_text("관측시간,기온\n2025-01-01,1.0\n", encoding="utf-8")
    result = scan_raw_directory(tmp_path)
    assert result["files"][0]["columns"] == ["관측시간", "기온"]
