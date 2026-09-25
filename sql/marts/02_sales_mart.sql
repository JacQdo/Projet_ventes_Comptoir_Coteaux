-- ============================================================
-- 02_sales_mart.sql
-- Table métier consolidée des ventes
-- ============================================================

CREATE OR REPLACE TABLE sales_mart AS
SELECT
    product_id,
    id_web,
    sku,
    price,
    stock_quantity,
    stock_status,
    total_sales,
    ca,
    price_zscore,
    premium,
    CASE
        WHEN premium THEN 'Premium'
        ELSE 'Ordinaire'
    END AS wine_category
FROM staging_sales
WHERE product_id IS NOT NULL;
