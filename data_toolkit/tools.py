from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
LOG_RE = re.compile(
    r"^(?P<ts>\S+\s+\S+)\s+(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL)\s+(?P<msg>.*)$"
)


def csv_dedupe(src: str | Path, dest: str | Path, key_fields: list[str] | None = None) -> int:
    src, dest = Path(src), Path(dest)
    seen: set[tuple[str, ...]] = set()
    kept = 0
    with src.open(newline="", encoding="utf-8") as fin, dest.open(
        "w", newline="", encoding="utf-8"
    ) as fout:
        reader = csv.DictReader(fin)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")
        keys = key_fields or list(reader.fieldnames)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            sig = tuple(row.get(k, "") for k in keys)
            if sig in seen:
                continue
            seen.add(sig)
            writer.writerow(row)
            kept += 1
    return kept


def csv_to_json(src: str | Path, dest: str | Path) -> int:
    src, dest = Path(src), Path(dest)
    with src.open(newline="", encoding="utf-8") as fin:
        rows = list(csv.DictReader(fin))
    dest.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(rows)


def json_to_csv(src: str | Path, dest: str | Path) -> int:
    src, dest = Path(src), Path(dest)
    data = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("JSON must be a non-empty list of objects")
    if not all(isinstance(x, dict) for x in data):
        raise ValueError("JSON must be a list of objects")
    fields: list[str] = []
    for row in data:
        for k in row:
            if k not in fields:
                fields.append(k)
    with dest.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow({k: row.get(k, "") for k in fields})
    return len(data)


def parse_log(src: str | Path) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for raw in Path(src).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = LOG_RE.match(line)
        if m:
            out.append(m.groupdict())
        else:
            out.append({"ts": "", "level": "UNKNOWN", "msg": line})
    return out


def validate_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value.strip()))


def validate_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_date(value: str, fmt: str = "%Y-%m-%d") -> bool:
    try:
        datetime.strptime(value.strip(), fmt)
        return True
    except ValueError:
        return False


def flatten_json(obj: Any, prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            flat.update(flatten_json(v, key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}[{i}]" if prefix else f"[{i}]"
            flat.update(flatten_json(v, key))
    else:
        flat[prefix] = obj
    return flat


def csv_stats(src: str | Path) -> dict[str, Any]:
    src = Path(src)
    with src.open(newline="", encoding="utf-8") as fin:
        reader = csv.reader(fin)
        header = next(reader, None)
        rows = list(reader)
    return {
        "path": str(src),
        "columns": header or [],
        "column_count": len(header or []),
        "row_count": len(rows),
        "empty_cells": sum(1 for row in rows for cell in row if cell.strip() == ""),
    }


def slug(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")
