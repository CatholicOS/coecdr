# COECDR Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Common Oecumenical Council Data Repository (COECDR) — a canonical, stable-ID registry of the 21 ecumenical councils recognized by the Catholic Church.

**Architecture:** `data/councils.json` is the hand-authored source of truth (21 entries). A Python generator (`scripts/generate_registry.py`) validates the data and renders the human-readable `registry/councils.md`, so the table can never silently drift. Documentation (README, schema proposal) explains the ID grammar and the recognition model.

**Tech Stack:** Python 3 standard library only (`json`, `unittest`, `pathlib`, `re`). No third-party dependencies. Data as JSON; documentation and registry as Markdown.

## Global Constraints

- **Repository:** `CatholicOS/coecdr`; curated by the Catholic Engineering Task Force (CETF). License Apache-2.0 (already in `LICENSE`).
- **ID grammar:** `oec:<place-slug>-<roman-ordinal>`, ordinal always present and lowercase (`i`, `ii`, …). Slug is lowercase ASCII, diacritics stripped, hyphen-separated.
- **`number`** is the council's position 1–21 in the Catholic sequence (distinct from the place-ordinal in the ID).
- **`rp:` cross-references** must be valid IDs from `../crpdr/data/pontiffs.json` (verified in Task 1, Step 1). Exact slugs used by this plan: `rp:sylvester-i`, `rp:damasus-i`, `rp:celestine-i`, `rp:leo-i`, `rp:vigilius-i`, `rp:agatho-i`, `rp:leo-ii`, `rp:adrian-i`, `rp:adrian-ii`, `rp:callixtus-ii`, `rp:innocent-ii`, `rp:alexander-iii`, `rp:innocent-iii`, `rp:innocent-iv`, `rp:gregory-x`, `rp:clement-v`, `rp:gregory-xii`, `rp:martin-v`, `rp:eugene-iv`, `rp:julius-ii`, `rp:leo-x`, `rp:paul-iii`, `rp:pius-iv`, `rp:pius-ix`, `rp:john-xxiii`, `rp:paul-vi`.
- **`recognized_as_ecumenical_by`** vocabulary is exactly `catholic`, `eastern_orthodox`, `oriental_orthodox`, `church_of_the_east`; every entry contains `catholic`; the array captures **formal conciliar reception only** (Protestant doctrinal esteem stays in prose).
- **Originality:** all prose (`significance`, notes) is authored in the registry's own words. No third-party table is captured or quoted; there is no `data/source/` directory.
- **Encoding:** files are UTF-8; date ranges use an en-dash (`–`) in `years_raw`.

## File Structure

- `data/councils.json` — source of truth, 21 council records + metadata. (Task 1)
- `scripts/test_councils_data.py` — structural/invariant tests over the data. (Task 1)
- `scripts/generate_registry.py` — validate + render `registry/councils.md`. (Task 2)
- `scripts/test_generate_registry.py` — tests for the generator's validation and rendering. (Task 2)
- `registry/councils.md` — generated table (build artifact, committed). (Task 2)
- `README.md` — what/why, ID scheme, contents, sources. (Task 3)
- `docs/schema-proposal.md` — full grammar, recognition model, open questions. (Task 3)

---

### Task 1: Author the council dataset

**Files:**
- Create: `data/councils.json`
- Test: `scripts/test_councils_data.py`

**Interfaces:**
- Produces: `data/councils.json` — top-level object `{ "$comment", "id_scheme", "sources", "council_count": 21, "entries": [ …21… ] }`. Each entry has keys: `number` (int), `id` (str), `name` (str), `label_en` (str), `aliases` (list[str]), `location` (str), `location_country` (str|null), `year_start` (int), `year_end` (int), `years_raw` (str), `century` (int), `reigning_pontiff` (str|null), `convened_by` (`{"text": str, "rp": str|null}`), `confirmed_by` (str|null), `recognized_as_ecumenical_by` (list[str]), `reception_note` (str|null), `significance` (str), `note` (str|null). Task 2 consumes this file.

- [ ] **Step 1: Verify every `rp:` slug exists in CRPDR**

Run:
```bash
cd /home/johnrdorazio/development/CatholicOS_org
python3 - <<'PY'
import json
ids={e['id'] for e in json.load(open('crpdr/data/pontiffs.json'))['entries']}
need=["rp:sylvester-i","rp:damasus-i","rp:celestine-i","rp:leo-i","rp:vigilius-i",
"rp:agatho-i","rp:leo-ii","rp:adrian-i","rp:adrian-ii","rp:callixtus-ii","rp:innocent-ii",
"rp:alexander-iii","rp:innocent-iii","rp:innocent-iv","rp:gregory-x","rp:clement-v",
"rp:gregory-xii","rp:martin-v","rp:eugene-iv","rp:julius-ii","rp:leo-x","rp:paul-iii",
"rp:pius-iv","rp:pius-ix","rp:john-xxiii","rp:paul-vi"]
missing=[x for x in need if x not in ids]
print("MISSING:", missing or "none")
PY
```
Expected: `MISSING: none`. If any are missing, stop and reconcile the slug against `crpdr/data/pontiffs.json` before writing the data.

- [ ] **Step 2: Write the failing data-invariant test**

