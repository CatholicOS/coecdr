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

```text
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

## License

The data and documentation in this repository are licensed under the [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nc-nd/4.0/) (CC BY-NC-ND 4.0). See [`LICENSE`](LICENSE) for the full legal code.
