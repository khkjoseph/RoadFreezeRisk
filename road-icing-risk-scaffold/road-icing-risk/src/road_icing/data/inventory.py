"""Lightweight inventory: inspect paths, archive members and CSV headers, not full data."""
from __future__ import annotations

import csv
import json
import zipfile
from collections import Counter
from pathlib import Path


def _csv_header(path: Path) -> dict:
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            with path.open("r", encoding=encoding, newline="") as fp:
                sample = fp.read(4096)
            if not sample.strip():
                return {"encoding": encoding, "columns": []}
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            line = next(csv.reader(sample.splitlines(), dialect=dialect), [])
            return {"encoding": encoding, "columns": line}
        except (UnicodeError, OSError, csv.Error, StopIteration):
            continue
    return {"warning": "Unable to read header; inspect manually"}


def scan_raw_directory(raw_dir: Path) -> dict:
    """List files under raw_dir without reading or altering the actual dataset."""
    raw_dir = Path(raw_dir)
    if not raw_dir.exists():
        raise FileNotFoundError(f"No such raw directory: {raw_dir}")
    records = []
    for path in sorted(raw_dir.rglob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        item = {"relative_path": path.relative_to(raw_dir).as_posix(),
                "extension": path.suffix.lower(), "bytes": path.stat().st_size}
        if path.suffix.lower() in {".csv", ".tsv"}:
            item.update(_csv_header(path))
        elif path.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(path) as zf:
                    members = zf.infolist()
                    item["archive_entry_count"] = len(members)
                    item["archive_total_uncompressed_bytes"] = sum(i.file_size for i in members)
                    item["archive_extensions"] = dict(Counter(
                        Path(i.filename).suffix.lower() for i in members if not i.is_dir()))
                    item["archive_first_paths"] = [i.filename for i in members[:20]]
            except (zipfile.BadZipFile, OSError) as exc:
                item["warning"] = str(exc)
        elif path.suffix.lower() == ".shp":
            required = [path.with_suffix(x).exists() for x in (".shx", ".dbf", ".prj")]
            item["shapefile_sidecars"] = {k: v for k, v in zip(("shx", "dbf", "prj"), required)}
        records.append(item)
    return {"raw_dir": str(raw_dir), "number_of_files": len(records), "files": records}


def write_inventory(raw_dir: Path, out: Path) -> dict:
    result = scan_raw_directory(raw_dir)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
