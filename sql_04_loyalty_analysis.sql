-- ============================================================
-- 04_loyalty_analysis.sql
-- Customer Segmentation Analysis
-- Identifies loyal, high-value, at-risk, and churned customers
-- ============================================================

-- ============================================================
-- QUERY 1 — Loyalty Tier Breakdown
-- ============================================================
SELECT
    CASE
        WHEN loyalty_points >= 5000 THEN 'Platinum (5000+)'
        WHEN loyalty_points >= 2000 THEN 'Gold (2000–4999)'
        WHEN loyalty_points >= 1000 THEN 'Silver (1000–1999)'
        WHEN loyalty_points >=  500 THEN 'Bronze (500–999)'
        ELSE 'Standard (<500)'
    END                                  AS loyalty_tier,
    COUNT(*)                             AS customer_count,
    ROUND(AVG(total_spent), 2)           AS avg_total_spent,
    ROUND(AVG(total_purchases), 1)       AS avg_purchases,
    ROUND(AVG(days_since_last_purchase), 0) AS avg_days_inactive,
    ROUND(SUM(total_spent), 2)           AS tier_revenue
FROM customers
GROUP BY loyalty_tier
ORDER BY MIN(loyalty_points) DESC;


-- ============================================================
-- QUERY 2 — Top 25 High-Value Customers (Champions)
-- ============================================================
SELECT
    customer_id,
    full_name,
    age,
    city,
    state,
    preferred_category,
    ROUND(total_spent, 2)                AS lifetime_value,
    total_purchases,
    ROUND(avg_order_value, 2)            AS avg_order_value,
    loyalty_points,
    days_since_last_purchase,
    customer_tier,
    CASE
        WHEN days_since_last_purchase <= 30  THEN 'Active'
        WHEN days_since_last_purchase <= 90  THEN 'Warm'
        WHEN days_since_last_purchase <= 180 THEN 'Cooling'
        ELSE 'Cold'
    END AS engagement_status
FROM customers
ORDER BY total_spent DESC
LIMIT 25;


-- ============================================================
-- QUERY 3 — Loyal Customers (High Frequency + Long Tenure)
-- ============================================================
SELECT
    customer_id,
    full_name,
    city,
    state,
    ROUND(total_spent, 2)                     AS total_spent,
    total_purchases,
    loyalty_points,
    days_since_join                            AS tenure_days,
    ROUND(days_since_join / 365.0, 1)         AS tenure_years,
    days_since_last_purchase,
    preferred_category,
    customer_tier
FROM customers
WHERE total_purchases   >= 40
  AND days_since_join   >= 365
  AND days_since_last_purchase <= 180
ORDER BY total_purchases DESC, total_spent DESC;


-- ============================================================
-- QUERY 4 — At-Risk Customers (Previously Active, Now Dormant)
-- ============================================================
SELECT
    customer_id,
    full_name,
    city,
    state,
    ROUND(total_spent, 2)          AS total_spent,
    total_purchases,
    loyalty_points,
    days_since_last_purchase,
    days_since_join,
    preferred_category,
    CASE
        WHEN total_spent >= 2000 THEN 'HIGH VALUE at-risk'
        WHEN total_spent >=  500 THEN 'MID VALUE at-risk'
        ELSE 'LOW VALUE at-risk'
    END AS risk_category
FROM customers
WHERE days_since_last_purchase > 180
  AND total_purchases >= 5
ORDER BY total_spent DESC;


-- ============================================================
-- QUERY 5 — New Customer Onboarding Monitor (< 6 months)
-- ============================================================
SELECT
    customer_id,
    full_name,
    age,
    city,
    state,
    join_date,
    days_since_join,
    total_purchases,
    ROUND(total_spent, 2)      AS total_spent,
    ROUND(avg_order_value, 2)  AS avg_order_value,
    preferred_category,
    CASE
        WHEN total_purchases >= 5  AND days_since_join <= 60  THEN 'Fast Starter'
        WHEN total_purchases >= 2  AND days_since_join <= 120 THEN 'Warming Up'
        WHEN total_purchases = 1                               THEN 'One-Time Buyer'
        ELSE 'Slow Start'
    END AS onboarding_status
FROM customers
WHERE days_since_join <= 180
ORDER BY total_spent DESC;


-- ============================================================
-- QUERY 6 — Churn Risk Score Card
-- ============================================================
WITH churn_calc AS (
    SELECT
        customer_id,
        full_name,
        total_spent,
        total_purchases,
        loyalty_points,
        days_since_last_purchase,
        days_since_join,
        customer_tier,
        -- Churn risk factors (higher = riskier)
        CASE WHEN days_since_last_purchase > 365 THEN 3
             WHEN days_since_last_purchase > 180 THEN 2
             WHEN days_since_last_purchase >  90 THEN 1
             ELSE 0 END AS recency_risk,
        CASE WHEN total_purchases < 3  THEN 2
             WHEN total_purchases < 8  THEN 1
             ELSE 0 END AS frequency_risk,
        CASE WHEN loyalty_points < 100 THEN 2
             WHEN loyalty_points < 500 THEN 1
             ELSE 0 END AS loyalty_risk
    FROM customers
)
SELECT
    customer_id,
    full_name,
    ROUND(total_spent, 2)            AS total_spent,
    total_purchases,
    days_since_last_purchase,
    customer_tier,
    (recency_risk + frequency_risk + loyalty_risk) AS churn_risk_score,
    CASE
        WHEN (recency_risk + frequency_risk + loyalty_risk) >= 6 THEN 'CRITICAL'
        WHEN (recency_risk + frequency_risk + loyalty_risk) >= 4 THEN 'HIGH'
        WHEN (recency_risk + frequency_risk + loyalty_risk) >= 2 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS churn_risk_level
FROM churn_calc
ORDER BY churn_risk_score DESC, total_spent DESC;


-- ============================================================
-- QUERY 7 — Customer Lifetime Value Summary by Tier
-- ============================================================
SELECT
    customer_tier,
    COUNT(*)                                     AS customer_count,
    ROUND(AVG(total_spent), 2)                   AS avg_clv,
    ROUND(MIN(total_spent), 2)                   AS min_clv,
    ROUND(MAX(total_spent), 2)                   AS max_clv,
    ROUND(SUM(total_spent), 2)                   AS total_revenue,
    ROUND(100.0 * SUM(total_spent) /
          (SELECT SUM(total_spent) FROM customers), 1) AS revenue_pct,
    ROUND(AVG(loyalty_points), 0)                AS avg_loyalty_pts,
    ROUND(AVG(total_purchases), 1)               AS avg_purchases
FROM customers
GROUP BY customer_tier
ORDER BY avg_clv DESC;
