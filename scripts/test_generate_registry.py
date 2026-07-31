import copy
import json
import unittest
from pathlib import Path

import generate_registry as gen

DATA = Path(__file__).resolve().parent.parent / "data" / "councils.json"


class TestGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))

    def test_validate_accepts_real_data(self):
        gen.validate(self.doc)  # must not raise

    def test_validate_rejects_duplicate_id(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][1]["id"] = bad["entries"][0]["id"]
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_bad_communion(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["recognized_as_ecumenical_by"] = ["catholic", "anglican"]
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_missing_catholic(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["recognized_as_ecumenical_by"] = ["eastern_orthodox"]
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_wrong_count(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"].pop()  # drop last entry, now len != 21
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_non_contiguous_numbers(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][5]["number"] = 99  # breaks contiguity
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_malformed_id(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["id"] = "oec:trent"  # missing ordinal
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_empty_recognition_set(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["recognized_as_ecumenical_by"] = []
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_malformed_rp_crossref(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["reigning_pontiff"] = "paul-iii"  # missing rp: prefix
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_year_start_after_year_end(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["year_start"] = 400
        bad["entries"][0]["year_end"] = 300
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_century_mismatch(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["century"] = 99  # wrong century, years left valid
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_empty_significance(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["significance"] = ""
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_render_contains_all_ids_and_header(self):
        out = gen.render(self.doc)
        self.assertIn("# Ecumenical Councils", out)
        for e in self.doc["entries"]:
            self.assertIn(e["id"], out)

    def test_render_has_legend_for_communion_codes(self):
        out = gen.render(self.doc)
        for token in ["**C** =", "**EO** =", "**OO** =", "**CE** ="]:
            self.assertIn(token, out)


if __name__ == "__main__":
    unittest.main()
