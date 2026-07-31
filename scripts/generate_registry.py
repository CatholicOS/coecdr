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
    required = ("number", "id", "recognized_as_ecumenical_by", "reigning_pontiff",
                "convened_by", "confirmed_by", "year_start", "year_end", "century",
                "significance")
    for e in entries:
        missing = [k for k in required if k not in e]
        if missing:
            label = e.get("id", f"entry #{e.get('number', '?')}")
            raise ValueError(f"{label}: missing required key(s) {missing}")
        if not isinstance(e["convened_by"], dict) or "rp" not in e["convened_by"]:
            raise ValueError(f"{e['id']}: convened_by must be an object containing 'rp'")
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
        if e["century"] != (e["year_start"] - 1) // 100 + 1:
            raise ValueError(f"{cid}: century inconsistent with year_start")
        if not isinstance(e["significance"], str) or not e["significance"].strip():
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
