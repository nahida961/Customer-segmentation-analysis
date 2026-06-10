[README.md](https://github.com/user-attachments/files/28804307/README.md)
# 📊 Customer Segmentation Analysis

> **Understand customer behaviour, identify high-value groups, and drive data-informed marketing decisions**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![SQL](https://img.shields.io/badge/SQL-SQLite-lightgrey?logo=sqlite)
![Excel](https://img.shields.io/badge/Excel-openpyxl-green?logo=microsoft-excel)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Project Overview

This end-to-end data analytics project performs **customer segmentation** on a dataset of 500 customers using SQL queries, Python analytics, and an automated Excel report. It segments customers across multiple dimensions — **age, spending, location, purchase frequency, and loyalty** — and delivers actionable business insights through 12 charts and a 6-sheet Excel workbook.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🗄 **SQL Analysis** | 4 SQL scripts covering segmentation, spending, RFM, and loyalty queries |
| 📈 **12 Charts** | Donut, bar, box, scatter, heatmap, bubble, cohort, and more |
| 📋 **Excel Report** | 6-sheet formatted workbook with KPI dashboard and full data |
| 🤖 **Synthetic Dataset** | 500-record realistic customer dataset auto-generated |
| 🔍 **RFM Scoring** | Champions → Lost segmentation using Recency, Frequency, Monetary |
| ⚠️ **Churn Risk** | 4-level churn scoring (Low / Medium / High / Critical) |
| 💡 **Insights Doc** | Full recommendations markdown with action priorities |

---

## 📁 Project Structure

```
customer-segmentation-analysis/
│
├── 📂 data/
│   └── customers.csv              # Synthetic dataset (500 customers)
│
├── 📂 sql/
│   ├── 01_create_tables.sql       # Database schema
│   ├── 02_segmentation_queries.sql# Age, spend, location, RFM, category queries
│   ├── 03_spending_analysis.sql   # Revenue, AOV, cohort, Pareto analysis
│   └── 04_loyalty_analysis.sql    # Loyalty tiers, at-risk, churn scoring
│
├── 📂 scripts/
│   ├── generate_dataset.py        # Generates data/customers.csv
│   ├── run_analysis.py            # Runs SQL + generates all 12 charts
│   └── create_excel_report.py     # Builds formatted Excel workbook
│
├── 📂 notebooks/
│   └── customer_segmentation_analysis.ipynb  # Interactive Jupyter notebook
│
├── 📂 insights/
│   └── recommendations.md         # Full insights and action plan
│
├── 📂 outputs/
│   ├── charts/                    # 12 generated PNG charts
│   ├── customers.db               # SQLite database
│   └── Customer_Segmentation_Report.xlsx  # Excel workbook
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/customer-segmentation-analysis.git
cd customer-segmentation-analysis
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Generate Dataset
```bash
python scripts/generate_dataset.py
```
> Creates `data/customers.csv` with 500 realistic customer records

### 4. Run Full Analysis (Charts + SQLite DB)
```bash
python scripts/run_analysis.py
```
> Generates all 12 charts → `outputs/charts/` and SQLite DB → `outputs/customers.db`

### 5. Generate Excel Report
```bash
python scripts/create_excel_report.py
```
> Creates `outputs/Customer_Segmentation_Report.xlsx` with 6 formatted sheets

### 6. Open Jupyter Notebook (Optional)
```bash
jupyter notebook notebooks/customer_segmentation_analysis.ipynb
```

---

## 📊 Output Preview

### Customer Tier Distribution
> 6 segments: Premium · Loyal · Regular · New · Budget · At-Risk

### 12 Generated Charts
| # | Chart | Description |
|---|-------|-------------|
| 01 | Tier Distribution Donut | Customer count per segment |
| 02 | Avg Lifetime Value by Tier | Revenue potential per tier |
| 03 | Revenue vs Customer Share | Pareto analysis |
| 04 | Spending Distribution Boxplot | Spread within each tier |
| 05 | Age Group Analysis | Count + avg spend by age |
| 06 | Top 10 Cities Revenue | Geographic revenue leaders |
| 07 | Category Preference Heatmap | Product preferences by tier |
| 08 | RFM Segment Distribution | Champions → Lost |
| 09 | Loyalty Points vs Spend | Scatter by tier |
| 10 | Churn Risk by Tier | 4-level risk stacked bar |
| 11 | Cohort Revenue Analysis | Join-year cohort CLV |
| 12 | Frequency vs AOV Bubble | Purchase behaviour |

### Excel Workbook Sheets
| Sheet | Contents |
|-------|----------|
| 📊 Summary Dashboard | KPI cards + tier summary table |
| 🔍 Customer Segments | Age group + spending band tables |
| 💰 Spending Analysis | Top 20 customers + cohort + state revenue |
| 🏆 Loyalty Analysis | Loyalty tiers + at-risk customers |
| 📈 RFM Analysis | Full RFM scoring + segment guide |
| 📋 Raw Data | All 500 records with auto-filter |

---

## 🔍 SQL Queries Included

```sql
-- RFM Segmentation (sample)
WITH rfm_scores AS (
    SELECT customer_id,
        CASE WHEN days_since_last_purchase <= 30 THEN 5 ... END AS recency_score,
        CASE WHEN total_purchases >= 100 THEN 5 ... END AS frequency_score,
        CASE WHEN total_spent >= 10000 THEN 5 ... END AS monetary_score
    FROM customers
)
SELECT *, (recency_score + frequency_score + monetary_score) AS rfm_total,
    CASE WHEN rfm_total >= 13 THEN 'Champions' ... END AS rfm_segment
FROM rfm_scores
ORDER BY rfm_total DESC;
```

See `sql/` folder for all 4 query scripts.

---

## 📌 Key Insights

1. **Top 8.6% of customers (Premium tier) drive ~40% of total revenue**
2. **21% of customers are At-Risk** — inactive >180 days; targeted win-back can recover $150K+
3. **Age 35–44 has the highest AOV** despite not being the largest cohort
4. **Electronics & Clothing** are preferred by high-spending segments
5. **2021–2022 cohorts** show the highest average CLV, suggesting optimal targeting windows

Full analysis: [`insights/recommendations.md`](insights/recommendations.md)

---

## 🛠 Tech Stack

| Tool | Usage |
|------|-------|
| **Python 3.9+** | Core analysis language |
| **pandas** | Data manipulation and aggregation |
| **SQLite3** | In-process SQL query engine |
| **matplotlib** | Chart generation |
| **seaborn** | Statistical visualizations |
| **openpyxl** | Excel workbook creation and formatting |
| **Jupyter** | Interactive analysis notebook |

---

## 📈 Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | string | Unique identifier (CUST0001–CUST0500) |
| `full_name` | string | Customer name |
| `age` | integer | Age (18–75) |
| `gender` | string | Male / Female / Other |
| `city` | string | Home city |
| `state` | string | US state abbreviation |
| `join_date` | date | Account creation date |
| `last_purchase_date` | date | Most recent transaction date |
| `total_purchases` | integer | Lifetime purchase count |
| `total_spent` | float | Total lifetime spend (USD) |
| `avg_order_value` | float | Average transaction value |
| `loyalty_points` | integer | Accumulated loyalty points |
| `preferred_category` | string | Most-shopped product category |
| `days_since_join` | integer | Tenure in days |
| `days_since_last_purchase` | integer | Recency in days |
| `customer_tier` | string | Segment label |

---

## 👤 Author

**Nahida Banoo** — BSc (Hons) Computer Science, University of Delhi  
Research: Financial Fraud Detection using Topological Data Analysis(TDA) (Research Paper, 2026)
