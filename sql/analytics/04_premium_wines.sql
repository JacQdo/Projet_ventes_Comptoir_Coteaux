-- ============================================================
-- 04_premium_wines.sql
-- Analyse des vins Premium
-- ============================================================

CREATE OR REPLACE TABLE premium_wines AS
SELECT
    product_id,
    id_web,
    sku,
    price,
    total_sales,
    ca,
    price_zscore,
    stock_quantity,
    stock_status
FROM sales_mart
WHERE premium = TRUE
ORDER BY price DESC;
