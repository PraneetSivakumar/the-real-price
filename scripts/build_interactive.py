"""Builds dashboard/the_real_price_interactive.html - the interactive dashboard.

Embeds the enriched data as JSON into scripts/interactive_template.html, so the page works
offline and on GitHub Pages with no server and no external libraries.
Run from the project root:  python3 scripts/build_interactive.py
"""
import json

import pandas as pd

df = pd.read_csv("data/processed/transactions_enriched.csv")
m = json.load(open("dashboard/metrics.json"))

keys = ["date", "time", "merchant", "category", "subcategory", "amount", "direction",
        "payment_method", "channel", "spend_type", "shift_day", "period", "hour"]
tx = []
for r in df.itertuples():
    tx.append([r.date, r.time, r.merchant, r.category, r.subcategory, round(r.amount_gbp, 2), r.direction,
               r.payment_method, r.channel, r.spend_type, int(bool(r.shift_day)),
               0 if r.period.startswith("Internship") else 1, int(r.hour)])

balance = df.groupby("date").balance_gbp.last().round(2)
sp = df[df.direction == "Debit"]
after = sp[sp.period == "After internship (Jul-Oct)"]
late = (after.hour >= 21) | (after.hour < 5)
lt = after[(after.subcategory == "Takeaway delivery") & after.shift_day & late]
base = {
    "late_take_spend": round(lt.amount_gbp.sum(), 2), "late_take_orders": int(len(lt)),
    "topup_spend": round(after[after.subcategory == "Top-up shop"].amount_gbp.sum(), 2),
    "late_online": round(after[after.channel.isin(["Online", "App"]) & ((after.hour >= 22) | (after.hour < 5))
                               & after.category.isin(["Clothing", "Shopping (misc)", "Entertainment"])].amount_gbp.sum(), 2),
    "tub_spend": round(sp[sp.subcategory == "Protein (small tub, in-store)"].amount_gbp.sum(), 2),
    "zombie_monthly": 7.98,
    "bulk_ratio": round(m["protein_per_20g"]["Protein (bulk online)"] / m["protein_per_20g"]["Protein (small tub, in-store)"], 3),
    "days_after": 117, "days_total": 298,
}
data = {
    "keys": keys, "tx": tx,
    "balance": [[d, b] for d, b in balance.items()],
    "endBalance": m["end_balance"], "netPerDay": m["runway"]["net_per_day"],
    "lastDate": "2026-10-25", "wage": 12.71, "base": base,
    "payday": m["payday"],
}
tpl = open("scripts/interactive_template.html").read()
out = tpl.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
open("dashboard/the_real_price_interactive.html", "w").write(out)
print("dashboard/the_real_price_interactive.html written,", len(out) // 1024, "KB")
