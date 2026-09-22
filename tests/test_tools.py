import tempfile
import unittest
from pathlib import Path

from data_toolkit import tools


class ToolkitTests(unittest.TestCase):
    def test_csv_dedupe(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "in.csv"
            dest = Path(d) / "out.csv"
            src.write_text("id,name\n1,a\n1,a\n2,b\n", encoding="utf-8")
            n = tools.csv_dedupe(src, dest)
            self.assertEqual(n, 2)
            self.assertEqual(dest.read_text(encoding="utf-8"), "id,name\n1,a\n2,b\n")

    def test_csv_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "in.csv"
            js = Path(d) / "out.json"
            back = Path(d) / "back.csv"
            src.write_text("id,name\n1,a\n2,b\n", encoding="utf-8")
            self.assertEqual(tools.csv_to_json(src, js), 2)
            self.assertEqual(tools.json_to_csv(js, back), 2)
            self.assertEqual(back.read_text(encoding="utf-8"), "id,name\n1,a\n2,b\n")

    def test_parse_log(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.log"
            p.write_text("2026-09-22 12:00:00 INFO boot\nnot a log\n", encoding="utf-8")
            rows = tools.parse_log(p)
            self.assertEqual(rows[0]["level"], "INFO")
            self.assertEqual(rows[1]["level"], "UNKNOWN")

    def test_validators(self):
        self.assertTrue(tools.validate_email("jay@example.com"))
        self.assertFalse(tools.validate_email("nope"))
        self.assertTrue(tools.validate_url("https://example.com/x"))
        self.assertFalse(tools.validate_url("ftp://x"))
        self.assertTrue(tools.validate_date("2026-09-22"))
        self.assertFalse(tools.validate_date("22-09-2026"))

    def test_flatten_and_slug_and_stats(self):
        flat = tools.flatten_json({"a": {"b": 1}, "c": [2]})
        self.assertEqual(flat["a.b"], 1)
        self.assertEqual(flat["c[0]"], 2)
        self.assertEqual(tools.slug("Hello, World!"), "hello-world")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "in.csv"
            p.write_text("id,name\n1,a\n2,\n", encoding="utf-8")
            s = tools.csv_stats(p)
            self.assertEqual(s["row_count"], 2)
            self.assertEqual(s["empty_cells"], 1)


if __name__ == "__main__":
    unittest.main()
