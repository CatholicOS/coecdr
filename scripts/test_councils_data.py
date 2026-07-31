import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "councils.json"
ID_RE = re.compile(r"^oec:[a-z]+(?:-[a-z]+)*-[ivx]+$")
COMMUNIONS = {"catholic", "eastern_orthodox", "oriental_orthodox", "church_of_the_east"}
RP_RE = re.compile(r"^rp:[a-z]+(?:-[a-z]+)*-[ivx]+$|^rp:peter$")


class TestCouncilsData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.entries = cls.doc["entries"]

    def test_count_is_21(self):
        self.assertEqual(self.doc["council_count"], 21)
        self.assertEqual(len(self.entries), 21)

    def test_numbers_contiguous_1_to_21(self):
        self.assertEqual([e["number"] for e in self.entries], list(range(1, 22)))

    def test_ids_unique_and_well_formed(self):
        ids = [e["id"] for e in self.entries]
        self.assertEqual(len(ids), len(set(ids)), "duplicate IDs")
        for i in ids:
            self.assertRegex(i, ID_RE, f"malformed id: {i}")

    def test_recognition_vocabulary_and_catholic_present(self):
        for e in self.entries:
            rec = e["recognized_as_ecumenical_by"]
            self.assertTrue(rec, f"{e['id']}: empty recognition")
            self.assertIn("catholic", rec, f"{e['id']}: missing catholic")
            self.assertTrue(set(rec) <= COMMUNIONS, f"{e['id']}: bad vocab {rec}")

    def test_recognition_matrix(self):
        by_num = {e["number"]: set(e["recognized_as_ecumenical_by"]) for e in self.entries}
        self.assertEqual(by_num[1], COMMUNIONS)
        self.assertEqual(by_num[2], COMMUNIONS)
        self.assertEqual(by_num[3], {"catholic", "eastern_orthodox", "oriental_orthodox"})
        self.assertEqual(by_num[4], {"catholic", "eastern_orthodox"})
        for n in range(5, 8):
            self.assertEqual(by_num[n], {"catholic", "eastern_orthodox"})
        for n in range(8, 22):
            self.assertEqual(by_num[n], {"catholic"})

    def test_rp_crossrefs_well_formed(self):
        for e in self.entries:
            for ref in [e["reigning_pontiff"], e["convened_by"]["rp"], e["confirmed_by"]]:
                if ref is not None:
                    self.assertRegex(ref, RP_RE, f"{e['id']}: bad rp ref {ref}")

    def test_rp_crossrefs_exist_in_crpdr(self):
        crpdr = DATA.parent.parent.parent / "crpdr" / "data" / "pontiffs.json"
        if not crpdr.exists():
            self.skipTest("crpdr not present")
        pope_ids = {p["id"] for p in json.loads(crpdr.read_text(encoding="utf-8"))["entries"]}
        for e in self.entries:
            for ref in [e["reigning_pontiff"], e["convened_by"]["rp"], e["confirmed_by"]]:
                if ref is not None:
                    self.assertIn(ref, pope_ids, f"{e['id']}: {ref} not in CRPDR")

    def test_year_and_century_consistency(self):
        for e in self.entries:
            self.assertLessEqual(e["year_start"], e["year_end"])
            self.assertEqual(e["century"], (e["year_start"] - 1) // 100 + 1, e["id"])

    def test_required_prose_present(self):
        for e in self.entries:
            self.assertTrue(e["significance"].strip(), f"{e['id']}: empty significance")


if __name__ == "__main__":
    unittest.main()
