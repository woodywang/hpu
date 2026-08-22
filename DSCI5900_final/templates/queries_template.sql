-- =============================================================================
-- Vibe Retail Capstone — SQL Extraction Template
-- Group: [NUMBER]   Members: [NAMES]
-- =============================================================================
-- Instructions:
--   1. Use AI (vibe programming) to HELP draft queries — document prompts in Prompt Log
--   2. Fix syntax/logic yourself; add comments explaining each query
--   3. Requirements: JOIN 2+ tables, KPIs, GROUP BY, HAVING where applicable
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query 1: Join all three tables — sales detail with product & store names
-- KPI: line-level sales for downstream analysis
-- -----------------------------------------------------------------------------
-- TODO: Write SELECT ... FROM sales s
--       JOIN products p ON ...
--       JOIN stores st ON ...


-- -----------------------------------------------------------------------------
-- Query 2: Total revenue and units sold by store
-- KPIs: total_sales, total_units
-- Uses: GROUP BY
-- -----------------------------------------------------------------------------
-- TODO: Your query here


-- -----------------------------------------------------------------------------
-- Query 3: Revenue and profit by product category
-- KPIs: revenue, estimated_profit (total_amount - cost_price * quantity)
-- Uses: GROUP BY category
-- -----------------------------------------------------------------------------
-- TODO: Your query here


-- -----------------------------------------------------------------------------
-- Query 4: Slow movers — products with low total quantity sold
-- Uses: GROUP BY product, HAVING SUM(quantity) < [your threshold]
-- -----------------------------------------------------------------------------
-- TODO: Your query here
-- Example threshold: HAVING SUM(s.quantity) < 5


-- -----------------------------------------------------------------------------
-- Query 5: (Optional) Average order value by store
-- KPI: AVG(total_amount) — adjust if you define AOV differently
-- Uses: GROUP BY, HAVING if filtering small sample stores
-- -----------------------------------------------------------------------------
-- TODO: Your query here


-- =============================================================================
-- SQLite quick test (optional, from project root):
--   sqlite3 retail.db
--   .mode csv
--   .import data/products.csv products
--   .import data/stores.csv stores
--   .import data/sales.csv sales
--   .read templates/queries_template.sql
-- =============================================================================
