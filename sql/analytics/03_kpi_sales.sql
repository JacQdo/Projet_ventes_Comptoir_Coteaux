-- ============================================================
-- 03_kpi_sales.sql
-- Indicateurs commerciaux
-- ============================================================

CREATE OR REPLACE TABLE kpi_sales AS
SELECT
    COUNT(*) AS nb_produits,
    SUM(total_sales) AS quantite_vendue,
    SUM(ca) AS chiffre_affaires,
    AVG(price) AS prix_moyen,
    COUNT(*) FILTER (WHERE premium = TRUE) AS nb_vins_premium,
    COUNT(*) FILTER (WHERE premium = FALSE) AS nb_vins_ordinaires,
    SUM(ca) FILTER (WHERE premium = TRUE) AS ca_premium,
    SUM(ca) FILTER (WHERE premium = FALSE) AS ca_ordinaire
FROM sales_mart;
