"""
run_analysis.py
Customer Segmentation Analysis — Main Execution Script
Loads data → runs SQL queries → generates all charts → saves to outputs/
"""

import os
import sqlite3
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH    = os.path.join(BASE_DIR, "data", "customers.csv")
OUTPUTS_DIR  = os.path.join(BASE_DIR, "outputs")
CHARTS_DIR   = os.path.join(OUTPUTS_DIR, "charts")
DB_PATH      = os.path.join(OUTPUTS_DIR, "customers.db")

os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Palette & Style ────────────────────────────────────────────────────────
PALETTE = {
    "Premium":  "#1A1A2E",
    "Loyal":    "#16213E",
    "Regular":  "#0F3460",
    "New":      "#533483",
    "Budget":   "#E94560",
    "At-Risk":  "#F5A623",
}
TIER_ORDER  = ["Premium", "Loyal", "Regular", "New", "Budget", "At-Risk"]
TIER_COLORS = [PALETTE[t] for t in TIER_ORDER]

sns.set_theme(style="whitegrid", font="DejaVu Sans")
plt.rcParams.update({
    "figure.dpi":        150,
    "savefig.dpi":       150,
    "savefig.bbox":      "tight",
    "savefig.facecolor": "white",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.size":         10,
})

# ── Load Data ──────────────────────────────────────────────────────────────
print("📂  Loading dataset …")
df = pd.read_csv(DATA_PATH, parse_dates=["join_date", "last_purchase_date"])
print(f"    {len(df):,} customers loaded")

# ── SQLite ─────────────────────────────────────────────────────────────────
print("🗄   Building SQLite database …")
conn = sqlite3.connect(DB_PATH)
df.to_sql("customers", conn, if_exists="replace", index=False)
conn.commit()

# ── Helper ─────────────────────────────────────────────────────────────────
def q(sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)

def save(fig, name: str):
    path = os.path.join(CHARTS_DIR, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"    ✅  {name}")

# ══════════════════════════════════════════════════════════════════════════
# CHART 1 — Customer Tier Distribution (Donut)
# ══════════════════════════════════════════════════════════════════════════
print("\n📊  Generating charts …")

tier_counts = q("""
    SELECT customer_tier, COUNT(*) AS cnt
    FROM customers
    GROUP BY customer_tier
    ORDER BY cnt DESC
""")

fig, ax = plt.subplots(figsize=(7, 7))
explode = [0.03] * len(tier_counts)
colors  = [PALETTE.get(t, "#888") for t in tier_counts["customer_tier"]]
wedges, texts, autotexts = ax.pie(
    tier_counts["cnt"],
    labels=None,
    autopct="%1.1f%%",
    startangle=140,
    pctdistance=0.78,
    explode=explode,
    colors=colors,
    wedgeprops={"linewidth": 2, "edgecolor": "white"},
)
for at in autotexts:
    at.set(color="white", fontweight="bold", fontsize=9)

# Donut hole
circle = plt.Circle((0, 0), 0.55, color="white")
ax.add_patch(circle)
ax.text(0, 0.07, "500", ha="center", va="center", fontsize=22, fontweight="bold", color="#1A1A2E")
ax.text(0, -0.13, "Customers", ha="center", va="center", fontsize=11, color="#666")

legend_patches = [
    mpatches.Patch(color=PALETTE.get(row["customer_tier"], "#888"),
                   label=f'{row["customer_tier"]}  ({row["cnt"]})')
    for _, row in tier_counts.iterrows()
]
ax.legend(handles=legend_patches, loc="lower center", bbox_to_anchor=(0.5, -0.08),
          ncol=3, frameon=False, fontsize=9)
