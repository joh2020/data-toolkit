from __future__ import annotations

import json
import sys
from pathlib import Path

from . import tools

USAGE = """usage:
  python -m data_toolkit csv-dedupe IN.csv OUT.csv
  python -m data_toolkit csv-to-json IN.csv OUT.json
  python -m data_toolkit json-to-csv IN.json OUT.csv
  python -m data_toolkit parse-log IN.log
  python -m data_toolkit validate-email ADDR
  python -m data_toolkit validate-url URL
  python -m data_toolkit validate-date YYYY-MM-DD
  python -m data_toolkit flatten-json IN.json
  python -m data_toolkit csv-stats IN.csv
  python -m data_toolkit slug TEXT
"""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        sys.stderr.write(USAGE)
        return 2
    cmd, rest = args[0], args[1:]
    if cmd == "csv-dedupe" and len(rest) == 2:
        print(tools.csv_dedupe(rest[0], rest[1]))
        return 0
    if cmd == "csv-to-json" and len(rest) == 2:
        print(tools.csv_to_json(rest[0], rest[1]))
        return 0
    if cmd == "json-to-csv" and len(rest) == 2:
        print(tools.json_to_csv(rest[0], rest[1]))
        return 0
    if cmd == "parse-log" and len(rest) == 1:
        print(json.dumps(tools.parse_log(rest[0]), ensure_ascii=False, indent=2))
        return 0
    if cmd == "validate-email" and len(rest) == 1:
        ok = tools.validate_email(rest[0])
        print("ok" if ok else "invalid")
        return 0 if ok else 1
    if cmd == "validate-url" and len(rest) == 1:
        ok = tools.validate_url(rest[0])
        print("ok" if ok else "invalid")
        return 0 if ok else 1
    if cmd == "validate-date" and len(rest) == 1:
        ok = tools.validate_date(rest[0])
        print("ok" if ok else "invalid")
        return 0 if ok else 1
    if cmd == "flatten-json" and len(rest) == 1:
        data = json.loads(Path(rest[0]).read_text(encoding="utf-8"))
        print(json.dumps(tools.flatten_json(data), ensure_ascii=False, indent=2))
        return 0
    if cmd == "csv-stats" and len(rest) == 1:
        print(json.dumps(tools.csv_stats(rest[0]), ensure_ascii=False, indent=2))
        return 0
    if cmd == "slug" and rest:
        print(tools.slug(" ".join(rest)))
        return 0
    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
