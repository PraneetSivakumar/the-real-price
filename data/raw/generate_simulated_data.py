"""Generate a SIMULATED personal bank statement (1 Jan - 25 Oct 2026) for Ace's
personal spending analysis project. Patterns are planted on purpose so the analysis has
real "why / when / how" stories to find. All amounts and merchants are fictional/simulated."""
import csv, random, sys
from datetime import date, datetime, timedelta

random.seed(2026)
START, END = date(2026, 1, 1), date(2026, 10, 25)
RETAIL_END = date(2026, 10, 21)   # last day at the retail job
OUT = sys.argv[1]
rows = []

def add(d, hh, mm, desc, merchant, cat, sub, amt, method, channel, loc, direction="Debit"):
    rows.append(dict(date=d, time=f"{hh:02d}:{mm:02d}", bank_description=desc, merchant=merchant,
                     category=cat, subcategory=sub, amount_gbp=round(amt, 2), direction=direction,
                     payment_method=method, channel=channel, location=loc))

def rt(a, b):  # random time between hours a and b
    h = random.randint(a, b - 1)
    return h, random.randint(0, 59)

def pair(d):
    k = random.choice(list(d)); return k, d[k]

def days():
    d = START
    while d <= END:
        yield d
        d += timedelta(days=1)

internship = lambda d: date(2026, 1, 1) <= d <= date(2026, 6, 30)
# Paydays
paydays = set()
for m in range(1, 7):
    paydays.add(date(2026, m, 28))
tesco_pay = []
p = date(2026, 1, 9)
while p <= RETAIL_END + timedelta(days=7):
    tesco_pay.append(p); p += timedelta(days=28)
paydays.update(tesco_pay)

def days_since_payday(d):
    past = [p for p in paydays if p <= d]
    return (d - max(past)).days if past else 99