Create `scripts/test_councils_data.py`:
```python
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
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `cd /home/johnrdorazio/development/CatholicOS_org/coecdr && python3 -m unittest scripts.test_councils_data -v`
Expected: FAIL — `FileNotFoundError` / `No such file` for `data/councils.json` (file not yet written).

- [ ] **Step 4: Author `data/councils.json`**

Create `data/councils.json` with exactly this content:
```json
{
  "$comment": "COECDR seed registry: draft canonical IDs for the 21 ecumenical councils recognized by the Catholic Church. Original compilation in the registry's own words; no third-party table is captured. All IDs and fields are drafts pending CETF review (docs/schema-proposal.md).",
  "id_scheme": "oec:<place-slug>-<roman-ordinal> (ordinal always present)",
  "sources": {
    "note": "Background reading only; none is treated as an authoritative table to snapshot. The list, dates, and prose are the registry's own compilation.",
    "references": [
      "https://en.wikipedia.org/wiki/Catholic_ecumenical_councils",
      "https://it.cathopedia.org/wiki/Concilio_Ecumenico",
      "https://www.newadvent.org/library/almanac_14388a.htm",
      "https://www.catholic.com/magazine/print-edition/the-21-ecumenical-councils"
    ]
  },
  "council_count": 21,
  "entries": [
    {
      "number": 1, "id": "oec:nicaea-i",
      "name": "First Council of Nicaea", "label_en": "First Council of Nicaea", "aliases": [],
      "location": "Nicaea", "location_country": "TR",
      "year_start": 325, "year_end": 325, "years_raw": "325", "century": 4,
      "reigning_pontiff": "rp:sylvester-i",
      "convened_by": { "text": "Emperor Constantine I", "rp": null },
      "confirmed_by": null,
      "recognized_as_ecumenical_by": ["catholic", "eastern_orthodox", "oriental_orthodox", "church_of_the_east"],
      "reception_note": null,
      "significance": "Defined the consubstantiality (homoousios) of the Son with the Father against Arianism, promulgated the original Nicene Creed, and set a common rule for the date of Easter.",
      "note": "Convoked by Constantine I; the Roman legates Vitus and Vincentius subscribed on behalf of Pope Sylvester I."
    },
    {
      "number": 2, "id": "oec:constantinople-i",
      "name": "First Council of Constantinople", "label_en": "First Council of Constantinople", "aliases": [],
      "location": "Constantinople", "location_country": "TR",
      "year_start": 381, "year_end": 381, "years_raw": "381", "century": 4,
      "reigning_pontiff": "rp:damasus-i",
      "convened_by": { "text": "Emperor Theodosius I", "rp": null },
      "confirmed_by": null,
      "recognized_as_ecumenical_by": ["catholic", "eastern_orthodox", "oriental_orthodox", "church_of_the_east"],
      "reception_note": null,
      "significance": "Affirmed the divinity of the Holy Spirit against the Pneumatomachi and completed the Niceno-Constantinopolitan Creed still professed in the liturgy.",
      "note": "Convened as an Eastern council of 150 bishops; the West was not represented, and its ecumenical rank was received in the Roman Church only later."
    },
    {
      "number": 3, "id": "oec:ephesus-i",
      "name": "Council of Ephesus", "label_en": "Council of Ephesus", "aliases": [],
      "location": "Ephesus", "location_country": "TR",
      "year_start": 431, "year_end": 431, "years_raw": "431", "century": 5,
      "reigning_pontiff": "rp:celestine-i",
      "convened_by": { "text": "Emperor Theodosius II", "rp": null },
      "confirmed_by": "rp:celestine-i",
      "recognized_as_ecumenical_by": ["catholic", "eastern_orthodox", "oriental_orthodox"],
      "reception_note": "The Assyrian Church of the East, which venerates Nestorius, Diodore of Tarsus, and Theodore of Mopsuestia, does not receive this council; the modern Catholic–Assyrian Common Christological Declaration (1994) affirms a shared faith in the one Christ notwithstanding the ancient breach over terminology.",
      "significance": "Condemned Nestorianism and affirmed that Mary is Theotokos, Mother of God, defending the unity of the one personal subject who is Christ, true God and true man. Presided over by Cyril of Alexandria as legate of Pope Celestine I.",
      "note": null
    },
    {
      "number": 4, "id": "oec:chalcedon-i",
      "name": "Council of Chalcedon", "label_en": "Council of Chalcedon", "aliases": [],
      "location": "Chalcedon", "location_country": "TR",
      "year_start": 451, "year_end": 451, "years_raw": "451", "century": 5,
      "reigning_pontiff": "rp:leo-i",
      "convened_by": { "text": "Emperor Marcian", "rp": null },
      "confirmed_by": "rp:leo-i",
      "recognized_as_ecumenical_by": ["catholic", "eastern_orthodox"],
      "reception_note": "The great Christological watershed. The Oriental Orthodox (miaphysite) churches do not receive Chalcedon, holding Cyril's formula of the 'one incarnate nature of the Word'; modern joint declarations (e.g. Coptic–Catholic 1973, Syriac–Catholic 1984) affirm that the two families confess the same mystery of the incarnate Christ in differing formulas.",
      "significance": "Defined that Christ is one person in two natures, divine and human, united without confusion, change, division, or separation (the Chalcedonian Definition), receiving Pope Leo I's Tome as its rule of faith.",
      "note": "Pope Leo I confirmed the doctrinal definition — his Tome was acclaimed, 'Peter has spoken through Leo' — but withheld approval of canon 28 on the precedence of the see of Constantinople."
    },
    {
      "number": 5, "id": "oec:constantinople-ii",
      "name": "Second Council of Constantinople", "label_en": "Second Council of Constantinople", "aliases": [],
      "location": "Constantinople", "location_country": "TR",
      "year_start": 553, "year_end": 553, "years_raw": "553", "century": 6,
      "reigning_pontiff": "rp:vigilius-i",
      "convened_by": { "text": "Emperor Justinian I", "rp": null },
      "confirmed_by": "rp:vigilius-i",
      "recognized_as_ecumenical_by": ["catholic", "eastern_orthodox"],
      "reception_note": null,
      "significance": "Condemned the 'Three Chapters' and reaffirmed Chalcedon interpreted in continuity with Cyril of Alexandria, seeking to reconcile the miaphysite East.",
      "note": "Pope Vigilius, present in Constantinople, at first resisted and only afterward assented to the council's decrees."
    },
    {
      "number": 6, "id": "oec:constantinople-iii",
      "name": "Third Council of Constantinople", "label_en": "Third Council of Constantinople", "aliases": [],
      "location": "Constantinople", "location_country": "TR",
      "year_start": 680, "year_end": 681, "years_raw": "680–681", "century": 7,
      "reigning_pontiff": "rp:agatho-i",
      "convened_by": { "text": "Emperor Constantine IV", "rp": null },
      "confirmed_by": "rp:leo-ii",
      "recognized_as_ecumenical_by": ["catholic", "eastern_orthodox"],
      "reception_note": null,
      "significance": "Condemned Monothelitism, defining that Christ has two wills and two natural operations, divine and human, in accordance with his two natures.",
      "note": "Opened under Pope Agatho, whose doctrinal letter guided it, and confirmed by his successor Leo II; the council anathematized Pope Honorius I for his role in the Monothelite controversy."
    },
    {
      "number": 7, "id": "oec:nicaea-ii",
      "name": "Second Council of Nicaea", "label_en": "Second Council of Nicaea", "aliases": [],
      "location": "Nicaea", "location_country": "TR",
      "year_start": 787, "year_end": 787, "years_raw": "787", "century": 8,
      "reigning_pontiff": "rp:adrian-i",
      "convened_by": { "text": "Empress Irene and Emperor Constantine VI", "rp": null },
      "confirmed_by": "rp:adrian-i",
      "recognized_as_ecumenical_by": ["catholic", "eastern_orthodox"],
      "reception_note": null,
      "significance": "Ended the first iconoclast crisis, restoring the veneration (dulia) of sacred images on the ground that the honor rendered passes to the prototype, while worship (latria) belongs to God alone.",
      "note": "The legates of Pope Hadrian I attended and the pope approved the council; it is the last of the seven councils shared with the Eastern Orthodox."
    },
    {
      "number": 8, "id": "oec:constantinople-iv",
      "name": "Fourth Council of Constantinople", "label_en": "Fourth Council of Constantinople", "aliases": [],
      "location": "Constantinople", "location_country": "TR",
      "year_start": 869, "year_end": 870, "years_raw": "869–870", "century": 9,
      "reigning_pontiff": "rp:adrian-ii",
      "convened_by": { "text": "Emperor Basil I", "rp": null },
      "confirmed_by": "rp:adrian-ii",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Deposed Photius and restored Ignatius as patriarch of Constantinople, condemning the residue of iconoclasm; the Catholic Church counts it as the eighth ecumenical council.",
      "note": "Here the Catholic and Eastern Orthodox reckonings diverge: much of the Orthodox tradition instead numbers as eighth the Constantinople synod of 879–880, which reinstated Photius. COECDR follows the Catholic sequence."
    },
    {
      "number": 9, "id": "oec:lateran-i",
      "name": "First Lateran Council", "label_en": "First Lateran Council", "aliases": [],
      "location": "Rome", "location_country": "IT",
      "year_start": 1123, "year_end": 1123, "years_raw": "1123", "century": 12,
      "reigning_pontiff": "rp:callixtus-ii",
      "convened_by": { "text": "Pope Callixtus II", "rp": "rp:callixtus-ii" },
      "confirmed_by": "rp:callixtus-ii",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Ratified the Concordat of Worms, ending the Investiture Controversy by distinguishing the spiritual investiture of bishops from their temporal regalia; the first ecumenical council held in the West.",
      "note": "Held at the Lateran Basilica (Saint John Lateran) in Rome."
    },
    {
      "number": 10, "id": "oec:lateran-ii",
      "name": "Second Lateran Council", "label_en": "Second Lateran Council", "aliases": [],
      "location": "Rome", "location_country": "IT",
      "year_start": 1139, "year_end": 1139, "years_raw": "1139", "century": 12,
      "reigning_pontiff": "rp:innocent-ii",
      "convened_by": { "text": "Pope Innocent II", "rp": "rp:innocent-ii" },
      "confirmed_by": "rp:innocent-ii",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Healed the schism of the antipope Anacletus II and enacted disciplinary canons, including the invalidity of marriages attempted by those in major orders (clerical celibacy).",
      "note": "Held at the Lateran Basilica (Saint John Lateran) in Rome."
    },
    {
      "number": 11, "id": "oec:lateran-iii",
      "name": "Third Lateran Council", "label_en": "Third Lateran Council", "aliases": [],
      "location": "Rome", "location_country": "IT",
      "year_start": 1179, "year_end": 1179, "years_raw": "1179", "century": 12,
      "reigning_pontiff": "rp:alexander-iii",
      "convened_by": { "text": "Pope Alexander III", "rp": "rp:alexander-iii" },
      "confirmed_by": "rp:alexander-iii",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Restricted papal elections to the cardinals and required a two-thirds majority (the rule still in force), and moved against the Cathars and Waldensians.",
      "note": "Held at the Lateran Basilica (Saint John Lateran) in Rome."
    },
    {
      "number": 12, "id": "oec:lateran-iv",
      "name": "Fourth Lateran Council", "label_en": "Fourth Lateran Council", "aliases": [],
      "location": "Rome", "location_country": "IT",
      "year_start": 1215, "year_end": 1215, "years_raw": "1215", "century": 13,
      "reigning_pontiff": "rp:innocent-iii",
      "convened_by": { "text": "Pope Innocent III", "rp": "rp:innocent-iii" },
      "confirmed_by": "rp:innocent-iii",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "The great reforming council of the medieval papacy: used the term transubstantiation, required annual confession and Easter communion of the faithful, and legislated broadly on faith and discipline.",
      "note": "Held at the Lateran Basilica (Saint John Lateran) in Rome; convoked by Innocent III at the height of the medieval papacy."
    },
    {
      "number": 13, "id": "oec:lyon-i",
      "name": "First Council of Lyon", "label_en": "First Council of Lyon", "aliases": [],
      "location": "Lyon", "location_country": "FR",
      "year_start": 1245, "year_end": 1245, "years_raw": "1245", "century": 13,
      "reigning_pontiff": "rp:innocent-iv",
      "convened_by": { "text": "Pope Innocent IV", "rp": "rp:innocent-iv" },
      "confirmed_by": "rp:innocent-iv",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Deposed the Emperor Frederick II and took measures for the defense of the Holy Land and the reform of church discipline.",
      "note": null
    },
    {
      "number": 14, "id": "oec:lyon-ii",
      "name": "Second Council of Lyon", "label_en": "Second Council of Lyon", "aliases": [],
      "location": "Lyon", "location_country": "FR",
      "year_start": 1274, "year_end": 1274, "years_raw": "1274", "century": 13,
      "reigning_pontiff": "rp:gregory-x",
      "convened_by": { "text": "Pope Gregory X", "rp": "rp:gregory-x" },
      "confirmed_by": "rp:gregory-x",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Achieved a short-lived reunion with the Greek Church, professed the procession of the Holy Spirit, and enacted the conclave rules for papal elections (Ubi periculum).",
      "note": null
    },
    {
      "number": 15, "id": "oec:vienne-i",
      "name": "Council of Vienne", "label_en": "Council of Vienne", "aliases": [],
      "location": "Vienne", "location_country": "FR",
      "year_start": 1311, "year_end": 1312, "years_raw": "1311–1312", "century": 14,
      "reigning_pontiff": "rp:clement-v",
      "convened_by": { "text": "Pope Clement V", "rp": "rp:clement-v" },
      "confirmed_by": "rp:clement-v",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Suppressed the Knights Templar and condemned errors attributed to the Beguines, Beghards, and the Free Spirit.",
      "note": null
    },
    {
      "number": 16, "id": "oec:constance-i",
      "name": "Council of Constance", "label_en": "Council of Constance", "aliases": [],
      "location": "Constance", "location_country": "DE",
      "year_start": 1414, "year_end": 1418, "years_raw": "1414–1418", "century": 15,
      "reigning_pontiff": "rp:gregory-xii",
      "convened_by": { "text": "Antipope John XXIII, at the urging of Emperor Sigismund; convalidated by Pope Gregory XII", "rp": "rp:gregory-xii" },
      "confirmed_by": "rp:martin-v",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Ended the Western Schism of three rival claimants and elected Pope Martin V, and condemned the errors of Wyclif and Hus.",
      "note": "Its ecumenical authority attaches to the sessions from Pope Gregory XII's convalidation onward and to the acts confirmed by Martin V; the conciliarist decree Haec Sancta is not received as of ecumenical authority."
    },
    {
      "number": 17, "id": "oec:florence-i",
      "name": "Council of Florence", "label_en": "Council of Florence",
      "aliases": ["Council of Basel–Ferrara–Florence"],
      "location": "Florence", "location_country": "IT",
      "year_start": 1431, "year_end": 1445, "years_raw": "1431–1445", "century": 15,
      "reigning_pontiff": "rp:eugene-iv",
      "convened_by": { "text": "Convoked at Basel by Pope Martin V (1431); transferred to Ferrara (1438) and Florence (1439) by Pope Eugene IV", "rp": "rp:martin-v" },
      "confirmed_by": "rp:eugene-iv",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Proclaimed reunion with the Greek Church (Laetentur Caeli, 1439) on the Filioque, purgatory, and papal primacy, and further unions with the Armenians, Copts, and others; most proved short-lived.",
      "note": "Ecumenical status attaches to the papally-recognized assembly that Eugene IV transferred to Ferrara and Florence; the rump Council of Basel that continued in defiance (electing the antipope Felix V) is not received as ecumenical. Sat successively at Basel (Switzerland) and Ferrara (Italy) before Florence, which gives it its conventional name."
    },
    {
      "number": 18, "id": "oec:lateran-v",
      "name": "Fifth Lateran Council", "label_en": "Fifth Lateran Council", "aliases": [],
      "location": "Rome", "location_country": "IT",
      "year_start": 1512, "year_end": 1517, "years_raw": "1512–1517", "century": 16,
      "reigning_pontiff": "rp:julius-ii",
      "convened_by": { "text": "Pope Julius II", "rp": "rp:julius-ii" },
      "confirmed_by": "rp:leo-x",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Reaffirmed papal authority over councils against conciliarism, condemned errors denying the immortality of the individual soul, and called for reforms that went largely unrealized on the eve of the Reformation.",
      "note": "Held at the Lateran Basilica (Saint John Lateran) in Rome; opened under Julius II, partly to counter the schismatic conciliabulum of Pisa, and concluded and confirmed under Leo X."
    },
    {
      "number": 19, "id": "oec:trent-i",
      "name": "Council of Trent", "label_en": "Council of Trent", "aliases": [],
      "location": "Trent", "location_country": "IT",
      "year_start": 1545, "year_end": 1563, "years_raw": "1545–1563", "century": 16,
      "reigning_pontiff": "rp:paul-iii",
      "convened_by": { "text": "Pope Paul III", "rp": "rp:paul-iii" },
      "confirmed_by": "rp:pius-iv",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Responded to the Protestant Reformation, defining Scripture and Tradition, original sin and justification, and the seven sacraments, and enacting sweeping disciplinary reform.",
      "note": "Convened in three periods (1545–1547, 1551–1552, 1562–1563) under Paul III, Julius III, and Pius IV; its decrees were confirmed by Pius IV in 1564."
    },
    {
      "number": 20, "id": "oec:vatican-i",
      "name": "First Vatican Council", "label_en": "First Vatican Council", "aliases": [],
      "location": "Vatican", "location_country": "VA",
      "year_start": 1869, "year_end": 1870, "years_raw": "1869–1870", "century": 19,
      "reigning_pontiff": "rp:pius-ix",
      "convened_by": { "text": "Pope Pius IX", "rp": "rp:pius-ix" },
      "confirmed_by": "rp:pius-ix",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "Defined the primacy and infallibility of the Roman Pontiff (Pastor Aeternus) and taught the harmony of faith and reason (Dei Filius).",
      "note": "Held at Saint Peter's Basilica; suspended in 1870 when Italian troops entered Rome and never formally reconvened."
    },
    {
      "number": 21, "id": "oec:vatican-ii",
      "name": "Second Vatican Council", "label_en": "Second Vatican Council", "aliases": [],
      "location": "Vatican", "location_country": "VA",
      "year_start": 1962, "year_end": 1965, "years_raw": "1962–1965", "century": 20,
      "reigning_pontiff": "rp:john-xxiii",
      "convened_by": { "text": "Pope John XXIII", "rp": "rp:john-xxiii" },
      "confirmed_by": "rp:paul-vi",
      "recognized_as_ecumenical_by": ["catholic"],
      "reception_note": null,
      "significance": "A pastoral council of renewal, issuing the constitutions on the liturgy (Sacrosanctum Concilium), the Church (Lumen Gentium), divine revelation (Dei Verbum), and the Church in the modern world (Gaudium et Spes), and teaching on ecumenism and religious liberty.",
      "note": "Held at Saint Peter's Basilica; convoked and opened by John XXIII in 1962 and concluded under Paul VI in 1965. It defined no new dogmas, exercising a pastoral magisterium."
    }
  ]
}
```

- [ ] **Step 5: Run the data test to verify it passes**

Run: `cd /home/johnrdorazio/development/CatholicOS_org/coecdr && python3 -m unittest scripts.test_councils_data -v`
Expected: PASS (all tests, including the CRPDR cross-reference existence check).

- [ ] **Step 6: Commit**

```bash
cd /home/johnrdorazio/development/CatholicOS_org/coecdr
git add data/councils.json scripts/test_councils_data.py
git commit -m "COECDR: seed dataset of the 21 ecumenical councils + invariant tests"
```

---

### Task 2: Registry generator and rendered table

**Files:**
- Create: `scripts/generate_registry.py`
- Create: `scripts/test_generate_registry.py`
- Create (build artifact): `registry/councils.md`

**Interfaces:**
- Consumes: `data/councils.json` (schema from Task 1).
- Produces: `scripts/generate_registry.py` exposing `load_data() -> dict`, `validate(doc) -> None` (raises `ValueError` on any violation), `render(doc) -> str` (returns the full Markdown document), and `main() -> None` (loads, validates, writes `registry/councils.md`). Running `python3 scripts/generate_registry.py` regenerates the table.

- [ ] **Step 1: Write the failing generator test**

Create `scripts/test_generate_registry.py`:
```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /home/johnrdorazio/development/CatholicOS_org/coecdr/scripts && python3 -m unittest test_generate_registry -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'generate_registry'`.

- [ ] **Step 3: Write `scripts/generate_registry.py`**

Create `scripts/generate_registry.py`:
```python
#!/usr/bin/env python3
"""Validate data/councils.json and render registry/councils.md.

The JSON is the source of truth; this script is the only writer of the
Markdown table, so the two can never silently drift. Run:

    python3 scripts/generate_registry.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "councils.json"
OUT = ROOT / "registry" / "councils.md"

ID_RE = re.compile(r"^oec:[a-z]+(?:-[a-z]+)*-[ivx]+$")
RP_RE = re.compile(r"^rp:[a-z]+(?:-[a-z]+)*-[ivx]+$|^rp:peter$")
COMMUNIONS = ["catholic", "eastern_orthodox", "oriental_orthodox", "church_of_the_east"]
CODE = {"catholic": "C", "eastern_orthodox": "EO",
        "oriental_orthodox": "OO", "church_of_the_east": "CE"}


def load_data():
    return json.loads(DATA.read_text(encoding="utf-8"))


def validate(doc):
    entries = doc.get("entries", [])
    if doc.get("council_count") != 21 or len(entries) != 21:
        raise ValueError("expected exactly 21 councils")
    if [e["number"] for e in entries] != list(range(1, 22)):
        raise ValueError("numbers must be contiguous 1..21 in order")
    seen = set()
    for e in entries:
        cid = e["id"]
        if not ID_RE.match(cid):
            raise ValueError(f"malformed id: {cid}")
        if cid in seen:
            raise ValueError(f"duplicate id: {cid}")
        seen.add(cid)
        rec = e["recognized_as_ecumenical_by"]
        if not rec:
            raise ValueError(f"{cid}: empty recognized_as_ecumenical_by")
        if "catholic" not in rec:
            raise ValueError(f"{cid}: must include 'catholic'")
        if any(c not in COMMUNIONS for c in rec):
            raise ValueError(f"{cid}: recognition outside vocabulary: {rec}")
        for ref in (e["reigning_pontiff"], e["convened_by"]["rp"], e["confirmed_by"]):
            if ref is not None and not RP_RE.match(ref):
                raise ValueError(f"{cid}: malformed rp cross-reference: {ref}")
        if e["year_start"] > e["year_end"]:
            raise ValueError(f"{cid}: year_start after year_end")
        if not e["significance"].strip():
            raise ValueError(f"{cid}: empty significance")


def _cell(value):
    """Escape a value for a Markdown table cell."""
    if value is None:
        return ""
    return str(value).replace("|", "\\|")


def _rp(ref):
    return f"`{ref}`" if ref else ""


def render(doc):
    entries = doc["entries"]
    lines = []
    lines.append("# Ecumenical Councils")
    lines.append("")
    lines.append(
        "Canonical draft IDs for the 21 ecumenical councils recognized by the "
        "Catholic Church, from the First Council of Nicaea (325) to the Second "
        "Vatican Council (1962–1965), in sequence order. `#` is the council's "
        "position in the Catholic sequence; the ID carries the place-ordinal "
        "(which Nicaea, which Lateran). The **Recognized** column records "
        "*formal* conciliar reception only — **C** = Catholic, **EO** = Eastern "
        "Orthodox, **OO** = Oriental Orthodox, **CE** = Church of the East. The "
        "first seven are the corpus shared with the Eastern Orthodox; the first "
        "three are shared also with the Oriental Orthodox, the first two with the "
        "Church of the East. Doctrinal esteem beyond formal reception (e.g. the "
        "authority of the first four across much of historic Protestantism) is "
        "discussed in the schema proposal, not encoded here. Popes are given as "
        "[CRPDR](../../crpdr) `rp:` IDs. All IDs are drafts pending CETF review "
        "([schema proposal](../docs/schema-proposal.md))."
    )
    lines.append("")
    header = ["#", "ID", "Council", "Years", "Place", "Country",
              "Reigning pontiff", "Convened by", "Confirmed by",
              "Recognized", "Significance"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for e in entries:
        codes = " ".join(CODE[c] for c in COMMUNIONS if c in e["recognized_as_ecumenical_by"])
        row = [
            str(e["number"]),
            f"`{e['id']}`",
            _cell(e["name"]),
            _cell(e["years_raw"]),
            _cell(e["location"]),
            _cell(e["location_country"]),
            _rp(e["reigning_pontiff"]),
            _cell(e["convened_by"]["text"]),
            _rp(e["confirmed_by"]),
            codes,
            _cell(e["significance"]),
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return "\n".join(lines)


def main():
    doc = load_data()
    validate(doc)
    OUT.write_text(render(doc), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(doc['entries'])} councils)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the generator test to verify it passes**

Run: `cd /home/johnrdorazio/development/CatholicOS_org/coecdr/scripts && python3 -m unittest test_generate_registry -v`
Expected: PASS (all six tests).

- [ ] **Step 5: Generate the registry table**

Run: `cd /home/johnrdorazio/development/CatholicOS_org/coecdr && python3 scripts/generate_registry.py`
Expected: prints `wrote registry/councils.md (21 councils)`. Open `registry/councils.md` and confirm 21 data rows, the legend, and that Lateran rows show `IT` while Vatican rows show `VA`.

- [ ] **Step 6: Run the full test suite**

Run: `cd /home/johnrdorazio/development/CatholicOS_org/coecdr && python3 -m unittest discover -s scripts -v`
Expected: PASS — both `test_councils_data` and `test_generate_registry`.

- [ ] **Step 7: Commit**

```bash
cd /home/johnrdorazio/development/CatholicOS_org/coecdr
git add scripts/generate_registry.py scripts/test_generate_registry.py registry/councils.md
git commit -m "COECDR: registry generator, tests, and rendered councils.md"
```

---

### Task 3: Documentation (README + schema proposal)

**Files:**
- Create: `README.md`
- Create: `docs/schema-proposal.md`

**Interfaces:**
- Consumes: the ID scheme and recognition model from `docs/superpowers/specs/2026-07-31-coecdr-design.md`; the generated `registry/councils.md`.
- Produces: human-facing documentation. No code depends on these.

- [ ] **Step 1: Write `README.md`**

Create `README.md`:
```markdown
# COECDR

The home of the **Common Oecumenical Council Data Repository**, curated by the
**Catholic Engineering Task Force** of the
[Catholic Digital Commons Foundation](https://github.com/CatholicOS).

## What is COECDR?

The Common Oecumenical Council Data Repository (COECDR) provides a canonicalized
list of identifiers for the **twenty-one ecumenical councils** recognized by the
Catholic Church, from the First Council of Nicaea (325) to the Second Vatican
Council (1962–1965).

Ecumenical councils carry a doctrinal weight and universality that local councils
and particular synods do not; this registry is dedicated to them specifically and
does not attempt to catalogue local or particular councils.

## Why?

Canonical council identifiers are needed wherever Catholic data must reference a
council unambiguously: doctrinal and magisterial attribution (a canon, decree, or
definition is cited by its council), church-history datasets, catechetical and
reference works, and cross-references from sibling registries — for instance the
Roman Pontiffs ([CRPDR](https://github.com/CatholicOS/crpdr)) who convened or
confirmed a council.

## The identifier scheme (draft)

```
oec:<place-slug>-<roman-ordinal>     e.g. oec:nicaea-i, oec:trent-i, oec:vatican-ii
```

Every identifier carries a Roman-numeral ordinal counting the assemblies held at
that place — `oec:nicaea-i` and `oec:nicaea-ii`, `oec:lateran-i` … `oec:lateran-v`
— *including* councils held there only once (`oec:trent-i`, `oec:chalcedon-i`), so
that an ID never has to shift if a place is ever used again. The `oec:` prefix
abbreviates *Oecumenical* and is deliberately distinct from the `ec:` that could
be read against the Ecclesiastical Circumscription registry. The full grammar and
the open questions are in [docs/schema-proposal.md](docs/schema-proposal.md).
**All IDs are drafts pending committee review.**

## Recognition across the churches

Recognition is not a simple binary, and the registry does not model it as one. The
per-council field `recognized_as_ecumenical_by` records **formal conciliar
reception** by the apostolic communions that hold a doctrine of ecumenical
councils: the Catholic Church (all twenty-one), the Eastern Orthodox (the first
seven), the Oriental Orthodox (the first three), and the Assyrian Church of the
East (the first two). Doctrinal esteem beyond formal reception — notably the
authority of the first four councils across much of historic Protestantism — is
described in prose, never entered into that array. See
[docs/schema-proposal.md](docs/schema-proposal.md) for the full account.

## Repository contents

- [`data/councils.json`](data/councils.json) — the seed registry: 21 council
  records, each with its draft canonical ID, name and aliases, place with the ISO
  3166-1 alpha-2 code of its modern country, dates, the reigning / convening /
  confirming Roman Pontiffs as [CRPDR](https://github.com/CatholicOS/crpdr) `rp:`
  cross-references, its formal-recognition set, and a short original summary.
- [`registry/councils.md`](registry/councils.md) — the same registry as a
  human-readable table, one row per council in sequence order.
- [`docs/schema-proposal.md`](docs/schema-proposal.md) — the proposed schema, the
  recognition model, and the open questions for the committee.
- [`scripts/generate_registry.py`](scripts/generate_registry.py) — regenerates
  the table (`python3 scripts/generate_registry.py`); tests:
  `python3 -m unittest discover -s scripts`.

## Sources

COECDR is an original compilation. The list of councils, their dates, and their
doctrinal significance are matters of public record and Catholic doctrine; the
registry authors its own table and prose from general knowledge and takes no
third-party tabulation as an authoritative source to capture. The registry
follows the Catholic reckoning and takes no position on disputed historical
questions beyond presenting that sequence.
```

- [ ] **Step 2: Write `docs/schema-proposal.md`**

Create `docs/schema-proposal.md`:
```markdown
# COECDR Schema Proposal

**Status:** Draft, pending CETF review.
**Registry:** Common Oecumenical Council Data Repository (`CatholicOS/coecdr`).

## 1. Identifier grammar

```abnf
council-id   = "oec:" place "-" ordinal
place        = lowercase *( lowercase / "-" ) lowercase
ordinal      = 1*( "i" / "v" / "x" )        ; lowercase Roman numeral
lowercase    = %x61-7A                        ; a-z
```

Examples: `oec:nicaea-i`, `oec:constantinople-iv`, `oec:lateran-v`, `oec:trent-i`,
`oec:vatican-ii`.

### 1.1 Rules

1. **Place-name slugs, in English**, lowercased, diacritics stripped, spaces
   hyphenated. The slug uses the council's conventional place-designation — for
   the Roman councils this is the basilica name (`lateran`, `vatican`), while the
   record's `location` field carries the civil city (Rome, Vatican).
2. **The `oec:` prefix** abbreviates *Oecumenical*, the classical spelling kept in
   the councils' historic titles; it is deliberately distinct from `ec:`.
3. **Ordinal always present**, counting assemblies at the same place in the
   Catholic sequence, so IDs are stable even for places used only once.
4. **Peripatetic councils** take their conventional place-name: the seventeenth is
   `oec:florence-i` (a.k.a. Council of Basel–Ferrara–Florence).

## 2. Data fields

Each entry in `data/councils.json`:

| field | type | meaning |
| --- | --- | --- |
| `number` | int 1–21 | position in the Catholic sequence |
| `id` | string | the `oec:` canonical identifier |
| `name`, `label_en` | string | common English name / display label |
| `aliases` | list[string] | alternative names |
| `location` | string | civil place of assembly |
| `location_country` | string \| null | ISO 3166-1 alpha-2 of the modern country |
| `year_start`, `year_end` | int | first / last year |
| `years_raw` | string | display date span |
| `century` | int | century of the council |
| `reigning_pontiff` | string \| null | `rp:` cross-reference to the pope at convocation |
| `convened_by` | object | `{ "text": string, "rp": string\|null }` — who summoned it |
| `confirmed_by` | string \| null | `rp:` cross-reference to the confirming pope |
| `recognized_as_ecumenical_by` | list[string] | formal-reception set (see §3) |
| `reception_note` | string \| null | prose on recognition nuance |
| `significance` | string | brief original summary of the council's import |
| `note` | string \| null | disambiguation / context |

For councils spanning several pontificates, `reigning_pontiff` names the pope at
convocation and `note` records the succession. For the first eight councils
`convened_by.rp` is null, because a Roman emperor summoned them.

## 3. Recognition model

`recognized_as_ecumenical_by` records **formal conciliar reception** — a communion
receiving the council *as* an ecumenical council — over a controlled vocabulary of
the four apostolic communions that hold such a doctrine:

| key | formally receives |
| --- | --- |
| `catholic` | all twenty-one (Latin and Eastern Catholic churches) |
| `eastern_orthodox` | the first seven |
| `oriental_orthodox` | the first three |
| `church_of_the_east` | the first two |

The dividing lines are doctrinal: the Church of the East parts at Ephesus (431),
which condemned Nestorius; the Oriental Orthodox at Chalcedon (451), the
Christological watershed; the Eastern Orthodox at the eighth council, where the
Catholic and Orthodox numberings also diverge (the Orthodox reckon the
Constantinople synod of 879–880 in its place).

### 3.1 The "common cores"

Several overlapping cores are commonly invoked; they are documented here rather
than encoded as booleans, because their meanings differ:

- **First two** (Nicaea I, Constantinople I) — the broad early Trinitarian core,
  shared as far as the Church of the East.
- **First three** (add Ephesus) — the common inheritance of the Catholic, Eastern
  Orthodox, and Oriental Orthodox churches.
- **First four** (add Chalcedon) — the classical Chalcedonian framework of
  Trinitarian and Christological doctrine; foundational and highly authoritative
  across much of historic Protestantism (Lutheran, Reformed, Anglican, Methodist),
  *with differing theories of conciliar authority*. This is doctrinal esteem, not
  a claim of universal Eastern reception — the Oriental Orthodox do not receive
  Chalcedon.
- **First seven** — the complete common ecumenical-council corpus of the Catholic
  and Eastern Orthodox churches.

Formal acceptance of a council, acceptance of its doctrinal content, agreement
that its condemnations were justified, and full ecclesial communion are related
but distinct; `recognized_as_ecumenical_by` speaks only to the first.

## 4. Open questions

1. **`cdcf:` cross-reference.** Whether to add a `cdcf:council/…` field once the
   cdcf-uri-scheme defines a council namespace (cf. CRPDR's `cdcf_person`).
2. **Conciliar documents / canons.** Whether to add a `documents` array
   enumerating a council's constitutions, decrees, or canons.
3. **Further communions.** Whether to represent non-formal positions (e.g.
   Anglican, Old Catholic) in structured data or keep them in prose.

All IDs and fields are **drafts pending CETF review.**
```

- [ ] **Step 3: Sanity-check the docs**

Run: `cd /home/johnrdorazio/development/CatholicOS_org/coecdr && ls README.md docs/schema-proposal.md && python3 -m unittest discover -s scripts`
Expected: both files listed; tests still PASS (docs don't affect them).

- [ ] **Step 4: Commit**

```bash
cd /home/johnrdorazio/development/CatholicOS_org/coecdr
git add README.md docs/schema-proposal.md
git commit -m "COECDR: README and schema proposal"
```

---

## Self-Review

**Spec coverage:**
- §1 Purpose / originality / reckoning → README "What/Why/Sources", schema §3, data `$comment` + `sources`. ✓
- §1.2 recognition model + common cores → Task 1 data (`recognized_as_ecumenical_by`, matrix test), schema §3/§3.1, README. ✓
- §2 ID scheme (grammar, always-mint ordinal, `oec:` rationale, peripatetic) → schema §1, README, `test_councils_data` ID regex. ✓
- §3 data model (all fields incl. `convened_by` object, `reception_note`) → Task 1 entries + schema §2. ✓
- §3.2 the 21 councils with correct IDs, years, countries (Lateran IT / Vatican VA) → Task 1 data + Task 2 render check (Step 5). ✓
- §4 repo layout (data / registry / docs / scripts, JSON-source + render script + test) → all three tasks. ✓
- §5 open questions → schema §4. ✓

**Placeholder scan:** No TBD/TODO; every code and data block is complete and literal. ✓

**Type consistency:** `validate`, `render`, `load_data`, `main` names match between `generate_registry.py` and `test_generate_registry.py`; field names (`recognized_as_ecumenical_by`, `convened_by.rp`, `confirmed_by`, `years_raw`) are identical across data, tests, generator, and schema doc. The `rp:` regex in both test files and the generator accepts `rp:peter` (no ordinal) as well as the ordinal form. ✓
