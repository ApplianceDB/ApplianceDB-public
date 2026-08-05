<div align="center">

# 🔧 ApplianceDB — Home Appliance Error Codes & Ranked Repairs

**438 verified error codes · 13 brands (LG · Samsung · GE · Whirlpool · Maytag · Bosch · Frigidaire · Hotpoint · Indesit · Beko · Miele · Candy · Hoover) · 2 markets (US · UK) · 26 brand×market×appliance pairs across 5 categories · 288 ranked repair procedures · 17 OEM parts with currency-aware observed price ranges (USD + GBP) · per-row provenance on every file**

[![Dataset License: ODbL v1.0](https://img.shields.io/badge/Dataset_License-ODbL_v1.0-blue.svg)](https://opendatacommons.org/licenses/odbl/1-0/)
[![Free sample: 438 codes](https://img.shields.io/badge/Free%20Sample-438%20codes-00F2FE.svg)](#whats-inside)
[![Full dataset: $299+](https://img.shields.io/badge/Full%20dataset-%24299%2B-F59E0B.svg)](#pricing)
[![Snapshot: 2026.07](https://img.shields.io/badge/Snapshot-2026.07-blue.svg)](CHANGELOG.md)
[![Site](https://img.shields.io/badge/Site-appliancedb--public.pages.dev-0a7c66.svg)](https://appliancedb-public.pages.dev/)

**[→ Browse the data at appliancedb-public.pages.dev](https://appliancedb-public.pages.dev/)** · **[Request the full dataset](mailto:appliancedb.untapped361@silomails.com?subject=ApplianceDB%20licensing)**

</div>

---

A structured dataset that turns an appliance error code into an **actionable repair plan**: every fault code is keyed by its **composite `(brand, market, appliance_type, code)` identity** — Samsung *washer* `5C` is a distinct record from Samsung *dishwasher* `5C`, and Samsung *US* washer `5C` is distinct from Samsung *UK* washer `5C` (regions ship different code sets) — and mapped to the manufacturer-directed remedy with a **DIY difficulty tier**, an implicated component, and a fault category.

This repository is the **free, open developer sample**, in the identical schema as the commercial database, so you can prototype joins, pipelines, and apps before licensing.

## What's inside

| File | Rows | Description |
| :--- | ---: | :--- |
| `error_codes.csv` / `.parquet` | 438 | Code registry: brand, appliance type, normalized code, meaning, component, cause category, severity, **`source_type` + source URL** |
| `repair_procedures.csv` / `.parquet` | 288 | Ranked repair procedures: rank + basis, title, paraphrased steps, DIY difficulty, **currency-aware** parts-cost ranges where observed, and **`source_type` + `source_url` provenance** on every row |
| `replacement_parts.csv` / `.parquet` | 20 | Exact OEM part numbers mapped to repair procedures, with **dated street-price observations** (retailer=price@date) and an explicit `price_currency` (USD / GBP) — prices observed in the market's own currency, never converted |
| `error_codes_fixes_joined.csv` / `.parquet` | 479 | Pre-joined analytical view (codes × fixes) for one-file ingestion |
| `brand_recalls.csv` | 69 | **Appliance recalls affecting these brands**, cross-referenced from the sibling [RecallDB](https://github.com/RecallDB) corpus (CPSC et al.) — recall IDs, dates, model numbers, remedies, and the agency listing URL per row |

**Coverage (each brand×market×type pair ≥ 10 codes):**

*US market:*

| Brand | Washer | Dryer | Dishwasher | Refrigerator | Oven/Range |
| :--- | ---: | ---: | ---: | ---: | ---: |
| LG | 14 | 14 | 11 | 16 | 18 |
| Samsung | 16 | 14 | 14 | 14 | — |
| GE | — | — | 13 | — | 16 |
| Whirlpool | 18 | 12 | — | — | 11 |
| Maytag | 18 | — | — | — | — |
| Bosch | 20 | — | 18 | — | — |
| Frigidaire | 19 | — | 17 | — | — |

*UK market (new — regions ship different code sets, so UK codes are separate records):*

| Brand | Washer |
| :--- | ---: |
| Samsung | 26 |
| Hotpoint | 17 |
| Indesit | 17 |
| Beko | 13 |
| Miele | 27 |
| Candy | 22 |
| Hoover | 23 |

**Provenance tiers:** 239 codes are `manufacturer_listing` (official brand support pages); 199 are `aggregator_listing` (reputable secondary repair references, used where official pages were unfetchable or thin). The `source_type` column flags every row so you can filter by tier. Codes whose source stated no meaning were **dropped, not padded** — as were `(brand, appliance_type)` pairs below 10 verified codes (Samsung range, Maytag dryer, GE washer/refrigerator, Frigidaire refrigerator, Zanussi UK washer, Fisher & Paykel AU washer).

Full column documentation: [DATA_DICTIONARY.md](DATA_DICTIONARY.md). CSVs are comma-delimited, UTF-8.

## How the content is built (the honest part)

- **No fabricated codes, ever.** Every published code is re-derived from a fetched source listing — never from model memory. Most are official manufacturer support pages; a disclosed minority come from reputable secondary repair references where the manufacturer page was unfetchable. The `source_type` and exact `source_url` are stored per row. Full lineage in [SOURCES.md](SOURCES.md).
- **Facts, not prose.** Code meanings and repair steps are **paraphrased into original wording** — manufacturer manual text is copyrighted and never reproduced verbatim.
- **Ranks earn their basis.** Each repair procedure carries an explicit `rank_basis`: `manufacturer_first` (the manufacturer's directed remedy) or `cost_ascending` (multi-step fix chains ordered from free DIY checks to component replacement). Frequency-based re-ranking is deferred until recorded community-signal counts exist — a rank without evidence is a guess, and guesses don't ship.
- **NULL over guess.** Parts and labor costs are left NULL wherever no verified price observation exists — never estimated. Where costs ARE present, the per-retailer observations behind the range (`retailer=price@date`) ship in the `price_observations` column; part numbers are corroborated against the manufacturer's own parts store.
- **Coverage honesty beats width.** Any `(brand, appliance_type)` pair with fewer than 10 verified codes is dropped rather than padded — Samsung range, Maytag dryer, GE washer/refrigerator, and Frigidaire refrigerator all sit outside v1 for exactly this reason.
- **Deterministic, test-gated build.** Composite-uniqueness, controlled-vocabulary, rank-contiguity, provenance, and ≥10-per-pair coverage gates all run in CI; rebuilds are reproducible.

## Browse the data as pages

Every code also renders as a standalone SEO page — 438 monographs plus per-category hubs, live at [appliancedb-public.pages.dev](https://appliancedb-public.pages.dev/) (e.g. [`landing/samsung-washer-5c.html`](https://appliancedb-public.pages.dev/landing/samsung-washer-5c.html)), each showing the meaning, ranked fixes, observed part costs, and its provenance link. `sitemap.xml` covers all of them.

## Use cases

- Appliance-repair and smart-home assistant apps (code → meaning → ranked fix in one join)
- Home-warranty and field-service triage automation (first-line diagnosis from the displayed code)
- AI home-maintenance co-pilots and RAG corpora over appliance diagnostics
- Parts e-commerce fitment and upsell tooling

## Quickstart

```python
import pandas as pd

codes = pd.read_csv("error_codes_fixes_joined.csv")
lg_drain = codes[(codes["brand"] == "LG") & (codes["cause_category"] == "drainage")]
print(lg_drain[["appliance_type", "code", "meaning", "title", "diy_difficulty"]])
```

## License

- **Sample dataset (this repo):** [Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1-0/) — free for research, education, and benchmarking with attribution and share-alike (see [LICENSE](LICENSE)).
- **Full / commercial dataset:** separate commercial license — see [Pricing](#pricing).
- **Documentation:** CC BY 4.0.

⚠️ **Safety:** repair steps are educational reference material, not a substitute for the manufacturer's service manual. Disconnect power and water before servicing; gas, sealed-refrigerant, and high-voltage work must only be performed by qualified technicians.

## Pricing

| Tier | What | Price |
| :--- | :--- | ---: |
| **Sample** | 438 codes (this repo + Kaggle) · CSV + Parquet | Free |
| **Repair Intelligence Snapshot** | Full corpus · CSV + Parquet + SQLite · quarterly refresh · instant download | **[$299](https://buy.stripe.com/9B64gA08Mcnk7nJgyY3840a)** |
| **Enterprise Integration License** | Everything in Snapshot + commercial embedding rights (warranty / field-service platforms) · parts cross-reference tables · priority code-coverage requests | **[$2,999 — request a quote](https://appliancedb-public.pages.dev/enterprise)** |

The Snapshot is self-serve: secure Stripe checkout (card / Apple Pay / Google Pay), **instant download** after payment, commercial license in the archive (see [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)). Enterprise is scoped per platform via the [request form](https://appliancedb-public.pages.dev/enterprise).

**[→ Request the full dataset](mailto:appliancedb.untapped361@silomails.com?subject=ApplianceDB%20licensing)** · or email **[appliancedb.untapped361@silomails.com](mailto:appliancedb.untapped361@silomails.com)** for a company invoice, quarterly-refresh subscription, or custom coverage.

Spotted a wrong fix, code meaning, or provenance link? See [CONTRIBUTING.md](CONTRIBUTING.md).
