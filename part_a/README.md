# Part A: Data Preparation & EDA
## What the code does
- `generate_data.py` (course-provided, unchanged) writes `data/raw/*.csv` and `data/policies/*.txt`.
- `clean_eda.py` explores shape, dtypes, nulls and unique counts, cleans the data, loads SQLite `data/instamart.db`, validates Pandas vs SQL and saves `outputs/eda.png`.

| Problem found | Fix |
|---|---|
| City written as `chennai`, `CHENNAI`, ` Chennai ` | `strip().title()` |
| Gender `M/m/male/MALE/F/...` and blanks | Mapped to Male / Female / Unknown |
| Impossible ages (280, -4, 0, 150, 999, 200) and missing ages | Impossible set to NaN (kept as missing, not guessed) |
| Exact duplicate order rows | Dropped |
| Earlier `pending` row for the same `order_id` | Kept the latest row per `order_id` (asserted no pending remain) |
| Unparseable `order_amount` (`N/A`, `error`) | Recomputed as price x quantity x (1 - discount) from `products` |
| Negative `delivery_minutes` | Set to NaN; blanks stay NaN (unknown) |
| Empty and very long tickets | Left in place on purpose; Part C guardrails block them |

## Run
```bash
cd part_a
python generate_data.py
python clean_eda.py
```
Dependencies: `pandas numpy matplotlib` (sqlite3 is built in). No environment variables.
## Key findings
- 1,200 customers, 40 products, 12,309 orders after cleaning (from 13,084 raw rows), 164 tickets.
- Removed 119 exact duplicates and 656 superseded pending rows; recomputed 112 bad amounts; nulled 105 impossible delivery times and 6 impossible ages.
- SQL validation passes: row counts, per-city counts, gender counts, status counts, completed revenue (INR 2,998,668.80) and no duplicate `order_id`.
- Plots: `outputs/eda.png`.
