# Data Provenance & Sourcing

Every error code in ApplianceDB is re-derived from an official manufacturer
support listing. The exact article URL is stored in the `source_url` column of
`error_codes.csv` for every row — provenance is per-record, not per-dataset.

## Source listings (v1)

| Ref | Brand | Appliance | Official listing |
| :--- | :--- | :--- | :--- |
| `lg_washer` | LG | Washer | LG USA Support — Washer Error Code List |
| `lg_dryer` | LG | Dryer | LG USA Support — Dryer Error Code List |
| `lg_refrigerator` | LG | Refrigerator | LG USA Support — Refrigerator Error Code List |
| `lg_dishwasher` | LG | Dishwasher | LG USA Support — Dishwasher Error Code List |
| `samsung_washer` | Samsung | Washer | Samsung US Support — Washing Machine Error Codes |
| `samsung_dryer` | Samsung | Dryer | Samsung US Support — Dryer Error Codes |
| `samsung_refrigerator` | Samsung | Refrigerator | Samsung US Support — Refrigerator Error Codes |
| `samsung_dishwasher` | Samsung | Dishwasher | Samsung US Support — Dishwasher Error Codes |
| `ge_dishwasher` | GE Appliances | Dishwasher | GE Appliances Support — Dishwasher Error/Fault/Function Codes |
| `whirlpool_wash_fl` / `_tl` | Whirlpool | Washer | Whirlpool Product Help — Error Codes in Front / Top Load HE Washers |
| `maytag_wash_fl` / `_tl` | Maytag | Washer | Maytag Product Help — Error Codes in Front / Top Load HE Washers |
| `lg_range` | LG | Oven/Range | LG USA Support — Range Error Codes List |
| `ge_range` | GE Appliances | Oven/Range | GE Appliances Support — Range & Wall Oven Fault Codes |
| `whirlpool_range` / `_f` | Whirlpool | Oven/Range | Whirlpool Product Help — Cooking Appliance Error Codes (+ per-code articles) |
| `frigidaire_dishwasher` | Frigidaire | Dishwasher | Frigidaire Owner Support — Dishwasher Error Codes and Alarms Guide |
| `samsung_uk_washer` | Samsung (UK market) | Washer | Samsung UK Support — washing machine code meanings |

### Aggregator listings (`source_type = aggregator_listing`)

Used where the manufacturer's official pages are unfetchable. Each row is
flagged with `source_type='aggregator_listing'` so buyers can filter by tier.

| Ref | Brand | Appliance | Secondary reference |
| :--- | :--- | :--- | :--- |
| `bosch_dishwasher_agg` | Bosch | Dishwasher | ApplianceCodeHub — Bosch Dishwasher Error Codes |
| `frigidaire_washer_agg` | Frigidaire | Washer | ApplianceAid — Frigidaire Front-Load Washer Fault Codes |
| `bosch_washer_agg` | Bosch | Washer | ApplianceCodeHub — Bosch Washing Machine Error Codes |
| `whirlpool_dryer_agg` | Whirlpool | Dryer | ApplianceCodeHub — Whirlpool Dryer Error Codes |
| `frigidaire_dw_agg` | Frigidaire | Dishwasher | ApplianceCodeHub — Frigidaire Dishwasher Error Codes (supplements the official guide) |
| `hotpoint_uk_washer_agg` | Hotpoint (UK market) | Washer | Whitegoods Help — Hotpoint Washing Machine Error Codes |
| `indesit_uk_washer_agg` | Indesit (UK market) | Washer | Whitegoods Help — Indesit Washing Machine Error Codes |
| `beko_uk_washer_agg` | Beko (UK market) | Washer | Whitegoods Help — Beko Washing Machine Error Codes |
| `miele_uk_washer_agg` | Miele (UK market) | Washer | Domex UK — Miele Washing Machine Fault Codes |
| `candy_uk_washer_agg` | Candy (UK market) | Washer | Whitegoods Help — Candy Washing Machine Error Codes |
| `hoover_uk_washer_agg` | Hoover (UK market) | Washer | Whitegoods Help — Hoover Washing Machine Error Codes |

The exact URLs are carried in `source_url`; see any row of `error_codes.csv`.

**Why aggregators for these two:** Bosch's official error-code pages return
HTTP 403 to automated fetches, and Frigidaire's official washer page carries no
inline code table — so their codes are sourced from reputable secondary repair
references (which republish the manufacturer tech-sheet tables) and clearly
flagged. All meanings remain original paraphrase.

**Shared-platform note:** Whirlpool/Maytag/KitchenAid legitimately share the
`F#E#` code scheme; rows are kept per brand — each sourced from that brand's own
listing — so brand-filtered lookups return complete results.

### Recall cross-reference

`brand_recalls.csv` is computed from the sibling **RecallDB** corpus (CPSC and
other agencies); every row carries the agency listing URL as provenance.
ApplianceDB adds only the brand match (word-boundary, alias-aware, with strict
rules for ambiguous names) — the recall facts are RecallDB's.

## Methodology & integrity

- **Facts, not prose.** A code's identifier, implicated component, and cause
  category are facts (not copyrightable). Meanings and repair steps are
  **paraphrased into original wording** — no manufacturer manual sentence is
  reproduced verbatim.
- **No memory sourcing.** LLMs "know" appliance codes from training data; that
  knowledge is *not* a source. Every fact was re-read from the fetched page.
- **Ranks earn a basis.** v1 repair procedures are `manufacturer_first` — the
  remedy the manufacturer directs first. Frequency-based re-ranking awaits
  recorded community-signal counts.
- **NULL over guess.** No costs, labor times, or part numbers are published
  without a verified observation.
- **Coverage honesty.** Any `(brand, appliance_type)` pair below 10 verified
  codes is dropped, not padded — GE refrigerator (8) and GE combo washer (2)
  were excluded from v1 on this basis.

## Roadmap

Additional brands (Whirlpool, Maytag, KitchenAid, Bosch, Frigidaire) and the
parts-cost layer (OEM part numbers + recorded street-price ranges) extend the
corpus using the identical fetch → paraphrase → provenance pipeline.
