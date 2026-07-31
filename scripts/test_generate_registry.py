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
        bad["entries"][0]["recognized_as_ecumenical_by"] = ["anglican"]
        with self.assertRaises(ValueError):
            gen.validate(bad)

    def test_validate_rejects_missing_catholic(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["recognized_as_ecumenical_by"] = ["eastern_orthodox"]
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
