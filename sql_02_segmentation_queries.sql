-- ============================================================
-- 02_segmentation_queries.sql
-- Customer Segmentation Analysis
-- Segments customers by age, spending, loyalty, and location
-- ============================================================

-- ============================================================
-- QUERY 1 — Age Group Segmentation
-- ============================================================
SELECT
    CASE
        WHEN age BETWEEN 18 AND 24 THEN '18-24 (Gen Z)'
        WHEN age BETWEEN 25 AND 34 THEN '25-34 (Millennials)'
        WHEN age BETWEEN 35 AND 44 THEN '35-44 (Gen X Young)'
        WHEN age BETWEEN 45 AND 54 THEN '45-54 (Gen X Mature)'
        WHEN age BETWEEN 55 AND 64 THEN '55-64 (Boomers)'
        ELSE '65+ (Seniors)'
    END                                AS age_group,
    COUNT(*)                           AS customer_count,
    ROUND(AVG(total_spent), 2)         AS avg_total_spent,
    ROUND(AVG(total_purchases), 1)     AS avg_purchases,
    ROUND(AVG(avg_order_value), 2)     AS avg_order_value,
    SUM(total_spent)                   AS group_revenue
FROM customers
GROUP BY age_group
ORDER BY age_group;


-- ============================================================
-- QUERY 2 — Spending Band Segmentation
-- ============================================================
SELECT
    CASE
        WHEN total_spent >= 10000 THEN 'Elite (≥$10K)'
        WHEN total_spent >=  5000 THEN 'Premium ($5K–$10K)'
        WHEN total_spent >=  2000 THEN 'High ($2K–$5K)'
        WHEN total_spent >=   500 THEN 'Mid ($500–$2K)'
        WHEN total_spent >=   100 THEN 'Low ($100–$500)'
        ELSE 'Minimal (<$100)'
    END                                AS spend_band,
    COUNT(*)                           AS customer_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct_of_customers,
    ROUND(SUM(total_spent), 2)         AS segment_revenue,
    ROUND(AVG(total_purchases), 1)     AS avg_purchases,
    ROUND(AVG(loyalty_points), 0)      AS avg_loyalty_pts
FROM customers
GROUP BY spend_band
ORDER BY MIN(total_spent) DESC;


-- ============================================================
-- QUERY 3 — Geographic / Location Segmentation (Top 15 Cities)
-- ============================================================
SELECT
    city,
    state,
    COUNT(*)                                           AS customer_count,
    ROUND(SUM(total_spent), 2)                         AS total_revenue,
    ROUND(AVG(total_spent), 2)                         AS avg_customer_value,
    ROUND(AVG(total_purchases), 1)                     AS avg_purchases,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 2) AS market_share_pct
FROM customers
GROUP BY city, state
ORDER BY total_revenue DESC
LIMIT 15;


-- ============================================================
-- QUERY 4 — RFM (Recency, Frequency, Monetary) Segmentation
-- ============================================================
WITH rfm_scores AS (
    SELECT
        customer_id,
        full_name,
        total_spent,
        total_purchases,
        days_since_last_purchase,
        -- Recency score (lower days = higher score)
        CASE
            WHEN days_since_last_purchase <=  30 THEN 5
            WHEN days_since_last_purchase <=  90 THEN 4
            WHEN days_since_last_purchase <= 180 THEN 3
            WHEN days_since_last_purchase <= 365 THEN 2
            ELSE 1
        END AS recency_score,
        -- Frequency score
        CASE
            WHEN total_purchases >= 100 THEN 5
            WHEN total_purchases >=  50 THEN 4
            WHEN total_purchases >=  25 THEN 3
            WHEN total_purchases >=  10 THEN 2
            ELSE 1
        END AS frequency_score,
        -- Monetary score
        CASE
            WHEN total_spent >= 10000 THEN 5
            WHEN total_spent >=  5000 THEN 4
            WHEN total_spent >=  2000 THEN 3
            WHEN total_spent >=   500 THEN 2
            ELSE 1
        END AS monetary_score
    FROM customers
),
rfm_combined AS (
    SELECT *,
        (recency_score + frequency_score + monetary_score) AS rfm_total
    FROM rfm_scores
)
SELECT
    customer_id,
    full_name,
    recency_score,
    frequency_score,
    monetary_score,
    rfm_total,
    CASE
        WHEN rfm_total >= 13 THEN 'Champions'
        WHEN rfm_total >= 10 THEN 'Loyal Customers'
        WHEN rfm_total >=  8 THEN 'Potential Loyalists'
        WHEN rfm_total >=  6 THEN 'At Risk'
        WHEN rfm_total >=  4 THEN 'Hibernating'
        ELSE 'Lost'
    END AS rfm_segment,
    ROUND(total_spent, 2)   AS total_spent,
    total_purchases,
    days_since_last_purchase
FROM rfm_combined
ORDER BY rfm_total DESC;


-- ============================================================
-- QUERY 5 — Category Preference by Segment
-- ============================================================
SELECT
    customer_tier,
    preferred_category,
    COUNT(*)                       AS customer_count,
    ROUND(AVG(total_spent), 2)     AS avg_spent,
    ROUND(SUM(total_spent), 2)     AS category_revenue
FROM customers
GROUP BY customer_tier, preferred_category
ORDER BY customer_tier, category_revenue DESC;


-- ============================================================
-- QUERY 6 — Gender Breakdown per Tier
-- ============================================================
SELECT
    customer_tier,
    gender,
    COUNT(*)                            AS count,
    ROUND(AVG(total_spent), 2)          AS avg_spent,
    ROUND(AVG(loyalty_points), 0)       AS avg_loyalty_pts
FROM customers
GROUP BY customer_tier, gender
ORDER BY customer_tier, count DESC;
