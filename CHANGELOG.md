# Changelog

All notable changes to the ApplianceDB free developer sample are documented here.
Snapshots follow `YYYY.MM` naming.

## [Unreleased]

### Added (distribution + recall cross-reference)
- **438 standalone SEO code pages** under `landing/` (one per
  brand × market × appliance type × code) plus 5 category hubs, `sitemap.xml`
  (444 URLs) and `robots.txt` — each page renders the shipped row with its
  ranked fixes, observed part costs, structured data (TechArticle,
  BreadcrumbList, FAQPage), and provenance link.
- **`brand_recalls.csv` (69 rows)**: appliance recalls affecting these brands,
  cross-referenced from the sibling RecallDB corpus with per-recall agency
  URLs and recalled model numbers. Word-boundary brand matching; ambiguous
  names (Candy, Hoover) restricted to CPSC laundry/dishwasher recalls.

### Added (long-tail remedies + parts)
- **16 long-tail remedy procedures** for Hotpoint F01/F08, Indesit F08, Beko
  E01/E03, Miele F53, Candy E16, Hoover E05 (per-code guides; fix-layer
  sources registered). 288 procedures; 39 codes carry multi-rank chains.
- **Data correction**: Hotpoint/Indesit `F08` is a heater-relay fault — the
  summary-table "door interlock" attribution was corrected against the
  deeper per-code sources.
- **2 new parts**: C00299278 door interlock (Hotpoint/Indesit `F16`,
  GBP 14.49–28.10) and LG EAU62043403 dishwasher drain pump motor (`OE`,
  USD 40.72–103.95). 17 parts / 20 procedure mappings.

### Notes
- `frequency_reported` re-ranking remains deferred: the community sources
  that could yield recordable report counts (repair forums, fixya, reddit)
  are not machine-accessible, and a rank basis without recorded evidence is
  fabrication. `manufacturer_first` and `cost_ascending` remain the shipped
  bases.

### Added (UK remedy enrichment)
- **23 multi-rank `cost_ascending` fix chains** for the flagship faults of
  Miele (F10/F11/F20/F34), Candy (E01/E02/E03/E08), and Hoover (E01/E02/E03)
  from per-code repair guides (fix-layer sources registered). Guide cost
  estimates were NOT shipped as costs — estimates are not dated retailer
  observations. 269 procedures total; 30 codes carry multi-rank chains.

