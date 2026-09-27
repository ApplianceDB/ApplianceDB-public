# Data Provenance & Sourcing

Every error code in ApplianceDB is re-derived from a fetched source listing of
one of two kinds: an official manufacturer support page
(`source_type = manufacturer_listing`) or, where the manufacturer's own listing
was unfetchable or too thin, an independent appliance-repair reference site —
ApplianceCodeHub, Whitegoods Help, ApplianceAid, or the help pages of UK repair
firm Domex (`source_type = aggregator_listing`). The tier and the exact article
URL are stored per row in `error_codes.csv` (`source_type`, `source_url`) —
provenance is per-record, not per-dataset.

## Manufacturer listings (`source_type = manufacturer_listing`)

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
| `whirlpool_dryer` | Whirlpool | Dryer | Whirlpool Product Help — Error Codes in Dryers (remedy source for AF and PF; the dryer codes themselves come from ApplianceCodeHub) |

### Aggregator listings (`source_type = aggregator_listing`)

Used where the manufacturer's own listing is unfetchable or too thin to reach
the 10-code floor. Each row is flagged with `source_type='aggregator_listing'`
so buyers can filter by tier.

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

**Why aggregators:** Bosch's official error-code pages return HTTP 403 to
automated fetches, and Frigidaire's official washer page carries no inline code
table. The other aggregator-sourced pairs were added where the brand's own
listing was unfetchable or too thin to reach the 10-code floor. All are clearly
flagged, and all meanings remain original paraphrase.

### Repair-guide listings (fix layer)

Some remedies for aggregator-sourced codes were paraphrased from per-code
ApplianceCodeHub repair guides. Each such remedy carries its guide as its own
source (`source_type` / `source_url` in `repair_procedures.csv`, and a
"Remedy source" line on its code page); other remedies cite the code's listing.

| Ref | Guide | URL |
| :--- | :--- | :--- |
| `bosch_e15_fix` | Bosch Dishwasher E15 Guide | https://www.appliancecodehub.com/bosch-dishwasher-error-e15.html |
| `bosch_e24_fix` | Bosch Dishwasher E24 Guide | https://www.appliancecodehub.com/bosch-dishwasher-error-e24.html |
| `frigidaire_e11_fix` | Frigidaire Washer E11 Guide | https://www.appliancecodehub.com/frigidaire-washing-machine-error-e11.html |
| `frigidaire_e21_fix` | Frigidaire Washer E21 Guide | https://www.appliancecodehub.com/frigidaire-washing-machine-error-e21.html |
| `miele_f11_fix` | Miele Washer F11 Guide | https://www.appliancecodehub.com/miele-washing-machine-error-f11.html |
| `miele_f10_fix` | Miele Washer F10 Guide | https://www.appliancecodehub.com/miele-washing-machine-error-f10.html |
| `miele_f20_fix` | Miele Washer F20 Guide | https://www.appliancecodehub.com/miele-washing-machine-error-f20.html |
| `miele_f34_fix` | Miele Washer F34 Guide | https://www.appliancecodehub.com/miele-washing-machine-error-f34.html |
| `candy_e01_fix` | Candy Washer E01 Guide | https://www.appliancecodehub.com/candy-washing-machine-error-e01.html |
| `candy_e02_fix` | Candy Washer E02 Guide | https://www.appliancecodehub.com/candy-washing-machine-error-e02.html |
| `candy_e03_fix` | Candy Washer E03 Guide | https://www.appliancecodehub.com/candy-washing-machine-error-e03.html |
| `candy_e08_fix` | Candy Washer E08 Guide | https://www.appliancecodehub.com/candy-washing-machine-error-e08.html |
| `hoover_e01_fix` | Hoover Washer E01 Guide | https://www.appliancecodehub.com/hoover-washing-machine-error-e01.html |
| `hoover_e02_fix` | Hoover Washer E02 Guide | https://www.appliancecodehub.com/hoover-washing-machine-error-e02.html |
| `hoover_e03_fix` | Hoover Washer E03 Guide | https://www.appliancecodehub.com/hoover-washing-machine-error-e03.html |
| `hotpoint_f01_fix` | Hotpoint Washer F01 Guide | https://www.appliancecodehub.com/hotpoint-washing-machine-error-f01.html |
| `hotpoint_f08_fix` | Hotpoint Washer F08 Guide | https://www.appliancecodehub.com/hotpoint-washing-machine-error-f08.html |
| `indesit_f08_fix` | Indesit Washer F08 Guide | https://www.appliancecodehub.com/indesit-washing-machine-error-f08.html |
| `beko_e01_fix` | Beko Washer E01 Guide | https://www.appliancecodehub.com/beko-washing-machine-error-e01.html |
| `beko_e03_fix` | Beko Washer E03 Guide | https://www.appliancecodehub.com/beko-washing-machine-error-e03.html |
| `miele_f53_fix` | Miele Washer F53 Guide | https://www.appliancecodehub.com/miele-washing-machine-error-f53.html |
| `candy_e16_fix` | Candy Washer E16 Guide | https://www.appliancecodehub.com/candy-washing-machine-error-e16.html |
| `hoover_e05_fix` | Hoover Washer E05 Guide | https://www.appliancecodehub.com/hoover-washing-machine-error-e05.html |
| `whirlpool_f01_fix` | Whirlpool Dryer F01 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f01.html |
| `whirlpool_f02_fix` | Whirlpool Dryer F02 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f02.html |
| `whirlpool_f06_fix` | Whirlpool Dryer F06 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f06.html |
| `whirlpool_f20_fix` | Whirlpool Dryer F20 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f20.html |
| `whirlpool_f24_fix` | Whirlpool Dryer F24 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f24.html |
| `whirlpool_f25_fix` | Whirlpool Dryer F25 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f25.html |
| `whirlpool_f26_fix` | Whirlpool Dryer F26 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f26.html |
| `whirlpool_f29_fix` | Whirlpool Dryer F29 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f29.html |
| `whirlpool_f30_fix` | Whirlpool Dryer F30 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f30.html |
| `whirlpool_f31_fix` | Whirlpool Dryer F31 Guide | https://www.appliancecodehub.com/whirlpool-dryer-error-f31.html |

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
- **Ranks earn a basis.** Each repair procedure carries `manufacturer_first`
  (the remedy the manufacturer directs first) or `cost_ascending` (free checks
  before part replacement). Frequency-based re-ranking awaits recorded
  community-signal counts.
- **NULL over guess.** No costs, labor times, or part numbers are published
  without a verified observation.
- **Coverage honesty.** Any `(brand, appliance_type)` pair below 10 verified
  codes is dropped, not padded — GE refrigerator (8) and GE combo washer (2)
  were excluded from v1 on this basis.

## Roadmap

Further brands and markets, per-remedy source links for the fix-layer guides,
and a wider parts-cost layer (OEM part numbers + recorded street-price ranges)
extend the corpus using the identical fetch → paraphrase → provenance pipeline.
