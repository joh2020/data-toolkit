# data-toolkit

Ten stdlib-only Python microtools. No third-party packages.

```
python -m unittest discover -s tests -v
```

```
python -m data_toolkit csv-dedupe in.csv out.csv
python -m data_toolkit csv-to-json in.csv out.json
python -m data_toolkit json-to-csv in.json out.csv
python -m data_toolkit parse-log in.log
python -m data_toolkit validate-email user@example.com
python -m data_toolkit validate-url https://example.com
python -m data_toolkit validate-date 2026-09-22
python -m data_toolkit flatten-json in.json
python -m data_toolkit csv-stats in.csv
python -m data_toolkit slug "Hello, World!"
```
