"""Part A: EDA, cleaning, SQLite load and Pandas-vs-SQL validation (Instamart data).
Run from this folder after generate_data.py."""
from pathlib import Path
import sqlite3, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent
RAW, CLEAN, OUT = HERE/"data/raw", HERE/"data/clean", HERE/"outputs"
CLEAN.mkdir(parents=True, exist_ok=True); OUT.mkdir(exist_ok=True)
cu, pr, od, tk = (pd.read_csv(RAW/f"{n}.csv") for n in ["customers", "products", "orders", "tickets"])

# ---------- 1. Explore ----------
for n, df in [("customers", cu), ("products", pr), ("orders", od), ("tickets", tk)]:
    print(f"\n== {n} {df.shape} =="); print("dtypes:", df.dtypes.astype(str).to_dict())
    print("nulls:", df.isna().sum()[lambda s: s > 0].to_dict()); print("unique:", df.nunique().to_dict())
print("\nraw city values:", sorted(cu.city.unique())); print("raw gender values:", sorted(cu.gender.dropna().unique()))
print("raw order statuses:", od.status.value_counts().to_dict())
log = {}

# ---------- 2. Customers ----------
cu = cu.drop_duplicates()
cu["city"] = cu.city.str.strip().str.title()                      # " chennai ", "CHENNAI" -> "Chennai"
gmap = {"male": "Male", "m": "Male", "female": "Female", "f": "Female"}
cu["gender"] = cu.gender.fillna("").str.strip().str.lower().map(gmap).fillna("Unknown")
cu["age"] = pd.to_numeric(cu.age, errors="coerce")
bad_age = (cu.age < 10) | (cu.age > 100)                          # 280, -4, 0, 150, 999, 200 are impossible
log["impossible_ages_set_null"] = int(bad_age.sum()); cu.loc[bad_age, "age"] = np.nan
log["missing_age_total"] = int(cu.age.isna().sum())
cu["signup_date"] = pd.to_datetime(cu.signup_date)

# ---------- 3. Orders ----------
log["exact_duplicate_rows"] = int(od.duplicated().sum()); od = od.drop_duplicates()
od["order_ts"] = pd.to_datetime(od.order_ts)
# partial duplicates: an earlier 'pending' row for the same order_id -> keep the latest record
log["order_ids_with_multiple_rows"] = int(od.order_id.duplicated().sum())
od = od.sort_values("order_ts").drop_duplicates("order_id", keep="last")
assert (od.status != "pending").all(), "a pending row survived"
# unparseable amounts ("N/A", "error") -> recompute from product price, quantity and discount
od["order_amount"] = pd.to_numeric(od.order_amount, errors="coerce")
od = od.merge(pr[["product_id", "price_inr"]], on="product_id", how="left")
fix = od.order_amount.isna(); log["amounts_recomputed"] = int(fix.sum())
od.loc[fix, "order_amount"] = (od.price_inr * od.quantity * (1 - od.discount_pct / 100)).round(2)
od = od.drop(columns="price_inr")
# delivery minutes: negatives / >120 are impossible -> NaN; blanks stay NaN (unknown)
od["delivery_minutes"] = pd.to_numeric(od.delivery_minutes, errors="coerce")
bad_d = (od.delivery_minutes <= 0) | (od.delivery_minutes > 120)
log["impossible_delivery_set_null"] = int(bad_d.sum()); od.loc[bad_d, "delivery_minutes"] = np.nan
od = od[od.customer_id.isin(cu.customer_id)].sort_values("order_id").reset_index(drop=True)

# ---------- 4. Tickets (kept as-is; empty/long ones must be blocked by Part C guardrails) ----------
tk = tk.fillna("")
log["empty_tickets_kept_for_guardrails"] = int((tk.text.str.strip() == "").sum())
print("\nCLEANING LOG:", log)

# ---------- 5. SQLite + validation ----------
db = HERE/"data/instamart.db"; con = sqlite3.connect(db)
for name, df in [("customers", cu), ("products", pr), ("orders", od), ("tickets", tk)]:
    df.to_sql(name, con, if_exists="replace", index=False); df.to_csv(CLEAN/f"{name}.csv", index=False)
    n = pd.read_sql(f"SELECT COUNT(*) n FROM {name}", con).n[0]; assert n == len(df); print(f"OK rows {name}: pandas={len(df)} sql={n}")
s = pd.read_sql("SELECT city, COUNT(*) n FROM customers GROUP BY city", con).set_index("city").n.sort_index()
assert (s == cu.city.value_counts().sort_index()).all(); print("OK city counts match:", s.to_dict())
g = pd.read_sql("SELECT gender, COUNT(*) n FROM customers GROUP BY gender", con).set_index("gender").n.sort_index()
assert (g == cu.gender.value_counts().sort_index()).all(); print("OK gender counts match:", g.to_dict())
r = pd.read_sql("SELECT ROUND(SUM(order_amount),2) r FROM orders WHERE status='completed'", con).r[0]
assert abs(r - round(od[od.status == "completed"].order_amount.sum(), 2)) < 0.01; print("OK completed revenue:", r)
st = pd.read_sql("SELECT status, COUNT(*) n FROM orders GROUP BY status", con).set_index("status").n.sort_index()
assert (st == od.status.value_counts().sort_index()).all(); print("OK status counts:", st.to_dict())
assert pd.read_sql("SELECT COUNT(*) n FROM (SELECT order_id FROM orders GROUP BY order_id HAVING COUNT(*)>1)", con).n[0] == 0
print("OK no duplicate order_id in SQL")

# ---------- 6. Plots ----------
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
cu.city.value_counts().plot.bar(ax=ax[0, 0], title="Customers by city (standardized)")
cu.gender.value_counts().plot.bar(ax=ax[0, 1], title="Gender (standardized)")
cu.age.plot.hist(bins=20, ax=ax[0, 2], title="Age (impossible values removed)")
od.order_amount.plot.hist(bins=40, ax=ax[1, 0], title="Order amount (INR)")
od.delivery_minutes.dropna().plot.hist(bins=30, ax=ax[1, 1], title="Delivery minutes"); ax[1, 1].axvline(45, color="r", ls="--")
od.status.value_counts().plot.bar(ax=ax[1, 2], title="Order status")
plt.tight_layout(); plt.savefig(OUT/"eda.png", dpi=120); print("saved outputs/eda.png")
