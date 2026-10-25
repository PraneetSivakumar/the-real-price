"""Phase 7 - builds dashboard/spending_wrapped.html, a Spotify-Wrapped-style story of the analysis.

Reads dashboard/metrics.json (written by notebooks/01_analysis.ipynb) and the enriched data,
so every number on the page comes from the analysis. Run from the project root:
    python3 scripts/build_wrapped.py
"""
import json
from html import escape

import pandas as pd

WAGE = 12.71
m = json.load(open("dashboard/metrics.json"))
df = pd.read_csv("data/processed/transactions_enriched.csv")
spend = df[df.direction == "Debit"]
refunds = df[(df.direction == "Credit") & (df.category != "Income")]
net = spend.groupby("category").amount_gbp.sum().sub(refunds.groupby("category").amount_gbp.sum(), fill_value=0)
housing = net["Housing & Bills"]
net = net.drop("Housing & Bills").sort_values(ascending=False).head(6)


def bars(series, fmt=lambda v: f"£{v:,.0f}", colour="#ff6b6b"):
    top = series.max()
    out = []
    for label, v in series.items():
        out.append(f'<div class="bar"><span class="lbl">{escape(str(label))}</span>'
                   f'<span class="track"><span class="fill" style="width:{100*v/top:.0f}%;background:{colour}"></span></span>'
                   f'<span class="val">{fmt(v)}</span></div>')
    return "\n".join(out)


st = m["spend_type"]
st_total = sum(st.values())
st_cols = {"Essential": "#3ddc97", "Investment": "#5fa8ff", "Lifestyle": "#ffd166", "Leakage": "#ff6b6b"}
st_strip = "".join(f'<span style="flex:{v};background:{st_cols[k]}" title="{k}"></span>' for k, v in st.items())
st_legend = "".join(f'<li><i style="background:{st_cols[k]}"></i>{k} <b>£{v:,.0f}</b> ({100*v/st_total:.0f}%)</li>' for k, v in st.items())
plan_rows = "".join(f'<tr><td>{escape(r["rule"])}</td><td>£{r["by_31_dec"]:,.0f}</td><td>£{r["per_year"]:,.0f}</td><td>{r["hours_per_year"]:.0f} h</td></tr>' for r in m["plan"])
tm = m["top_merchants"][0]
hh = m["hours_headlines"]
pay = m["payday"]
run = m["runway"]
nice = lambda iso: pd.Timestamp(iso).strftime('%-d %b %Y')
h = m["most_expensive_hour"]

slides = [
    ("#1b1464", "#7a1fa2", f"""<p class="kicker">Your 2026 in money · 1 Jan – 25 Oct</p>
<h1>£{m['total_spend']:,.0f}</h1>
<p class="big">That's <b>{m['total_hours']:,.0f} hours</b> of work at £{WAGE}/hour —<br>about <b>{m['total_hours']/7.5:,.0f} full shifts</b>.</p>"""),
    ("#0b3d2e", "#1d7a55", f"""<p class="kicker">Where it went (excluding rent &amp; bills)</p>
<h2>Your top categories</h2>{bars(net)}
<p class="note">Rent &amp; bills took another £{housing:,.0f} ({housing/WAGE:,.0f} hours).</p>"""),
    ("#3d0b0b", "#a2321f", f"""<p class="kicker">Your top merchant</p>
<h1>{escape(tm['merchant'])}</h1>
<p class="big">{tm['count']} payments · <b>£{tm['spend']:,.0f}</b> · {tm['spend']/WAGE:,.0f} hours</p>
<p class="note">Runners-up: {', '.join(escape(x['merchant']) for x in m['top_merchants'][1:4])}.</p>"""),
    ("#101b3d", "#2f4fa8", f"""<p class="kicker">Your most expensive hour</p>
<h1>{h:02d}:00</h1>
<p class="big">And after 22:00 you spent <b>£{m['late_night_spend']:,.0f}</b> —<br>the <b>late-night tax</b>: {hh['Late-night spending']:,.0f} hours of work.</p>"""),
    ("#3d2a00", "#b87900", f"""<p class="kicker">The payday effect</p>
<h1>{pay['ratio']:.1f}×</h1>
<p class="big">In the 3 days after payday you spent <b>£{pay['post_per_day']:.2f}/day</b><br>vs <b>£{pay['rest_per_day']:.2f}/day</b> the rest of the month.</p>
<p class="note">Permutation test: a gap this big happens by chance {pay['p_value']*100:.2f}% of the time.</p>"""),
    ("#2a0b3d", "#8a2fa8", f"""<p class="kicker">The after-shift takeaway</p>
<h1>{m['takeaway']['late_shift_orders']} orders</h1>
<p class="big">Every one of them after 21:00 on a shift day:<br><b>£{m['takeaway']['late_shift_spend']:,.0f}</b> = {hh['Takeaways after shifts']:,.0f} hours — you worked {hh['Takeaways after shifts']/7.5:.1f} shifts to pay for being too tired to cook.</p>"""),
    ("#0b2a3d", "#1f7aa2", f"""<p class="kicker">Your spending personality</p>
<h2>Essential · Investment · Lifestyle · Leakage</h2>
<div class="strip">{st_strip}</div><ul class="legend">{st_legend}</ul>
<p class="note">Income fell {m['income_drop_pct']:.0f}% after the internship. Spending fell only {m['spend_drop_pct']:.0f}%.</p>"""),
    ("#0b3d1f", "#2fa85a", f"""<p class="kicker">The plan</p>
<h2>5 rules · £{m['plan_total_year']:,.0f} a year · {m['plan_total_year']/WAGE:,.0f} hours back</h2>
<table><tr><th>Rule</th><th>by 31 Dec</th><th>per year</th><th>hours</th></tr>{plan_rows}</table>
<p class="note">Savings runway: at today's rate the balance reaches £0 around <b>{nice(run['zero_date'])}</b>; with the plan, around <b>{nice(run['zero_date_with_plan'])}</b>. The real fix is income — the job search.</p>"""),
]