### Added (UK deepening + full provenance)
- **Per-row provenance on every file**: `repair_procedures.csv` now carries
  `source_type` + `source_url` (the parent code's listing) — completing
  provenance coverage across all four exports.
- **Miele (27), Candy (22), Hoover (23)** UK washers via disclosed aggregator
  listings; Candy/Hoover share the Haier Europe platform but ship per brand
  with per-brand provenance, and Hoover's motor-generation code variance is
  encoded in the meanings.
- **Fisher & Paykel (AU) attempted and dropped**: official fault-code articles
  are JS-rendered and the aggregator states only 3 meanings — below the gate.
  `AU` stays reserved.

Corpus: **438 codes · 13 brands · 26 pairs · 2 markets (US 293 / UK 145)**.

### Added (currency + UK expansion)
- **Currency-aware costs**: cost columns are now `parts_cost_min/max` +
  `cost_currency` and `street_price_min/max` + `price_currency` (USD, GBP;
  EUR/CAD/AUD reserved) — prices are observed in the market's own currency,
  never converted. (Column rename from the `*_usd` names; pre-publish break.)
- **UK grows to 4 brands / 73 codes**: Indesit (17) and Beko (13) washers join
  Samsung UK and Hotpoint. Zanussi dropped (official page lists only 8
  category-level codes — below the 10-code gate).
- **First GBP part**: C00119307 drain pump (fits Hotpoint + Indesit `F05`) at
  GBP 19.49–32.49 from two named UK retailer observations, attached to new
  clear-then-replace F05 fix chains.

Corpus: **366 codes · 10 brands · 23 pairs · 2 markets · 246 procedures ·
15 parts (14 USD + 1 GBP)**.

### Added (multi-market)
- **`market` joins the composite code identity** — records are now unique on
  `(brand, market, appliance_type, code)`, because regions ship different code
  sets (Samsung UK washer `5C` is a separate record from Samsung US washer
  `5C`, with its own meaning and fix). Vocabulary: `US`, `UK` shipped; `EU`,
  `CA`, `AU` reserved.
- **UK market launch**: Samsung UK washer (26 codes + 26 manufacturer fixes,
  incl. UK-only codes like `11E`/`12E`/`PLO`/`HOT`) and **Hotpoint** UK washer
  (17 codes) — the 8th brand. Corpus: **336 codes · 21 pairs · 2 markets ·
  242 procedures**. UK costs are NULL pending UK price observations (cost
  columns remain USD).

### Added (final grind)
- **Oven/range category** (3 new pairs): LG (18 codes with per-code reset
  remedies), GE (16, reset-then-replace guidance), Whirlpool (11).
- **Whirlpool dryer (12)** and **Bosch washer (20)** via disclosed aggregator
  listings; **Frigidaire dishwasher (17)** merging the official owner guide
  with aggregator rows.
- Corpus at snapshot: **293 codes · 7 brands · 19 pairs across 5 categories ·
  216 ranked procedures (67% coverage) · 14 OEM parts** with dated price
  observations. Provenance split: 213 manufacturer / 80 aggregator.
- Honesty filters: codes whose source stated no meaning were dropped, as were
  pairs under 10 codes (Samsung range, Maytag dryer, GE washer/refrigerator,
  Frigidaire refrigerator).

### Added
- **Whirlpool and Maytag washers** (18 codes each) from each brand's own Product
  Help error-code pages, with per-brand provenance.
- **Bosch dishwasher (18)** and **Frigidaire front-load washer (19)** from
  reputable secondary references (official pages unfetchable), flagged
  `source_type='aggregator_listing'`.
- New **`source_type`** column on `error_codes` distinguishing
  `manufacturer_listing` from `aggregator_listing`.
- **45 new repair procedures**: Whirlpool + Maytag washers (manufacturer_first
  steps from each brand's own pages) and the first **multi-rank fix chains**
  (Bosch E15/E24, Frigidaire E11/E21; `rank_basis='cost_ascending'` — free DIY
  checks first, component replacement last). 81 of 199 codes now carry ≥1
  ranked fix (89 procedures total).
- **Parts + cost layer**: 14 exact OEM part numbers (drain pumps, door
  locks/latches, inlet valve, dryer heating element, dryer thermistor, fridge
  evaporator fan) mapped to replace-component procedures, corroborated against
  each manufacturer's own parts store, with **dated per-retailer price
  observations** shipped in the new `price_observations` column. Costed
  procedures carry `parts_cost` ranges + `cost_year`. Parts without a named
  price observation were dropped rather than estimated.
- **Fix scale-out to 70% coverage (159 procedures)**: LG + Samsung dryer and
  refrigerator remedies from the official listings — including honest
  `professional_only` rows where the manufacturer publishes no user
  troubleshooting — plus GE dishwasher reset/replace chains. 17 codes carry
  multi-rank fix chains.

Corpus now **199 codes across 7 brands / 13 pairs** — 162 manufacturer-sourced,
37 aggregator-sourced.

### Notes
- Whirlpool/Maytag dishwasher+dryer official consolidated pages carry <10
  described codes (deferred to a per-code pass).

## [2026.07] — Initial release

### Added
- **126 verified error codes** across 3 brands (LG, Samsung, GE) and 9
  `(brand, appliance_type)` pairs — washer, dryer, dishwasher, refrigerator.
- **41 manufacturer-directed repair procedures** (`rank_basis = manufacturer_first`)
  with DIY difficulty tiers and paraphrased remedy steps.
- Per-record provenance: every code carries its manufacturer `source_url`.
- Formats: CSV + Parquet, plus a pre-joined analytical view.
- Full `dataset-metadata.json` (ODbL-1.0, every column described).

### Integrity
- Every fact re-derived from an official manufacturer listing — no memory
  sourcing, no verbatim manufacturer prose.
- Coverage-honesty gate applied: GE refrigerator (8 codes) and GE combo washer
  (2) dropped for falling below the ≥ 10-per-pair threshold.
- Parts/cost columns intentionally NULL pending verified price observations.
