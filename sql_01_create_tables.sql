-- ============================================================
-- 01_create_tables.sql
-- Customer Segmentation Analysis
-- Creates the database schema and loads customer data
-- ============================================================

-- Drop tables if they exist (for re-runs)
DROP TABLE IF EXISTS customer_segments;
DROP TABLE IF EXISTS customers;

-- ============================================================
-- CUSTOMERS TABLE
-- ============================================================
CREATE TABLE customers (
    customer_id              VARCHAR(10)    PRIMARY KEY,
    full_name                VARCHAR(100)   NOT NULL,
    age                      INTEGER        NOT NULL,
    gender                   VARCHAR(10),
    city                     VARCHAR(60),
    state                    VARCHAR(5),
    join_date                DATE           NOT NULL,
    last_purchase_date       DATE,
    total_purchases          INTEGER        DEFAULT 0,
    total_spent              DECIMAL(10,2)  DEFAULT 0.00,
    avg_order_value          DECIMAL(10,2)  DEFAULT 0.00,
    loyalty_points           INTEGER        DEFAULT 0,
    preferred_category       VARCHAR(50),
    days_since_join          INTEGER,
    days_since_last_purchase INTEGER,
    customer_tier            VARCHAR(20)
);

-- ============================================================
-- CUSTOMER SEGMENTS TABLE (derived / analytical)
-- ============================================================
CREATE TABLE customer_segments (
    customer_id          VARCHAR(10)   PRIMARY KEY,
    rfm_segment          VARCHAR(30),
    value_segment        VARCHAR(20),
    age_group            VARCHAR(20),
    spend_band           VARCHAR(20),
    loyalty_status       VARCHAR(20),
    churn_risk           VARCHAR(10),
    segment_label        VARCHAR(40),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- NOTE: After running this script, load data using:
--   .import --csv data/customers.csv customers   (SQLite CLI)
--   OR use the Python analysis script which loads via pandas + sqlite3
