"""Phase 2 - Feature engineering.

Reads the raw (SIMULATED) bank statement and adds the columns the analysis needs:
weekday, hour, time_band, month, period, shift_day, days_since_payday, spend_type and
hours_of_work. Raw data is never edited - the output goes to data/processed/.

Run from the project root:  python3 scripts/enrich.py
"""
from datetime import date

import pandas as pd

RAW = "data/raw/transactions_2026-01-01_to_2026-10-25_SIMULATED.csv"
MAP = "data/reference/spend_type_map.csv"
OUT = "data/processed/transactions_enriched.csv"

# Assumptions (documented in docs/data_dictionary.md)
HOURLY_WAGE = 12.71                     # UK National Living Wage from April 2026, used to convert £ into hours of work
INTERNSHIP_END = pd.Timestamp("2026-06-30")
RETAIL_END = pd.Timestamp("2026-10-21")  # last day of the retail job


def time_band(hour: int) -> str:
    if 5 <= hour < 12:
        return "Morning (05-12)"
    if 12 <= hour < 17:
        return "Afternoon (12-17)"
    if 17 <= hour < 22:
        return "Evening (17-22)"
    return "Late night (22-05)"


def is_shift_day(d: pd.Timestamp) -> bool:
    """Retail rota: weekends during the internship, Wed/Fri/Sat/Sun after it, none after the job ended."""
    if d > RETAIL_END:
        return False
    if d <= INTERNSHIP_END:
        return d.weekday() in (5, 6)
    return d.weekday() in (2, 4, 5, 6)


def main() -> None:
    df = pd.read_csv(RAW, parse_dates=["date"])
    df["amount_gbp"] = df["amount_gbp"].astype(float)

    # Basic data checks - stop if the raw file is broken
    assert df["transaction_id"].is_unique, "duplicate transaction ids"
    assert df.notna().all().all(), "blank cells in raw data"
    assert set(df["direction"]) <= {"Debit", "Credit"}

    hhmm = df["time"].str.split(":", expand=True).astype(int)
    df["hour"] = hhmm[0]
    df["weekday"] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.weekday >= 5
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df["time_band"] = df["hour"].apply(time_band)
    df["period"] = df["date"].apply(lambda d: "Internship (Jan-Jun)" if d <= INTERNSHIP_END else "After internship (Jul-Oct)")
    df["shift_day"] = df["date"].apply(is_shift_day)

    # Days since the most recent payday (paydays are taken from the income rows, not hard-coded)
    paydays = sorted(df.loc[(df["direction"] == "Credit") & (df["category"] == "Income"), "date"].unique())
    def days_since(d):
        past = [p for p in paydays if p <= d]
        return (d - past[-1]).days if past else None
    df["days_since_payday"] = df["date"].apply(days_since)

    # Spend type: most specific mapping rule wins (merchant > subcategory > category)
    m = pd.read_csv(MAP)
    def spend_type(row):
        if row["direction"] == "Credit":
            return "Income" if row["category"] == "Income" else "Refund"
        for cat, sub, merch in [(row.category, row.subcategory, row.merchant),
                                (row.category, row.subcategory, "*"),
                                (row.category, "*", "*")]:
            hit = m[(m.category == cat) & (m.subcategory == sub) & (m.merchant == merch)]
            if len(hit):
                return hit.iloc[0]["spend_type"]
        return "Unmapped"
    df["spend_type"] = df.apply(spend_type, axis=1)

    # Rule: a takeaway delivered after 21:00 on a shift day counts as Leakage (tired-and-hungry spending)
    late_take = (df["subcategory"] == "Takeaway delivery") & df["shift_day"] & ((df["hour"] >= 21) | (df["hour"] < 5))
    df.loc[late_take, "spend_type"] = "Leakage"
    assert (df["spend_type"] != "Unmapped").all(), df.loc[df["spend_type"] == "Unmapped", ["category", "subcategory"]]

    # Signed amount (spending negative, money in positive) and the headline metric: hours of work
    df["signed_amount_gbp"] = df.apply(lambda r: r.amount_gbp if r.direction == "Credit" else -r.amount_gbp, axis=1)
    df["hours_of_work"] = (df["amount_gbp"] / HOURLY_WAGE).round(2)

    df["date"] = df["date"].dt.date
    df.to_csv(OUT, index=False)
    print(f"{len(df)} rows -> {OUT}")
    print(df["spend_type"].value_counts().to_string())


if __name__ == "__main__":
    main()
