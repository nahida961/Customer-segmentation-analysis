-- ============================================================
-- 03_spending_analysis.sql
-- Customer Segmentation Analysis
-- Deep-dive into spending patterns and revenue distribution
-- ============================================================

-- ============================================================
-- QUERY 1 — Revenue Concentration (Pareto / 80-20 Rule)
-- ============================================================
WITH ranked AS (
    SELECT
        customer_id,
        full_name,
        total_spent,
        SUM(total_spent) OVER (ORDER BY total_spent DESC) AS running_total,
        SUM(total_spent) OVER ()                           AS grand_total,
        ROW_NUMBER()     OVER (ORDER BY total_spent DESC)  AS rank_num,
        COUNT(*)         OVER ()                           AS total_customers
    FROM customers
)
SELECT
    customer_id,
    full_name,
    ROUND(total_spent, 2)                               AS total_spent,
    rank_num,
    ROUND(100.0 * rank_num / total_customers, 1)        AS cumulative_customer_pct,
    ROUND(100.0 * running_total / grand_total, 1)       AS cumulative_revenue_pct
FROM ranked
WHERE rank_num <= 100   -- Top 100 customers
ORDER BY rank_num;


-- ============================================================
-- QUERY 2 — Average Order Value Bands
-- ============================================================
SELECT
    CASE
        WHEN avg_order_value <  25              THEN 'Under $25'
        WHEN avg_order_value BETWEEN  25 AND  49 THEN '$25–$49'
        WHEN avg_order_value BETWEEN  50 AND  99 THEN '$50–$99'
        WHEN avg_order_value BETWEEN 100 AND 199 THEN '$100–$199'
        WHEN avg_order_value BETWEEN 200 AND 499 THEN '$200–$499'
        ELSE '$500+'
    END                                  AS aov_band,
    COUNT(*)                             AS customer_count,
    ROUND(AVG(total_purchases), 1)       AS avg_purchases,
    ROUND(AVG(total_spent), 2)           AS avg_lifetime_value,
    ROUND(SUM(total_spent), 2)           AS segment_revenue
FROM customers
GROUP BY aov_band
ORDER BY MIN(avg_order_value);


-- ============================================================
-- QUERY 3 — Spending Trend by Join Cohort (Year)
-- ============================================================
SELECT
    STRFTIME('%Y', join_date)                         AS cohort_year,
    COUNT(*)                                          AS cohort_size,
    ROUND(AVG(total_spent), 2)                        AS avg_lifetime_value,
    ROUND(AVG(total_purchases), 1)                    AS avg_purchases,
    ROUND(AVG(avg_order_value), 2)                    AS avg_order_value,
    ROUND(SUM(total_spent), 2)                        AS cohort_revenue,
    ROUND(AVG(days_since_join), 0)                    AS avg_tenure_days
FROM customers
GROUP BY cohort_year
ORDER BY cohort_year;


-- ============================================================
-- QUERY 4 — High-Value Customer Profiles (Top 20%)
-- ============================================================
SELECT
    c.customer_id,
    c.full_name,
    c.age,
    c.gender,
    c.city,
    c.state,
    c.preferred_category,
    ROUND(c.total_spent, 2)           AS total_spent,
    c.total_purchases,
    ROUND(c.avg_order_value, 2)       AS avg_order_value,
    c.loyalty_points,
    c.days_since_last_purchase,
    c.customer_tier
FROM customers c
WHERE c.total_spent >= (
    SELECT PERCENTILE_CONT(0.80) WITHIN GROUP (ORDER BY total_spent)
    FROM customers
)
ORDER BY c.total_spent DESC;


-- ============================================================
-- QUERY 5 — Spending Distribution Summary Statistics
-- ============================================================
SELECT
    COUNT(*)                              AS total_customers,
    ROUND(SUM(total_spent), 2)            AS total_revenue,
    ROUND(AVG(total_spent), 2)            AS mean_ltv,
    ROUND(MIN(total_spent), 2)            AS min_ltv,
    ROUND(MAX(total_spent), 2)            AS max_ltv,
    ROUND(AVG(total_purchases), 1)        AS mean_purchases,
    ROUND(AVG(avg_order_value), 2)        AS mean_aov,
    ROUND(AVG(loyalty_points), 0)         AS mean_loyalty_pts,
    ROUND(AVG(days_since_last_purchase),0) AS mean_days_since_purchase
FROM customers;


-- ============================================================
-- QUERY 6 — Revenue by State (Top 10)
-- ============================================================
SELECT
    state,
    COUNT(DISTINCT city)                            AS cities_count,
    COUNT(*)                                        AS customer_count,
    ROUND(SUM(total_spent), 2)                      AS total_revenue,
    ROUND(AVG(total_spent), 2)                      AS avg_customer_value,
    ROUND(100.0 * SUM(total_spent) /
          (SELECT SUM(total_spent) FROM customers), 1) AS revenue_share_pct
FROM customers
GROUP BY state
ORDER BY total_revenue DESC
LIMIT 10;
