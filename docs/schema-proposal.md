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
| `reigning_pontiff` | string \| null | `rp:` cross-reference to the pope reigning at the council's opening — for a council convoked under one pope but substantially held under his successor, the pope of the council proper |
| `convened_by` | object | `{ "text": string, "rp": string\|null }` — who summoned it |
| `confirmed_by` | string \| null | `rp:` cross-reference to the confirming pope |
| `recognized_as_ecumenical_by` | list[string] | formal-reception set (see §3) |
| `reception_note` | string \| null | prose on recognition nuance |
| `significance` | string | brief original summary of the council's import |
| `note` | string \| null | disambiguation / context |

For councils spanning several pontificates, `reigning_pontiff` names the pope
reigning when the council opened — or, where a council was convoked under one
pope but substantially held under his successor, the pope of the council
proper — and `note` records the transfer. For the first eight councils
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
