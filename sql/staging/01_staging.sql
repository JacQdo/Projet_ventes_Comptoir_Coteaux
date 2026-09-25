-- ============================================================
-- 01_staging.sql
-- Staging des données de ventes
-- ============================================================

CREATE OR REPLACE TABLE staging_sales AS
SELECT
    CAST(product_id AS INTEGER) AS product_id,
    CAST(onsale_web AS INTEGER) AS onsale_web,
    CAST(price AS DOUBLE) AS price,
    CAST(stock_quantity AS INTEGER) AS stock_quantity,
    CAST(stock_status AS VARCHAR) AS stock_status,
    CAST(id_web AS INTEGER) AS id_web,
    CAST(sku AS VARCHAR) AS sku,
    CAST(total_sales AS DOUBLE) AS total_sales,
    CAST(post_type AS VARCHAR) AS post_type,
    CAST(ca AS DOUBLE) AS ca,
    CAST(price_zscore AS DOUBLE) AS price_zscore,
    CAST(premium AS BOOLEAN) AS premium
FROM read_csv_auto('/app/data/processed/sales_products.csv');