for d in days():
    wd = d.weekday()  # 0 Mon .. 6 Sun
    m = d.month
    office_day = internship(d) and wd in (1, 3) and random.random() < 0.9   # hybrid: Tue/Thu
    shift_day = d <= RETAIL_END and ((internship(d) and wd in (5, 6)) or (not internship(d) and wd in (2, 4, 5, 6)))
    post_pay = days_since_payday(d) <= 3
    job_hunt = d >= date(2026, 6, 15)

    # ---------- Income ----------
    if internship(d) and d.day == 28:
        add(d, 6, 5, "FASTER PAYMENT RECEIVED PAYROLL - INTERNSHIP", "Internship payroll", "Income", "Salary",
            1840.00, "Bank transfer", "Online", "-", "Credit")
    if d in tesco_pay:
        amt = random.uniform(360, 410) if (d - timedelta(days=14)) <= date(2026, 6, 30) else random.uniform(1180, 1290)
        add(d, 6, 10, "FASTER PAYMENT RECEIVED PAYROLL - RETAIL JOB", "Retail job payroll", "Income", "Wages",
            amt, "Bank transfer", "Online", "-", "Credit")

    # ---------- Fixed monthly bills / subscriptions ----------
    if d.day == 1:
        add(d, 7, 0, "STANDING ORDER HOUSE SHARE RENT", "Landlord (house share)", "Housing & Bills", "Rent", 575.00, "Standing order", "Online", "Hatfield")
    if d.day == 3:
        add(d, 7, 2, "DD OCTOPUS ENERGY SHARE", "Energy & broadband share", "Housing & Bills", "Utilities", random.choice([58.0, 61.5, 64.0]) if m < 5 else random.choice([44.0, 47.5]), "Direct debit", "Online", "-")
    if d.day == 5:
        add(d, 7, 4, "DD GIFFGAFF", "giffgaff", "Housing & Bills", "Mobile", 12.00, "Direct debit", "Online", "-")
    if d.day == 7:
        add(d, 7, 6, "DD PUREGYM LTD", "PureGym", "Health & Fitness", "Gym membership", 24.99, "Direct debit", "Online", "Hatfield")
    subs = [(10, "NETFLIX.COM", "Netflix", 10.99), (12, "SPOTIFY UK", "Spotify", 12.99), (15, "AMAZON PRIME*UK", "Amazon Prime", 8.99),
            (18, "APPLE.COM/BILL ICLOUD", "Apple iCloud+", 2.99), (20, "GOOGLE *YOUTUBEPREMIUM", "YouTube Premium", 12.99),
            (22, "DISNEYPLUS", "Disney+", 5.99), (24, "GOOGLE ONE STORAGE", "Google One", 1.99)]
    for day_, desc, merch, price in subs:
        if d.day == day_:
            add(d, 4, 30, desc, merch, "Subscriptions", "Streaming & storage", price, "Debit card", "Online", "-")
    if d.day == 9 and d >= date(2026, 4, 1):
        add(d, 4, 31, "OPENAI *CHATGPT SUBSCR", "ChatGPT Plus", "Subscriptions", "AI tools", 20.00, "Debit card", "Online", "-")
    if d.day == 16 and d >= date(2026, 7, 1):
        add(d, 4, 32, "LINKEDIN PREMIUM CAREER", "LinkedIn Premium", "Subscriptions", "Career", 29.99, "Debit card", "Online", "-")

    # ---------- Commute (internship office days) ----------
    if office_day:
        add(d, 7, random.randint(5, 25), "TRAINLINE.COM", "Trainline", "Transport", "Train (commute)", random.choice([27.40, 28.90, 31.20]), "Apple Pay", "App", "Online")
        add(d, *rt(8, 9), "COSTA COFFEE MILTON KEYNES", "Costa Coffee", "Eating Out", "Coffee", random.choice([3.45, 3.65, 3.95]), "Apple Pay", "In-store", "Milton Keynes")
        if random.random() < 0.8:
            add(d, *rt(12, 14), *pair({"PRET A MANGER MK": "Pret A Manger", "GREGGS MILTON KEYNES": "Greggs", "TESCO EXPRESS MK": "Tesco Express"}), "Eating Out", "Lunch", random.uniform(4.2, 8.9), "Apple Pay", "In-store", "Milton Keynes")

    # ---------- Groceries ----------
    if wd == 6 or (wd == 0 and random.random() < 0.15):  # weekly shop
        store = random.choices(["ALDI STORES HATFIELD", "LIDL GB HATFIELD", "TESCO STORES HATFIELD"], [5, 2, 3])[0]
        name = {"ALDI STORES HATFIELD": "Aldi", "LIDL GB HATFIELD": "Lidl", "TESCO STORES HATFIELD": "Tesco"}[store]
        add(d, *rt(10, 13), store, name, "Groceries", "Weekly shop", random.uniform(24, 46), "Debit card", "In-store", "Hatfield")
    # top-up trips (convenience premium) - more on shift days and after payday
    if random.random() < (0.32 if shift_day else 0.18) + (0.10 if post_pay else 0):
        store = random.choice(["TESCO EXPRESS HATFIELD", "M&S SIMPLY FOOD HATFIELD", "SAINSBURYS LOCAL HATFIELD", "CO-OP GROUP HATFIELD"])
        name = {"TESCO EXPRESS HATFIELD": "Tesco Express", "M&S SIMPLY FOOD HATFIELD": "M&S Food", "SAINSBURYS LOCAL HATFIELD": "Sainsbury's Local", "CO-OP GROUP HATFIELD": "Co-op"}[store]
        add(d, *rt(16, 22), store, name, "Groceries", "Top-up shop", random.uniform(4.5, 16.5), "Apple Pay", "In-store", "Hatfield")

    # ---------- Takeaway / delivery: late night after shifts, payday spikes, rising with job hunt ----------
    p_take = 0.06 + (0.22 if shift_day else 0) + (0.15 if post_pay else 0) + (0.10 if job_hunt else 0) + (0.05 if wd in (4, 5) else 0)
    if random.random() < p_take:
        app = random.choices(["DELIVEROO.CO.UK", "UBER *EATS", "JUST EAT.CO.UK"], [4, 4, 2])[0]
        name = {"DELIVEROO.CO.UK": "Deliveroo", "UBER *EATS": "Uber Eats", "JUST EAT.CO.UK": "Just Eat"}[app]
        h = random.choice([21, 22, 22, 23, 23, 0]) if shift_day else random.choice([19, 20, 21])
        add(d, h, random.randint(0, 59), app, name, "Eating Out", "Takeaway delivery", random.uniform(14.5, 31.0), "Apple Pay", "App", "Hatfield")
    if random.random() < 0.10:
        add(d, *rt(12, 20), *pair({"NANDOS HATFIELD": "Nando's", "MCDONALDS HATFIELD": "McDonald's", "GREGGS HATFIELD": "Greggs", "WAGAMAMA ST ALBANS": "Wagamama"}), "Eating Out", "Restaurants & fast food", random.uniform(5.5, 24.0), "Apple Pay", "In-store", "Hatfield")

    # ---------- Protein & supplements ----------
    if d in (date(2026, 1, 5), date(2026, 10, 6), date(2026, 2, 9), date(2026, 3, 18), date(2026, 4, 27), date(2026, 6, 4), date(2026, 7, 14), date(2026, 8, 25)):
        add(d, *rt(20, 23), "MYPROTEIN.COM", "Myprotein", "Health & Fitness", "Protein (bulk online)", random.uniform(34, 56), "Debit card", "Online", "Online")
    if random.random() < 0.035:  # impulse small tubs at high unit price
        add(d, *rt(11, 19), "HOLLAND & BARRETT HATFIELD", "Holland & Barrett", "Health & Fitness", "Protein (small tub, in-store)", random.choice([18.99, 21.99, 24.99]), "Apple Pay", "In-store", "Hatfield")
    if random.random() < 0.08:
        add(d, *rt(10, 18), *pair({"BOOTS HATFIELD": "Boots", "TESCO EXPRESS HATFIELD": "Tesco Express"}),
            "Health & Fitness", "Protein bars & shakes", random.uniform(2.0, 6.5), "Apple Pay", "In-store", "Hatfield")

    # ---------- Men's skincare & body wash / toiletries ----------
    if random.random() < 0.045:
        add(d, *rt(11, 19), *pair({"BOOTS HATFIELD": "Boots", "SUPERDRUG HATFIELD": "Superdrug", "BOOTS.COM": "Boots"}),
            "Personal Care", "Men's skincare", random.uniform(8, 32), "Apple Pay", random.choice(["In-store", "Online"]), "Hatfield")
    if d == date(2026, 5, 30):
        add(d, 15, 12, "JOHN LEWIS SKINCARE WATFORD", "John Lewis", "Personal Care", "Men's skincare", 68.00, "Debit card", "In-store", "Watford")
    if random.random() < 0.04:
        add(d, *rt(10, 20), *pair({"SUPERDRUG HATFIELD": "Superdrug", "TESCO STORES HATFIELD": "Tesco", "BOOTS HATFIELD": "Boots"}),
            "Personal Care", "Body wash & toiletries", random.uniform(3.0, 9.5), "Apple Pay", "In-store", "Hatfield")
    if d.day in (14,) :
        add(d, *rt(10, 17), "MANE BARBERS HATFIELD", "Barber", "Personal Care", "Haircut", 15.00, "Apple Pay", "In-store", "Hatfield")

    # ---------- Clothing & shoes (late-night online impulse, payday) ----------
    if random.random() < 0.035 + (0.07 if post_pay else 0):
        late = random.random() < 0.55
        h = random.choice([23, 0, 1]) if late else random.randint(12, 19)
        shop = random.choices(["ASOS.COM", "PRIMARK HATFIELD", "H&M ONLINE", "UNIQLO LONDON", "ZARA.COM", "NEXT RETAIL"], [4, 3, 2, 1, 2, 1])[0]
        name = {"ASOS.COM": "ASOS", "PRIMARK HATFIELD": "Primark", "H&M ONLINE": "H&M", "UNIQLO LONDON": "Uniqlo", "ZARA.COM": "Zara", "NEXT RETAIL": "Next"}[shop]
        online = shop not in ("PRIMARK HATFIELD", "UNIQLO LONDON")
        if not online and h in (23, 0, 1): h = random.randint(12, 18)
        amt = random.uniform(14, 75)
        add(d, h, random.randint(0, 59), shop, name, "Clothing", "Clothing", amt, "Debit card" if online else "Apple Pay", "Online" if online else "In-store", "Online" if online else ("London" if "LONDON" in shop else "Hatfield"))
        if name == "ASOS" and random.random() < 0.45:  # some returned
            rd = d + timedelta(days=random.randint(8, 16))
            if rd <= END:
                add(rd, 9, random.randint(0, 59), "ASOS.COM REFUND", "ASOS", "Clothing", "Refund", round(amt * random.choice([1, 0.5]), 2), "Debit card", "Online", "Online", "Credit")
    for sd, desc, merch, sub, amt, chan, loc in [
        (date(2026, 2, 28), "NIKE.COM UK", "Nike", "Trainers", 94.99, "Online", "Online"),
        (date(2026, 4, 11), "SPORTS DIRECT HATFIELD", "Sports Direct", "Cricket shoes", 54.99, "In-store", "Hatfield"),
        (date(2026, 7, 3), "CLARKS SHOES LONDON", "Clarks", "Formal shoes (interviews)", 79.00, "In-store", "London"),
        (date(2026, 8, 29), "JD SPORTS FASHION", "JD Sports", "Trainers", 110.00, "Online", "Online")]:
        if d == sd:
            add(d, *rt(12, 23), desc, merch, "Shoes", sub, amt, "Debit card", chan, loc)
    if d in (date(2026, 1, 3), date(2026, 1, 4)):
        add(d, *rt(20, 24), "NEXT RETAIL JANUARY SALE" if d.day == 3 else "ASOS.COM", "Next" if d.day == 3 else "ASOS", "Clothing", "January sales", random.uniform(38, 70), "Debit card", "Online", "Online")
    if d == date(2026, 10, 18):
        add(d, 14, 20, "UNIQLO LONDON", "Uniqlo", "Clothing", "Winter jacket", 59.90, "Apple Pay", "In-store", "London")
    if d == date(2026, 7, 2):
        add(d, 14, 40, "M&S CLOTHING LONDON", "M&S", "Clothing", "Interview outfit", 89.00, "Debit card", "In-store", "London")

    # ---------- Cricket / hobbies ----------
    if d == date(2026, 4, 4):
        add(d, 10, 30, "HATFIELD CRICKET CLUB SUBS", "Cricket club", "Sport & Hobbies", "Club membership", 120.00, "Bank transfer", "Online", "Hatfield")
    if d == date(2026, 4, 18):
        add(d, 13, 5, "DECATHLON UK", "Decathlon", "Sport & Hobbies", "Cricket kit", 72.50, "Debit card", "In-store", "St Albans")
    if date(2026, 5, 1) <= d <= date(2026, 8, 31) and wd == 6 and random.random() < 0.7:
        add(d, 17, random.randint(0, 59), "HATFIELD CC MATCH FEE", "Cricket club", "Sport & Hobbies", "Match fees & teas", 6.00, "Apple Pay", "In-store", "Hatfield")

    # ---------- Social / entertainment / travel ----------
    if wd == 4 and random.random() < 0.35:
        add(d, *rt(19, 23), *pair({"THE RED LION HATFIELD": "The Red Lion (pub)", "WETHERSPOON ST ALBANS": "Wetherspoon", "ODEON CINEMAS": "Odeon"}),
            "Entertainment", "Social & cinema", random.uniform(8, 32), "Apple Pay", "In-store", "Hatfield")
    if random.random() < 0.025:
        add(d, *rt(19, 24), "STEAM GAMES", "Steam", "Entertainment", "Games", random.uniform(4.99, 39.99), "Debit card", "Online", "Online")
    if random.random() < 0.06:
        add(d, *rt(8, 22), *pair({"TFL TRAVEL CH": "TfL", "UBER *TRIP": "Uber", "GREAT NORTHERN": "Great Northern"}),
            "Transport", "Local & London travel", random.uniform(3.5, 19.0), "Apple Pay", "App", random.choice(["London", "Hatfield"]))
    if d == date(2026, 8, 14):
        add(d, 9, 15, "LNER TICKETS", "LNER", "Travel", "Weekend trip (Edinburgh)", 86.40, "Debit card", "Online", "Online")
    if d == date(2026, 8, 15):
        add(d, 16, 0, "PREMIER INN EDINBURGH", "Premier Inn", "Travel", "Weekend trip (Edinburgh)", 118.00, "Debit card", "Online", "Edinburgh")

    # ---------- Learning / career ----------
    for ld, desc, merch, sub, amt in [(date(2026, 3, 8), "UDEMY ONLINE COURSES", "Udemy", "Online course", 14.99),
                                       (date(2026, 7, 20), "WATERSTONES", "Waterstones", "Books", 24.98),
                                       (date(2026, 9, 6), "COURSERA", "Coursera", "Certificate", 39.00)]:
        if d == ld:
            add(d, *rt(18, 22), desc, merch, "Learning & Career", sub, amt, "Debit card", "Online", "Online")

    # ---------- Amazon misc, gifts, cash ----------
    if random.random() < 0.06 + (0.05 if post_pay else 0):
        add(d, *rt(18, 24), "AMZNMKTPLACE AMAZON.CO.UK", "Amazon", "Shopping (misc)", "Household & gadgets", random.uniform(6, 45), "Debit card", "Online", "Online")
    if d in (date(2026, 3, 22), date(2026, 6, 12), date(2026, 9, 18)):
        add(d, *rt(12, 19), "CARD FACTORY / GIFT", "Gifts", "Gifts", "Birthday gifts", random.uniform(18, 45), "Debit card", "In-store", "Hatfield")
    if random.random() < 0.03:
        add(d, *rt(10, 22), "CASH WITHDRAWAL LINK ATM", "Cash withdrawal", "Cash", "ATM", random.choice([20, 30, 40]), "Cash", "In-store", "Hatfield")