sections = "\n".join(f'<section style="background:linear-gradient(135deg,{a},{b})"><div class="card">{body}<p class="page">{i+1} / {len(slides)}</p></div></section>'
                     for i, (a, b, body) in enumerate(slides))

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spending Wrapped 2026</title>
<style>
:root {{ color-scheme: dark; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-snap-type: y mandatory; }}
body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #fff; background: #111; }}
section {{ min-height: 100vh; scroll-snap-align: start; display: flex; align-items: center; justify-content: center; padding: 24px 16px; }}
.card {{ width: 100%; max-width: 720px; }}
.kicker {{ text-transform: uppercase; letter-spacing: .14em; font-size: .8rem; opacity: .8; margin-bottom: 12px; }}
h1 {{ font-size: clamp(3rem, 12vw, 6.5rem); line-height: 1; font-weight: 800; margin-bottom: 18px; }}
h2 {{ font-size: clamp(1.4rem, 4.5vw, 2.2rem); margin-bottom: 18px; }}
.big {{ font-size: clamp(1.1rem, 3.6vw, 1.5rem); line-height: 1.45; }}
.note {{ margin-top: 18px; opacity: .8; font-size: .95rem; line-height: 1.5; }}
.page {{ margin-top: 28px; font-size: .75rem; opacity: .5; }}
.bar {{ display: grid; grid-template-columns: 130px 1fr 70px; gap: 10px; align-items: center; margin: 8px 0; font-size: .95rem; }}
.track {{ background: rgba(255,255,255,.12); border-radius: 6px; height: 14px; overflow: hidden; }}
.fill {{ display: block; height: 100%; border-radius: 6px; }}
.val {{ text-align: right; font-variant-numeric: tabular-nums; }}
.strip {{ display: flex; height: 28px; border-radius: 8px; overflow: hidden; margin: 8px 0 14px; }}
.legend {{ list-style: none; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: .95rem; }}
.legend i {{ display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 8px; vertical-align: -1px; }}
table {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
th, td {{ text-align: left; padding: 7px 6px; border-bottom: 1px solid rgba(255,255,255,.18); vertical-align: top; }}
th:not(:first-child), td:not(:first-child) {{ text-align: right; white-space: nowrap; }}
footer {{ text-align: center; padding: 20px 16px; font-size: .8rem; opacity: .6; background: #111; }}
@media (max-width: 520px) {{ .bar {{ grid-template-columns: 96px 1fr 58px; font-size: .85rem; }} .legend {{ grid-template-columns: 1fr; }} th, td {{ font-size: .8rem; }} }}
</style></head>
<body>
{sections}
<footer>The Real Price · Spending Wrapped 2026 · built on <b>simulated</b> data modelled on my lifestyle · Praneet Sivakumar</footer>
</body></html>"""

open("dashboard/spending_wrapped.html", "w").write(html)
print("dashboard/spending_wrapped.html written")
