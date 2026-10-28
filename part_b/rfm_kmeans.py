"""Part B: RFM + K-Means (K=2..8) + silhouette selection. Run Part A first."""
from pathlib import Path
import sqlite3, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
HERE = Path(__file__).resolve().parent; OUT = HERE/"outputs"; OUT.mkdir(exist_ok=True)
con = sqlite3.connect(HERE.parent/"part_a/data/instamart.db")
od = pd.read_sql("SELECT customer_id, order_id, order_ts, order_amount FROM orders WHERE status='completed'", con, parse_dates=["order_ts"])
n_all = pd.read_sql("SELECT COUNT(*) n FROM customers", con).n[0]
ref = od.order_ts.max().normalize() + pd.Timedelta(days=1)         # snapshot date = day after last order
rfm = od.groupby("customer_id").agg(Recency=("order_ts", lambda s: (ref - s.max()).days),
                                    Frequency=("order_id", "nunique"), Monetary=("order_amount", "sum")).reset_index()
print(f"customers with >=1 completed order: {len(rfm)} / {n_all}  (others have no RFM and are labelled 'No orders')")
X = StandardScaler().fit_transform(rfm[["Recency", "Frequency", "Monetary"]])
rows = []
for k in range(2, 9):
    km = KMeans(k, n_init=10, random_state=42).fit(X)
    rows.append((k, km.inertia_, silhouette_score(X, km.labels_)))
res = pd.DataFrame(rows, columns=["K", "inertia", "silhouette"]); print(res.round(4).to_string(index=False))
res.to_csv(OUT/"kmeans_metrics.csv", index=False)
best = int(res.loc[res.silhouette.idxmax(), "K"]); print("Optimal K (max silhouette):", best)
km = KMeans(best, n_init=10, random_state=42).fit(X); rfm["cluster"] = km.labels_
cz = pd.DataFrame(km.cluster_centers_, columns=["R", "F", "M"])     # centroids in standardized units
def label(r):
    if r.M > .5 and r.F > .5: return "Champions (high spend, frequent)"
    if r.M > .5: return "High-value spenders"
    if r.F > .3: return "Frequent regulars"
    if r.R > .3: return "At-risk (lapsing, not ordered recently)"
    return "Occasional buyers"
names = cz.apply(label, axis=1); dup = names[names.duplicated(keep=False)]
names[dup.index] = [f"{n} (C{i})" for i, n in dup.items()]
rfm["segment"] = rfm.cluster.map(names)
prof = rfm.groupby("segment")[["Recency", "Frequency", "Monetary"]].mean().round(1)
prof["customers"] = rfm.segment.value_counts(); print(prof.to_string())
allc = pd.read_sql("SELECT customer_id FROM customers", con).merge(rfm, how="left", on="customer_id")
allc["segment"] = allc.segment.fillna("No orders")
allc.to_sql("rfm_segments", con, if_exists="replace", index=False); prof.to_csv(OUT/"segment_profile.csv")
fig, ax = plt.subplots(1, 3, figsize=(17, 4.5))
ax[0].plot(res.K, res.inertia, "o-"); ax[0].set(title="Elbow: inertia vs K", xlabel="K")
ax[1].plot(res.K, res.silhouette, "o-r"); ax[1].axvline(best, ls="--"); ax[1].set(title="Silhouette vs K", xlabel="K")
p = PCA(2).fit_transform(X)
for c in sorted(rfm.cluster.unique()): m = rfm.cluster == c; ax[2].scatter(p[m, 0], p[m, 1], s=10, label=names[c])
ax[2].legend(fontsize=7); ax[2].set_title(f"Segments (K={best}, PCA view)")
plt.tight_layout(); plt.savefig(OUT/"kmeans.png", dpi=120); print("saved outputs/kmeans.png")
