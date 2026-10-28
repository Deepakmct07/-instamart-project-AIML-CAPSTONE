# Part B: Customer Segmentation (RFM + K-Means)
## What the code does
`rfm_kmeans.py` reads completed orders from `../part_a/data/instamart.db`, computes per customer Recency (days since last order, snapshot = day after the last order), Frequency (orders) and Monetary (INR spent), standardizes with `StandardScaler`, runs K-Means for K=2..8 recording inertia and silhouette, picks K with the best silhouette, names segments from the standardized centroids, and saves `rfm_segments` to the database. Customers with no completed order are labelled "No orders".
## Run
Run Part A first, then `python rfm_kmeans.py` (from `part_b/`).
Dependencies: `pandas numpy scikit-learn matplotlib`. No environment variables.
## Key findings
- Silhouette by K: 2 = 0.465, 3 = 0.445, **4 = 0.526**, 5 = 0.481, 6 = 0.482, 7 = 0.416, 8 = 0.412. K=4 is optimal; inertia keeps falling smoothly, so silhouette is the deciding metric.
- Segments (1,175 customers with orders; 25 have none):

| Segment | Avg recency (days) | Avg orders | Avg spend (INR) | Customers |
|---|---|---|---|---|
| Frequent regulars | 8.8 | 19.4 | 3,410 | 419 |
| High-value spenders | 24.1 | 6.8 | 7,130 | 138 |
| Occasional buyers | 28.9 | 3.8 | 1,058 | 436 |
| At-risk (lapsing) | 109.0 | 2.2 | 686 | 182 |

- The At-risk group (not ordering for about 3.5 months) is the retention team's target list.
- Plots: `outputs/kmeans.png` (elbow, silhouette, PCA cluster view); tables: `outputs/kmeans_metrics.csv`, `outputs/segment_profile.csv`.
