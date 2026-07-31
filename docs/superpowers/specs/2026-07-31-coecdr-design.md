# COECDR — Common Oecumenical Council Data Repository: Design

**Date:** 2026-07-31
**Status:** Approved design, pending implementation
**Repository:** `CatholicOS/coecdr`
**Curation:** Catholic Engineering Task Force (CETF) of the Catholic Digital Commons Foundation (CDCF)
**License:** Apache-2.0

## 1. Purpose

COECDR provides canonical, stable identifiers for the **twenty-one ecumenical
councils** recognized by the Catholic Church, from the First Council of Nicaea
(325) to the Second Vatican Council (1962–1965), for use wherever Catholic data
must reference a council unambiguously: magisterial and doctrinal attribution
(a canon, decree, or definition is cited by its council), church-history
datasets, catechetical and reference works, and cross-references from sibling
registries (e.g. Roman Pontiffs who convened or confirmed a council).

Ecumenical councils carry a doctrinal weight and universality that local
councils and particular synods do not; the registry is dedicated to them
specifically, and does not attempt to catalogue local or particular councils.

### 1.1 Sourcing and originality

Unlike [CRPDR](https://github.com/CatholicOS/crpdr), which seeds from the Holy
See's own reference table, COECDR has **no single authoritative table to
snapshot**. The list of ecumenical councils, their dates, and their doctrinal
import are matters of public record and Catholic doctrine, but the convenient
tabulations available online (e.g. newadvent.org, catholic.com, Wikipedia,
cathopedia.org) are not authoritative sources on par with the Holy See's site.

Accordingly, COECDR is an **original compilation**: the list, dates, places,
pontiff cross-references, and the prose `significance` summaries are authored by
the registry in its own words from general knowledge, using such references only
as background reading. No third-party table is captured or quoted verbatim, and
there is no `data/source/` snapshot. (This also means there is no copyright
constraint of the kind that governs the martyrology texts.)

### 1.2 Reckoning and recognition

The registry follows the **Catholic reckoning** of twenty-one councils. The
numbering diverges from the Eastern Orthodox reckoning at the eighth: the
Catholic sequence counts the Council of Constantinople of 869–870, whereas much
of the Eastern Orthodox tradition instead reckons the Constantinople synod of
879–880; this divergence is noted on the affected record rather than resolved by
the registry. COECDR takes no position on disputed historical or ecclesiological
questions beyond presenting the Catholic sequence.

Recognition of these councils across the apostolic Christian communions is not a
simple binary, and the registry does not model it as one. It distinguishes
**formal conciliar reception** (a communion receives the council *as* an
ecumenical council) from the broader **doctrinal reception or esteem** a
council's teaching may enjoy elsewhere. Formal reception is captured per record
in `recognized_as_ecumenical_by` (§3), over a controlled vocabulary of the four
apostolic communions that hold a doctrine of ecumenical councils:

| communion key | formally receives |
| --- | --- |
| `catholic` | all twenty-one (Latin and the Eastern Catholic churches in communion with Rome) |
| `eastern_orthodox` | the first seven |
| `oriental_orthodox` | the first three (they reject Chalcedon and later) |
| `church_of_the_east` | the first two (it venerates figures the Council of Ephesus condemned) |

The dividing lines are doctrinal, not merely chronological: the Church of the
East parts at Ephesus (431), the Oriental Orthodox at Chalcedon (451) — the great
Christological watershed — and the Eastern Orthodox at the eighth council. All
seven of the common Catholic–Eastern-Orthodox councils predate the conventional
East–West rupture; being pre-schism does *not* distinguish the first four from
the first seven.

#### 1.2.1 The "common cores" (documented, not naively derived)

Several overlapping "common cores" are commonly invoked; the registry documents
them in prose (README and `docs/schema-proposal.md`) rather than asserting them
as booleans, because their meaning differs:

- **First two** (Nicaea I, Constantinople I) — the broad early Trinitarian core,
  shared as far as the Church of the East.
- **First three** (add Ephesus) — the common conciliar inheritance of the
  Catholic, Eastern Orthodox, *and* Oriental Orthodox churches.
- **First four** (add Chalcedon) — the classical Chalcedonian framework of
  Trinitarian and Christological doctrine. It is foundational and doctrinally
  authoritative across much of historic Protestantism (Lutheran, Reformed,
  Anglican, Methodist) — *with differing theories of conciliar authority*. This
  is a statement of doctrinal esteem, **not** a claim of universal Eastern
  reception: the Oriental Orthodox do not formally receive Chalcedon.
- **First seven** — the complete common ecumenical-council corpus formally shared
  by the Catholic and Eastern Orthodox churches.

Protestant reception is therefore recorded only in prose (it is doctrinal esteem,
not the formal conciliar reception the `recognized_as_ecumenical_by` vocabulary
denotes), and is never entered into that array.

## 2. Identifier scheme

```
oec:<place-slug>-<roman-ordinal>        (all councils)
```

Examples: `oec:nicaea-i`, `oec:nicaea-ii`, `oec:constantinople-iv`,
`oec:lateran-v`, `oec:trent-i`, `oec:vatican-ii`.

### 2.1 Rules

1. **Place-name slugs, in English.** The identifier is built on the council's
   place of assembly, lowercased, diacritics stripped, spaces replaced by
   hyphens. English is the de-facto language of worldwide technology standards.
   Latin or vernacular labels (e.g. *Concilium Tridentinum*) belong in the data
   as attributes, not in the ID.
2. **The `oec:` prefix.** The prefix abbreviates *Oecumenical* (the classical
   spelling preserved in the councils' own historic titles and in the repository
   name). It is deliberately distinct from `ec:`, which could be read against the
   *Ecclesiastical Circumscription* registry (CECDR); the `oec:` prefix scopes
   the namespace unambiguously to ecumenical councils.
3. **Ordinal always present.** Every identifier carries a lowercase Roman-numeral
   ordinal, *including* councils held only once at a given place (`oec:trent-i`,
   `oec:chalcedon-i`, `oec:ephesus-i`, `oec:vienne-i`). Canonical IDs must be
   stable over time: were a future council ever held again at the same place, the
   existing ID must not shift to make room for it. Minting a bare slug and adding
   an ordinal later would break stability; minting the ordinal from day one costs
   nothing. This mirrors CRPDR's immutable-ordinal principle.
4. **Ordinals count assemblies at the same place, in the Catholic sequence.**
   Nicaea → `oec:nicaea-i`, `oec:nicaea-ii`; Constantinople → `-i` … `-iv`;
   Lateran → `-i` … `-v`; Lyon → `-i`, `-ii`; Vatican → `-i`, `-ii`. The ordinal
   is the place-ordinal (which Nicaea, which Lateran), not the council's overall
   position 1–21; the overall position is carried separately as `number`.
5. **Peripatetic councils take their conventional place-name.** The seventeenth
   council, which sat successively at Basel, Ferrara, and Florence, is
   canonically the *Council of Florence*: `oec:florence-i`, with
   "Council of Basel–Ferrara–Florence" recorded as an alias.

### 2.2 Grammar (ABNF, per RFC 5234)

```abnf
council-id   = "oec:" place "-" ordinal
place        = lowercase *( lowercase / "-" ) lowercase
ordinal      = 1*( "i" / "v" / "x" )        ; lowercase Roman numeral
lowercase    = %x61-7A                        ; a-z
```

## 3. Data model

`data/councils.json` is the **hand-authored source of truth**: a JSON object
with registry metadata and an `entries` array of twenty-one council records, in
sequence order. Each record:

| field | type | meaning |
| --- | --- | --- |
| `number` | integer 1–21 | position in the Catholic sequence of ecumenical councils |
| `id` | string | the `oec:` canonical identifier |
| `name` | string | the council's common English name (e.g. "First Council of Nicaea") |
| `label_en` | string | display label (may equal `name`) |
| `aliases` | array of string | alternative names (e.g. "Council of Basel–Ferrara–Florence") |
| `location` | string | place of assembly (city) |
| `location_country` | string \| null | ISO 3166-1 alpha-2 of the modern country of that place (e.g. Nicaea → `TR`, Trent → `IT`, Vatican → `VA`) |
| `year_start` | integer | first year of the council |
| `year_end` | integer | last year of the council |
| `years_raw` | string | display form of the date span (e.g. "325", "1545–1563") |
| `century` | integer | century of the council |
| `reigning_pontiff` | string \| null | CRPDR `rp:` cross-reference to the pope reigning at the time |
| `convened_by` | object | `{ "text": <string>, "rp": <rp-id \| null> }` — who summoned the council; for the early councils this is a Roman emperor, so `text` names him and `rp` is null |
| `confirmed_by` | string \| null | CRPDR `rp:` cross-reference to the pope who confirmed the council's decrees, where applicable |
| `recognized_as_ecumenical_by` | array of string | the apostolic communions that **formally** receive it as ecumenical, from the controlled vocabulary `catholic` / `eastern_orthodox` / `oriental_orthodox` / `church_of_the_east` (§1.2). Always contains `catholic` |
| `reception_note` | string \| null | prose on recognition nuance a boolean cannot carry (e.g. Chalcedon as the Christological watershed and the modern miaphysite/Chalcedonian rapprochement; the Church of the East and the Nestorian question at Ephesus; broad Protestant doctrinal esteem for the first four) |
| `significance` | string | brief, original-wording summary of the council's principal doctrinal definitions and import |
| `note` | string \| null | disambiguation or context (e.g. the Orthodox eighth-council divergence; a council spanning several pontificates) |

The per-council recognition assignments over `recognized_as_ecumenical_by`:

| # | council | catholic | eastern_orthodox | oriental_orthodox | church_of_the_east |
| --- | --- | :-: | :-: | :-: | :-: |
| 1 | Nicaea I | ✓ | ✓ | ✓ | ✓ |
| 2 | Constantinople I | ✓ | ✓ | ✓ | ✓ |
| 3 | Ephesus | ✓ | ✓ | ✓ | — |
| 4 | Chalcedon | ✓ | ✓ | — | — |
| 5–7 | Constantinople II, Constantinople III, Nicaea II | ✓ | ✓ | — | — |
| 8–21 | Constantinople IV … Vatican II | ✓ | — | — | — |

Top-level metadata: a `$comment` (draft-status notice), `id_scheme`, a `sources`
array (the background references, explicitly marked non-authoritative), and
`council_count` (21).

### 3.1 Worked examples

```json
{
  "number": 1,
  "id": "oec:nicaea-i",
  "name": "First Council of Nicaea",
  "label_en": "First Council of Nicaea",
  "aliases": [],
  "location": "Nicaea",
  "location_country": "TR",
  "year_start": 325, "year_end": 325, "years_raw": "325",
  "century": 4,
  "reigning_pontiff": "rp:sylvester-i",
  "convened_by": { "text": "Emperor Constantine I", "rp": null },
  "confirmed_by": null,
  "recognized_as_ecumenical_by": ["catholic", "eastern_orthodox", "oriental_orthodox", "church_of_the_east"],
  "reception_note": null,
  "significance": "Defined the consubstantiality of the Son with the Father against Arianism; promulgated the original Nicene Creed and a common rule for the date of Easter.",
  "note": null
},
{
  "number": 19,
  "id": "oec:trent-i",
  "name": "Council of Trent",
  "label_en": "Council of Trent",
  "aliases": [],
  "location": "Trent",
  "location_country": "IT",
  "year_start": 1545, "year_end": 1563, "years_raw": "1545–1563",
  "century": 16,
  "reigning_pontiff": "rp:paul-iii",
  "convened_by": { "text": "Pope Paul III", "rp": "rp:paul-iii" },
  "confirmed_by": "rp:pius-iv",
  "recognized_as_ecumenical_by": ["catholic"],
  "reception_note": null,
  "significance": "Responded to the Protestant Reformation: defined Scripture and Tradition, original sin and justification, and the seven sacraments, and enacted sweeping disciplinary reform.",
  "note": "Convened in three periods (1545–1547, 1551–1552, 1562–1563) under Paul III, Julius III, and Pius IV; its decrees were confirmed by Pius IV in 1564."
}
```

### 3.2 The twenty-one councils and their IDs

| # | ID | Name | Years | Place (country) |
| --- | --- | --- | --- | --- |
| 1 | `oec:nicaea-i` | First Council of Nicaea | 325 | Nicaea (TR) |
| 2 | `oec:constantinople-i` | First Council of Constantinople | 381 | Constantinople (TR) |
| 3 | `oec:ephesus-i` | Council of Ephesus | 431 | Ephesus (TR) |
| 4 | `oec:chalcedon-i` | Council of Chalcedon | 451 | Chalcedon (TR) |
| 5 | `oec:constantinople-ii` | Second Council of Constantinople | 553 | Constantinople (TR) |
| 6 | `oec:constantinople-iii` | Third Council of Constantinople | 680–681 | Constantinople (TR) |
| 7 | `oec:nicaea-ii` | Second Council of Nicaea | 787 | Nicaea (TR) |
| 8 | `oec:constantinople-iv` | Fourth Council of Constantinople | 869–870 | Constantinople (TR) |
| 9 | `oec:lateran-i` | First Lateran Council | 1123 | Rome / Lateran (IT) |
| 10 | `oec:lateran-ii` | Second Lateran Council | 1139 | Rome / Lateran (IT) |
| 11 | `oec:lateran-iii` | Third Lateran Council | 1179 | Rome / Lateran (IT) |
| 12 | `oec:lateran-iv` | Fourth Lateran Council | 1215 | Rome / Lateran (IT) |
| 13 | `oec:lyon-i` | First Council of Lyon | 1245 | Lyon (FR) |
| 14 | `oec:lyon-ii` | Second Council of Lyon | 1274 | Lyon (FR) |
| 15 | `oec:vienne-i` | Council of Vienne | 1311–1312 | Vienne (FR) |
| 16 | `oec:constance-i` | Council of Constance | 1414–1418 | Constance (DE) |
| 17 | `oec:florence-i` | Council of Florence | 1431–1445 | Basel / Ferrara / Florence (IT) |
| 18 | `oec:lateran-v` | Fifth Lateran Council | 1512–1517 | Rome / Lateran (IT) |
| 19 | `oec:trent-i` | Council of Trent | 1545–1563 | Trent (IT) |
| 20 | `oec:vatican-i` | First Vatican Council | 1869–1870 | Vatican (VA) |
| 21 | `oec:vatican-ii` | Second Vatican Council | 1962–1965 | Vatican (VA) |

The country column follows the modern political geography of the place of
assembly. The five **Lateran** councils met at the Basilica of St. John Lateran,
which stands in Rome and so is attributed to Italy (`IT`); the two **Vatican**
councils met at the Basilica of St. Peter, within the modern sovereign territory
of Vatican City State (`VA`). The seventeenth council's `location_country` is
`IT` for Florence, the city that gives it its conventional name, with Basel (CH)
and Ferrara (IT) recorded in the `note`.

## 4. Repository layout

```
coecdr/
  README.md                        — what/why, ID scheme summary, contents, sources
  LICENSE                          — Apache-2.0
  .gitignore
  data/councils.json               — hand-authored source of truth (21 entries)
  registry/councils.md             — generated human-readable table
  docs/schema-proposal.md          — full ID grammar, ordinal rule, open questions
  docs/superpowers/specs/          — this design document
  scripts/generate_registry.py     — renders registry/councils.md from data/councils.json
  scripts/test_generate_registry.py
```

`data/councils.json` is authored by hand; `registry/councils.md` is **generated**
from it by `scripts/generate_registry.py` (`python3 scripts/generate_registry.py`),
so the table can never silently drift from the data. Tests:
`python3 -m unittest discover -s scripts`. The generator validates the data as it
renders (unique IDs, well-formed `oec:` grammar, `number` 1–21 contiguous,
`recognized_as_ecumenical_by` non-empty and always containing `catholic`, its
values drawn only from the controlled vocabulary, `rp:` cross-references
well-formed) and fails loudly on any violation.

## 5. Open questions (recorded in `docs/schema-proposal.md`, non-blocking)

1. **`cdcf:` cross-reference.** Whether to add a `cdcf:council/…` cross-reference
   field once the [cdcf-uri-scheme](https://github.com/xudonglab/cdcf-uri-scheme)
   defines a council namespace, analogous to CRPDR's `cdcf_person`.
2. **Conciliar documents / canons.** How finely to enumerate a council's
   constitutions, decrees, or canons — out of scope for the seed, but the data
   model should not preclude a later `documents` array.
3. **Further common-core communions.** Whether to extend
   `recognized_as_ecumenical_by` beyond the four apostolic communions modelled
   here (e.g. to represent Anglican or Old Catholic positions), or to keep such
   doctrinal-esteem relationships in prose as the design currently does.

Resolved during review (recorded here for provenance): Eastern Catholic
recognition is subsumed under `catholic` (those churches, in communion with Rome,
receive all twenty-one); the Lateran councils are attributed to `IT` (Basilica of
St. John Lateran, in Rome) and the Vatican councils to `VA` (Basilica of St.
Peter, Vatican City).

All IDs and fields are **drafts pending CETF review.**