# ---- sort, running balance, ids, a few real-world messy bits ----
rows.sort(key=lambda r: (r["date"], r["time"]))
bal = 1600.00
out = []
for i, r in enumerate(rows, 1):
    bal += r["amount_gbp"] if r["direction"] == "Credit" else -r["amount_gbp"]
    r["balance_gbp"] = round(bal, 2)
    r["transaction_id"] = f"T{i:05d}"
    out.append(r)
    if bal < 0 and not any(x.get("_fee") == (r["date"].year, r["date"].month) for x in out):
        bal -= 6.00
        fee = dict(transaction_id="", date=r["date"], time="23:59", bank_description="OVERDRAFT USAGE FEE", merchant="Bank",
                   category="Bank fees", subcategory="Overdraft fee", amount_gbp=6.00, direction="Debit",
                   payment_method="Bank charge", channel="Online", location="-", balance_gbp=round(bal, 2), _fee=(r["date"].year, r["date"].month))
        out.append(fee)
for i, r in enumerate(out, 1):
    r["transaction_id"] = f"T{i:05d}"
    r.pop("_fee", None)

cols = ["transaction_id", "date", "time", "bank_description", "merchant", "category", "subcategory", "amount_gbp",
        "direction", "payment_method", "channel", "location", "balance_gbp"]
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in out:
        r = dict(r); r["date"] = r["date"].isoformat(); r["amount_gbp"] = f"{r['amount_gbp']:.2f}"; r["balance_gbp"] = f"{r['balance_gbp']:.2f}"
        w.writerow(r)
print(len(out), "rows; closing balance", round(bal, 2))
