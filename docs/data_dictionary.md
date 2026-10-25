# Data dictionary

## Raw: `data/raw/transactions_2026-01-01_to_2026-10-25_SIMULATED.csv`
707 rows · 1 Jan – 25 Oct 2026 · one row per bank transaction · **simulated**.

| Column | Type | Meaning |
|---|---|---|
| transaction_id | text | Unique ID (T00001…) |
| date | date | Transaction date (YYYY-MM-DD) |
| time | text | Time (HH:MM, UK time) |
| bank_description | text | Raw text as a bank export shows it (e.g. `UBER *EATS`) |
| merchant | text | Clean merchant name |
| category | text | 16 spending categories + Income |
| subcategory | text | Detail within the category (e.g. Takeaway delivery, Top-up shop) |
| amount_gbp | number | Always positive; use `direction` for in or out |
| direction | text | Debit = money out, Credit = money in (income or refund) |
| payment_method | text | Apple Pay, Debit card, Direct debit, Standing order, Bank transfer, Cash |
| channel | text | In-store, Online, App |
| location | text | Town, Online or `-` |
| balance_gbp | number | Running balance after the transaction |

## Added by `scripts/enrich.py` (`data/processed/transactions_enriched.csv`)
| Column | Rule |
|---|---|
| hour | Hour from `time` |
| weekday, is_weekend | From `date` |
| month | YYYY-MM |
| time_band | Morning 05–12, Afternoon 12–17, Evening 17–22, Late night 22–05 |
| period | Internship (Jan–Jun) / After internship (Jul–Oct) |
| shift_day | Retail rota assumption: Sat & Sun during the internship; Wed, Fri, Sat & Sun from July; none after 21 Oct |
| days_since_payday | Days since the latest income row (blank before the first payday on 9 Jan) |
| spend_type | From `data/reference/spend_type_map.csv` (most specific rule wins). Override: a takeaway delivered after 21:00 on a shift day = Leakage. Credits = Income or Refund |
| signed_amount_gbp | Negative for money out, positive for money in |
| hours_of_work | amount ÷ £12.71 (UK National Living Wage from April 2026) |

## Known quirks
- **October is partial** (25 days) — compare spend per day, not monthly totals.
- **Subscriptions renew at ~04:30**, so they are excluded from time-of-day analysis (not a choice made at that hour).
- **Refunds** (5 ASOS credits) are netted off their category in the category totals.
