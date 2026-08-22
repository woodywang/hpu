-- =============================================================================
-- Vibe Retail Capstone — SQL Extraction
-- Group: [NUMBER]   Members: [NAMES]
-- =============================================================================
-- Business questions covered:
-- 1. Products with highest / lowest sales
-- 2. Store with highest revenue
-- 3. Inventory risk products (low sales + high cost)
-- 5. Products with highest / lowest gross margin rate
-- 6. Store with highest rent return ratio
-- 8. Best / worst store-product combinations
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 1: Detailed sales fact table with product and store metadata
-- Purpose: Create a joined fact table for all downstream KPI analysis.
-- -----------------------------------------------------------------------------
WITH sales_detail AS (
    SELECT
        s.sale_id,
        s.product_id,
        p.product_name,
        p.category,
        p.cost_price,
        s.store_id,
        st.store_location,
        st.monthly_rent,
        s.sale_date,
        s.quantity,
        s.total_amount,
        (s.total_amount - p.cost_price * s.quantity) AS gross_profit,
        (s.total_amount - p.cost_price * s.quantity) / NULLIF(s.total_amount, 0) AS gross_margin_rate
    FROM sales s
    LEFT JOIN products p
        ON p.product_id = s.product_id
    LEFT JOIN stores st
        ON st.store_id = s.store_id
)
SELECT *
FROM sales_detail
ORDER BY sale_date, sale_id;

-- -----------------------------------------------------------------------------
-- Query 2: Products with highest and lowest total sales volume
-- Purpose: Answer Q1
-- -----------------------------------------------------------------------------
WITH product_summary AS (
    SELECT
        product_name,
        SUM(quantity) AS total_units,
        SUM(total_amount) AS total_revenue
    FROM (
        SELECT s.product_id, p.product_name, s.quantity, s.total_amount
        FROM sales s
        LEFT JOIN products p ON p.product_id = s.product_id
    )
    GROUP BY product_name
),
ranked AS (
    SELECT
        product_name,
        total_units,
        ROW_NUMBER() OVER (ORDER BY total_units DESC) AS rn_highest,
        ROW_NUMBER() OVER (ORDER BY total_units ASC) AS rn_lowest
    FROM product_summary
)
SELECT product_name, total_units,
       CASE
           WHEN rn_highest = 1 THEN 'highest_sales'
           WHEN rn_lowest = 1 THEN 'lowest_sales'
       END AS sales_rank_type
FROM ranked
WHERE rn_highest = 1 OR rn_lowest = 1
ORDER BY total_units DESC;

-- -----------------------------------------------------------------------------
-- Query 3: Store with the highest revenue
-- Purpose: Answer Q2
-- -----------------------------------------------------------------------------
SELECT
    st.store_location,
    SUM(s.total_amount) AS total_revenue,
    SUM(s.quantity) AS total_units
FROM sales s
LEFT JOIN stores st ON st.store_id = s.store_id
GROUP BY st.store_location
ORDER BY total_revenue DESC
LIMIT 1;

-- -----------------------------------------------------------------------------
-- Query 4: Inventory risk products with low sales and high cost
-- Purpose: Answer Q3, use HAVING to isolate risky products
-- -----------------------------------------------------------------------------
SELECT
    p.product_name,
    SUM(s.quantity) AS total_units,
    SUM(p.cost_price * s.quantity) AS total_cost,
    SUM(s.total_amount) AS total_revenue
FROM sales s
LEFT JOIN products p ON p.product_id = s.product_id
GROUP BY p.product_name
HAVING SUM(s.quantity) <= 3
   AND SUM(p.cost_price * s.quantity) >= 100
ORDER BY total_cost DESC;

-- -----------------------------------------------------------------------------
-- Query 5: Products with highest and lowest gross margin rate
-- Purpose: Answer Q5
-- -----------------------------------------------------------------------------
WITH product_margin AS (
    SELECT
        p.product_name,
        p.category,
        SUM(s.quantity) AS total_units,
        SUM(s.total_amount) AS total_revenue,
        SUM(p.cost_price * s.quantity) AS total_cost,
        SUM(s.total_amount - p.cost_price * s.quantity) AS gross_profit,
        (SUM(s.total_amount - p.cost_price * s.quantity) / NULLIF(SUM(s.total_amount), 0)) AS gross_margin_rate
    FROM sales s
    LEFT JOIN products p ON p.product_id = s.product_id
    GROUP BY p.product_name, p.category
),
ranked AS (
    SELECT
        product_name,
        category,
        total_units,
        total_revenue,
        total_cost,
        gross_profit,
        gross_margin_rate,
        ROW_NUMBER() OVER (ORDER BY gross_margin_rate DESC) AS rn_highest,
        ROW_NUMBER() OVER (ORDER BY gross_margin_rate ASC) AS rn_lowest
    FROM product_margin
)
SELECT product_name, category, total_units, total_revenue, total_cost, gross_profit, gross_margin_rate,
       CASE
           WHEN rn_highest = 1 THEN 'highest_margin'
           WHEN rn_lowest = 1 THEN 'lowest_margin'
       END AS margin_rank_type
FROM ranked
WHERE rn_highest = 1 OR rn_lowest = 1
ORDER BY gross_margin_rate DESC;

-- -----------------------------------------------------------------------------
-- Query 6: Store with the highest rent return ratio
-- Purpose: Answer Q6
-- -----------------------------------------------------------------------------
SELECT
    st.store_location,
    SUM(s.total_amount) AS total_revenue,
    st.monthly_rent,
    ROUND(SUM(s.total_amount) / st.monthly_rent, 4) AS roi
FROM sales s
LEFT JOIN stores st ON st.store_id = s.store_id
GROUP BY st.store_location, st.monthly_rent
ORDER BY roi DESC
LIMIT 1;

-- -----------------------------------------------------------------------------
-- Query 7: Best and worst store-product combinations by revenue
-- Purpose: Answer Q8
-- -----------------------------------------------------------------------------
WITH store_product_summary AS (
    SELECT
        st.store_location,
        p.product_name,
        SUM(s.quantity) AS total_units,
        SUM(s.total_amount) AS total_revenue,
        SUM(s.total_amount - p.cost_price * s.quantity) AS gross_profit
    FROM sales s
    LEFT JOIN products p ON p.product_id = s.product_id
    LEFT JOIN stores st ON st.store_id = s.store_id
    GROUP BY st.store_location, p.product_name
),
ranked AS (
    SELECT
        store_location,
        product_name,
        total_units,
        total_revenue,
        gross_profit,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS rn_best,
        ROW_NUMBER() OVER (ORDER BY total_revenue ASC) AS rn_worst
    FROM store_product_summary
)
SELECT store_location, product_name, total_units, total_revenue, gross_profit,
       CASE
           WHEN rn_best = 1 THEN 'best_combo'
           WHEN rn_worst = 1 THEN 'worst_combo'
       END AS combo_rank_type
FROM ranked
WHERE rn_best = 1 OR rn_worst = 1
ORDER BY total_revenue DESC;

-- =============================================================================
-- SQLite quick test (optional, from project root):
--   sqlite3 retail.db
--   .mode csv
--   .import data/products.csv products
--   .import data/stores.csv stores
--   .import data/sales.csv sales
--   .read 02_queries.sql
-- =============================================================================