ax.set_title("Customer Tier Distribution", fontsize=14, fontweight="bold", pad=20)
save(fig, "01_customer_tier_distribution.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 2 — Average Lifetime Value by Tier (Horizontal Bar)
# ══════════════════════════════════════════════════════════════════════════
clv = q("""
    SELECT customer_tier,
           ROUND(AVG(total_spent),2) AS avg_clv,
           ROUND(SUM(total_spent),2) AS total_rev
    FROM customers
    GROUP BY customer_tier
    ORDER BY avg_clv DESC
""")

fig, ax = plt.subplots(figsize=(9, 5))
colors = [PALETTE.get(t, "#888") for t in clv["customer_tier"]]
bars = ax.barh(clv["customer_tier"], clv["avg_clv"], color=colors, height=0.55,
               edgecolor="white", linewidth=0.5)
for bar, val in zip(bars, clv["avg_clv"]):
    ax.text(bar.get_width() + 80, bar.get_y() + bar.get_height() / 2,
            f"${val:,.0f}", va="center", fontsize=9, color="#333")
ax.set_xlabel("Average Customer Lifetime Value (USD)", fontsize=10)
ax.set_title("Average Lifetime Value by Customer Tier", fontsize=14, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.invert_yaxis()
ax.set_xlim(0, clv["avg_clv"].max() * 1.2)
save(fig, "02_avg_lifetime_value_by_tier.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 3 — Revenue Share by Tier (Stacked / Pareto)
# ══════════════════════════════════════════════════════════════════════════
rev_share = q("""
    SELECT customer_tier,
           COUNT(*) AS cnt,
           ROUND(SUM(total_spent),2) AS revenue
    FROM customers
    GROUP BY customer_tier
    ORDER BY revenue DESC
""")
rev_share["revenue_pct"]   = 100 * rev_share["revenue"] / rev_share["revenue"].sum()
rev_share["customer_pct"]  = 100 * rev_share["cnt"]     / rev_share["cnt"].sum()

x = np.arange(len(rev_share))
w = 0.35
fig, ax = plt.subplots(figsize=(10, 5))
b1 = ax.bar(x - w/2, rev_share["revenue_pct"], width=w,
            color=[PALETTE.get(t, "#888") for t in rev_share["customer_tier"]],
            label="Revenue %", edgecolor="white")
b2 = ax.bar(x + w/2, rev_share["customer_pct"], width=w,
            color=[PALETTE.get(t, "#888") + "88" for t in rev_share["customer_tier"]],
            label="Customer %", edgecolor="white")
for bar in list(b1) + list(b2):
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.3, f"{h:.1f}%",
            ha="center", fontsize=8, color="#444")
ax.set_xticks(x)
ax.set_xticklabels(rev_share["customer_tier"], fontsize=9)
ax.set_ylabel("Share (%)", fontsize=10)
ax.set_title("Revenue vs Customer Share by Tier", fontsize=14, fontweight="bold")
ax.legend(fontsize=9)
ax.set_ylim(0, rev_share[["revenue_pct", "customer_pct"]].max().max() * 1.2)
save(fig, "03_revenue_vs_customer_share.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 4 — Spending Distribution (Box Plot)
# ══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))
order   = TIER_ORDER
palette = {t: PALETTE[t] for t in TIER_ORDER}
sns.boxplot(data=df, x="customer_tier", y="total_spent", order=order,
            palette=palette, linewidth=1.2, fliersize=3, ax=ax)
ax.set_xlabel("Customer Tier", fontsize=10)
ax.set_ylabel("Total Spent (USD)", fontsize=10)
ax.set_title("Spending Distribution by Customer Tier", fontsize=14, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
save(fig, "04_spending_distribution_boxplot.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 5 — Age Group Distribution (Bar + Line)
# ══════════════════════════════════════════════════════════════════════════
df["age_group"] = pd.cut(df["age"],
    bins=[17,24,34,44,54,64,100],
    labels=["18-24","25-34","35-44","45-54","55-64","65+"])

age_grp = df.groupby("age_group", observed=True).agg(
    count=("customer_id","count"),
    avg_spent=("total_spent","mean")
).reset_index()

fig, ax1 = plt.subplots(figsize=(9,5))
ax2 = ax1.twinx()
bars = ax1.bar(age_grp["age_group"].astype(str), age_grp["count"],
               color="#0F3460", alpha=0.85, edgecolor="white")
ax2.plot(age_grp["age_group"].astype(str), age_grp["avg_spent"],
         color="#E94560", marker="o", linewidth=2.5, markersize=7, label="Avg Spend")
ax1.set_xlabel("Age Group", fontsize=10)
ax1.set_ylabel("Number of Customers", fontsize=10, color="#0F3460")
ax2.set_ylabel("Average Total Spent (USD)", fontsize=10, color="#E94560")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax1.set_title("Customer Count & Average Spend by Age Group", fontsize=14, fontweight="bold")
ax2.legend(loc="upper right", fontsize=9)
save(fig, "05_age_group_analysis.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 6 — Top 10 Cities by Revenue
# ══════════════════════════════════════════════════════════════════════════
city_rev = q("""
    SELECT city, state,
           COUNT(*) AS customers,
           ROUND(SUM(total_spent),2) AS revenue,
           ROUND(AVG(total_spent),2) AS avg_value
    FROM customers
    GROUP BY city
    ORDER BY revenue DESC
    LIMIT 10
""")
city_rev["label"] = city_rev["city"] + ", " + city_rev["state"]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(city_rev["label"], city_rev["revenue"],
               color="#1A1A2E", edgecolor="white", height=0.6)
for bar, val in zip(bars, city_rev["revenue"]):
    ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height()/2,
            f"${val:,.0f}", va="center", fontsize=8.5, color="#333")
ax.set_xlabel("Total Revenue (USD)", fontsize=10)
ax.set_title("Top 10 Cities by Customer Revenue", fontsize=14, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.invert_yaxis()
ax.set_xlim(0, city_rev["revenue"].max() * 1.2)
save(fig, "06_top_cities_revenue.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 7 — Preferred Category by Tier (Heatmap)
# ══════════════════════════════════════════════════════════════════════════
cat_pivot = df.groupby(["customer_tier", "preferred_category"]).size().unstack(fill_value=0)
# Reorder rows
cat_pivot = cat_pivot.reindex([t for t in TIER_ORDER if t in cat_pivot.index])

fig, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(cat_pivot, annot=True, fmt="d", cmap="Blues",
            linewidths=0.5, linecolor="#ddd", ax=ax,
            cbar_kws={"label": "Customer Count"})
ax.set_xlabel("Preferred Category", fontsize=10)
ax.set_ylabel("Customer Tier", fontsize=10)
ax.set_title("Product Category Preference by Customer Tier", fontsize=14, fontweight="bold")
plt.xticks(rotation=30, ha="right", fontsize=9)
save(fig, "07_category_preference_heatmap.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 8 — RFM Segment Distribution
# ══════════════════════════════════════════════════════════════════════════
rfm_df = q("""
    WITH rfm AS (
        SELECT
            CASE WHEN days_since_last_purchase<=30 THEN 5
                 WHEN days_since_last_purchase<=90 THEN 4
                 WHEN days_since_last_purchase<=180 THEN 3
                 WHEN days_since_last_purchase<=365 THEN 2 ELSE 1 END
            + CASE WHEN total_purchases>=100 THEN 5 WHEN total_purchases>=50 THEN 4
                   WHEN total_purchases>=25  THEN 3 WHEN total_purchases>=10  THEN 2 ELSE 1 END
            + CASE WHEN total_spent>=10000 THEN 5 WHEN total_spent>=5000 THEN 4
                   WHEN total_spent>=2000  THEN 3 WHEN total_spent>=500  THEN 2 ELSE 1 END
            AS rfm_total
        FROM customers
    )
    SELECT
        CASE WHEN rfm_total>=13 THEN 'Champions'
             WHEN rfm_total>=10 THEN 'Loyal'
             WHEN rfm_total>=8  THEN 'Potential Loyalists'
             WHEN rfm_total>=6  THEN 'At Risk'
             WHEN rfm_total>=4  THEN 'Hibernating'
             ELSE 'Lost' END AS rfm_segment,
        COUNT(*) AS cnt
    FROM rfm GROUP BY rfm_segment ORDER BY cnt DESC
""")

rfm_colors = ["#1A1A2E","#16213E","#0F3460","#533483","#E94560","#F5A623"]
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(rfm_df["rfm_segment"], rfm_df["cnt"],
              color=rfm_colors[:len(rfm_df)], edgecolor="white", width=0.6)
for bar, val in zip(bars, rfm_df["cnt"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            str(val), ha="center", fontsize=10, fontweight="bold", color="#333")
ax.set_ylabel("Number of Customers", fontsize=10)
ax.set_title("RFM Segment Distribution", fontsize=14, fontweight="bold")
plt.xticks(rotation=20, ha="right", fontsize=9)
ax.set_ylim(0, rfm_df["cnt"].max() * 1.15)
save(fig, "08_rfm_segment_distribution.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 9 — Loyalty Points vs Total Spent (Scatter)
# ══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 6))
for tier in TIER_ORDER:
    sub = df[df["customer_tier"] == tier]
    ax.scatter(sub["loyalty_points"], sub["total_spent"],
               color=PALETTE[tier], alpha=0.55, s=25, label=tier)
ax.set_xlabel("Loyalty Points", fontsize=10)
ax.set_ylabel("Total Spent (USD)", fontsize=10)
ax.set_title("Loyalty Points vs Total Spend", fontsize=14, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(title="Tier", fontsize=8, title_fontsize=9)
save(fig, "09_loyalty_points_vs_spend_scatter.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 10 — Churn Risk by Tier
# ══════════════════════════════════════════════════════════════════════════
churn_df = q("""
    WITH churn AS (
        SELECT customer_tier,
               CASE WHEN (
                   CASE WHEN days_since_last_purchase>365 THEN 3
                        WHEN days_since_last_purchase>180 THEN 2
                        WHEN days_since_last_purchase>90  THEN 1 ELSE 0 END
                 + CASE WHEN total_purchases<3 THEN 2 WHEN total_purchases<8 THEN 1 ELSE 0 END
                 + CASE WHEN loyalty_points<100 THEN 2 WHEN loyalty_points<500 THEN 1 ELSE 0 END
               ) >= 6 THEN 'CRITICAL'
               WHEN (
                   CASE WHEN days_since_last_purchase>365 THEN 3
                        WHEN days_since_last_purchase>180 THEN 2
                        WHEN days_since_last_purchase>90  THEN 1 ELSE 0 END
                 + CASE WHEN total_purchases<3 THEN 2 WHEN total_purchases<8 THEN 1 ELSE 0 END
                 + CASE WHEN loyalty_points<100 THEN 2 WHEN loyalty_points<500 THEN 1 ELSE 0 END
               ) >= 4 THEN 'HIGH'
               WHEN (
                   CASE WHEN days_since_last_purchase>365 THEN 3
                        WHEN days_since_last_purchase>180 THEN 2
                        WHEN days_since_last_purchase>90  THEN 1 ELSE 0 END
                 + CASE WHEN total_purchases<3 THEN 2 WHEN total_purchases<8 THEN 1 ELSE 0 END
                 + CASE WHEN loyalty_points<100 THEN 2 WHEN loyalty_points<500 THEN 1 ELSE 0 END
               ) >= 2 THEN 'MEDIUM'
               ELSE 'LOW' END AS churn_risk
        FROM customers
    )
    SELECT customer_tier, churn_risk, COUNT(*) AS cnt
    FROM churn
    GROUP BY customer_tier, churn_risk
""")

pivot_churn = churn_df.pivot(index="customer_tier", columns="churn_risk", values="cnt").fillna(0)
risk_order  = [c for c in ["LOW","MEDIUM","HIGH","CRITICAL"] if c in pivot_churn.columns]
pivot_churn = pivot_churn[risk_order]
pivot_churn = pivot_churn.reindex([t for t in TIER_ORDER if t in pivot_churn.index])

risk_colors = {"LOW": "#52c41a", "MEDIUM": "#faad14", "HIGH": "#f5222d", "CRITICAL": "#820014"}
fig, ax = plt.subplots(figsize=(11, 5))
bottom = np.zeros(len(pivot_churn))
for risk in risk_order:
    vals = pivot_churn[risk].values
    ax.bar(pivot_churn.index, vals, bottom=bottom,
           label=risk, color=risk_colors.get(risk, "#888"), edgecolor="white", width=0.55)
    bottom += vals
ax.set_ylabel("Customer Count", fontsize=10)
ax.set_title("Churn Risk Distribution by Customer Tier", fontsize=14, fontweight="bold")
ax.legend(title="Churn Risk", fontsize=9, title_fontsize=9)
save(fig, "10_churn_risk_by_tier.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 11 — Join Cohort Revenue (Line)
# ══════════════════════════════════════════════════════════════════════════
cohort = q("""
    SELECT STRFTIME('%Y', join_date) AS yr,
           COUNT(*) AS cohort_size,
           ROUND(AVG(total_spent),2) AS avg_clv,
           ROUND(SUM(total_spent),2) AS total_rev
    FROM customers
    GROUP BY yr ORDER BY yr
""")

fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()
ax1.bar(cohort["yr"], cohort["cohort_size"], color="#0F3460", alpha=0.7, label="Cohort Size")
ax2.plot(cohort["yr"], cohort["avg_clv"], color="#E94560", marker="o",
         linewidth=2.5, markersize=8, label="Avg CLV")
ax1.set_xlabel("Join Year (Cohort)", fontsize=10)
ax1.set_ylabel("Number of Customers", fontsize=10, color="#0F3460")
ax2.set_ylabel("Average CLV (USD)", fontsize=10, color="#E94560")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax1.set_title("Customer Cohort Analysis by Join Year", fontsize=14, fontweight="bold")
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2, labels1 + labels2, fontsize=9, loc="upper left")
save(fig, "11_cohort_revenue_analysis.png")

# ══════════════════════════════════════════════════════════════════════════
# CHART 12 — AOV vs Purchase Frequency (Bubble)
# ══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6))
for tier in TIER_ORDER:
    sub = df[df["customer_tier"] == tier].sample(min(50, len(df[df["customer_tier"] == tier])),
                                                  random_state=42)
    ax.scatter(sub["total_purchases"], sub["avg_order_value"],
               s=sub["total_spent"]/50,
               color=PALETTE[tier], alpha=0.5, label=tier)
ax.set_xlabel("Total Purchases (Frequency)", fontsize=10)
ax.set_ylabel("Average Order Value (USD)", fontsize=10)
ax.set_title("Purchase Frequency vs AOV\n(Bubble size = Total Spent)", fontsize=13, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(title="Tier", fontsize=8, title_fontsize=9)
save(fig, "12_frequency_vs_aov_bubble.png")

conn.close()
print(f"\n✅  All 12 charts saved → {CHARTS_DIR}")
print(f"🗄   SQLite DB saved   → {DB_PATH}")
