# ApplianceDB — Data Dictionary

All files are UTF-8, comma-delimited. The commercial corpus additionally ships
as SQLite. Codes are keyed by their composite `(brand, market, appliance_type, code)`
identity: the same code string is a **different record** across brands,
markets, and appliance types (regions ship different code sets).

## `error_codes.csv` (438 rows)

| Column | Type | Description |
| :--- | :--- | :--- |
| `code_id` | int | Primary key for the error-code record. |
| `brand` | string | Appliance manufacturer (`LG`, `Samsung`, `GE`, `Whirlpool`, `Maytag`, `Bosch`, `Frigidaire`, `Hotpoint`, `Indesit`, `Beko`, `Miele`, `Candy`, `Hoover`). |
| `market` | enum | Sales market the listing applies to: `US`, `UK` (vocabulary reserves `EU`, `CA`, `AU`). Part of the composite identity. |
| `appliance_type` | enum | `washer`, `dryer`, `dishwasher`, `refrigerator`, `oven_range`, `microwave`, `hvac`, `water_heater`. |
| `code` | string | Normalized error/fault code as shown on the display (uppercase, separators stripped: `5C`, `E11`, `F21`). |
| `meaning` | string | Original-wording explanation of what the code indicates (paraphrased; never verbatim manufacturer prose). |
| `component` | string | Primary component or subsystem implicated. |
| `cause_category` | string | Fault category — see controlled vocabulary below. |
| `severity` | enum | `informational`, `degraded`, or `stop_failure`. |
| `source_type` | enum | Provenance tier: `manufacturer_listing` (official brand page) or `aggregator_listing` (reputable secondary reference). |
| `source_name` | string | Human-readable name of the source listing. |
| `source_url` | url | Exact source URL used as provenance for this code. |

## `repair_procedures.csv` (288 rows)

| Column | Type | Description |
| :--- | :--- | :--- |
| `procedure_id` | int | Primary key for the repair procedure. |
| `code_id` | int | FK → `error_codes.code_id`. |
| `brand` / `appliance_type` / `code` | | Denormalized identity of the parent code. |
| `rank` | int | Attempt order (1 = try first); contiguous `1..N` per code. |
| `rank_basis` | enum | `manufacturer_first`, `frequency_reported`, or `cost_ascending`. |
| `title` | string | Short actionable title of the repair step. |
| `steps` | string | Original-wording remedy paraphrased from the manufacturer's guidance. |
| `diy_difficulty` | enum | `easy`, `moderate`, `advanced`, `professional_only`. |
| `est_labor_minutes` | int? | Estimated labor minutes (NULL where not observed). |
| `source_type` / `source_url` | | Provenance of the parent code's listing — the remedy is paraphrased from the same source. |
| `parts_cost_min` / `parts_cost_max` | decimal? | Parts-cost range in `cost_currency` units (NULL where no verified price observation). |
| `cost_currency` | enum | ISO currency of the cost range (`USD`, `GBP`; vocabulary reserves `EUR`, `CAD`, `AUD`). Costs are observed in the market's own currency, never converted. |
| `cost_year` | int? | Year the cost range was observed. |

## `replacement_parts.csv` (20 rows)

| Column | Type | Description |
| :--- | :--- | :--- |
| `part_id` | int | Primary key for the part. |
| `procedure_id` | int | FK → the repair procedure this part is mapped to. |
| `brand` / `appliance_type` / `code` | | Identity of the linked error code. |
| `oem_part_number` | string | Exact OEM part number (character-for-character from source, corroborated against the manufacturer's own parts store). |
| `name` | string | Part name/description. |
| `street_price_min` / `street_price_max` | decimal | Observed street-price range in `price_currency` units (single observation ⇒ equal bounds). |
| `price_currency` | enum | ISO currency of the observed prices (`USD`, `GBP`). |
| `cost_year` | int | Year the price range was observed. |
| `price_source_url` | url | Primary retailer/OEM-store URL for the observations. |
| `price_observations` | string | The recorded per-retailer observations (`retailer=price@date`) behind the range. |

Grows as verified price observations are recorded (NULL over guess — no part
ships without dated observations).

## `error_codes_fixes_joined.csv` (479 rows)

Pre-joined view: every code with its ranked fix (LEFT JOIN, so codes without a
shipped fix appear once with NULL fix columns) plus `source_url` provenance.

## `brand_recalls.csv` (69 rows)

Appliance recalls affecting ApplianceDB brands, cross-referenced from the
sibling RecallDB corpus. Matching is word-boundary on brand (aliases handled,
e.g. GE / General Electric) plus an appliance term in the title; ambiguous
brand names (Candy, Hoover) match only CPSC laundry/dishwasher recalls.

| Column | Type | Description |
| :--- | :--- | :--- |
| `brand` | string | ApplianceDB brand the recall matches. |
| `agency` | string | Issuing agency (e.g., CPSC). |
| `recall_external_id` | string | Agency recall identifier. |
| `recall_date` | date | Date the recall was issued. |
| `title` | string | Recall title as recorded by RecallDB. |
| `severity` / `remedy` / `units_affected` | | Carried from the agency listing where stated. |
| `model_numbers` | string | Up to 10 recalled model numbers (semicolon-separated) — join against fleet data. |
| `matched_via` | enum | `product_brand_field` or `title_mention`. |
| `source_url` | url | The agency listing URL — RecallDB's provenance for this recall. |

## Controlled vocabulary — `cause_category`

`drainage`, `water_supply`, `sensor`, `motor`, `heating`, `door_lock`,
`compressor`, `defrost`, `fan`, `communication`, `power`, `ventilation`,
`leak`, `refrigerant`, `ice_maker`, `suds`, `unbalanced`, `dispenser`,
`temperature`, `filter`, `informational`.
