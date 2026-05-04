-- Monthly executive trend
SELECT
    month,
    SUM(revenue) AS revenue,
    SUM(profit) AS profit,
    SUM(gross_margin) / SUM(revenue) AS gross_margin_rate,
    SUM(operating_cost) AS operating_cost,
    SUM(marketing_spend) AS marketing_spend,
    SUM(units_sold) AS units_sold
FROM business_metrics
GROUP BY month
ORDER BY month;

-- Region performance
SELECT
    region,
    SUM(revenue) AS revenue,
    SUM(profit) AS profit,
    SUM(gross_margin) / SUM(revenue) AS gross_margin_rate,
    SUM(revenue) / SUM(marketing_spend) AS marketing_efficiency
FROM business_metrics
GROUP BY region
ORDER BY profit DESC;

-- Product category performance
SELECT
    product_category,
    SUM(revenue) AS revenue,
    SUM(profit) AS profit,
    SUM(units_sold) AS units_sold,
    SUM(gross_margin) / SUM(revenue) AS gross_margin_rate
FROM business_metrics
GROUP BY product_category
ORDER BY profit DESC;

-- Customer segment economics
SELECT
    customer_segment,
    SUM(revenue) AS revenue,
    SUM(profit) AS profit,
    SUM(units_sold) AS units_sold,
    AVG(retention_rate) AS average_retention_rate,
    AVG(churn_risk) AS average_churn_risk
FROM business_metrics
GROUP BY customer_segment
ORDER BY revenue DESC;

-- Latest-month ranking by region and product
WITH latest_month AS (
    SELECT MAX(month) AS month FROM business_metrics
)
SELECT
    bm.region,
    bm.product_category,
    SUM(bm.revenue) AS revenue,
    SUM(bm.profit) AS profit,
    SUM(bm.gross_margin) / SUM(bm.revenue) AS gross_margin_rate
FROM business_metrics bm
JOIN latest_month lm ON bm.month = lm.month
GROUP BY bm.region, bm.product_category
ORDER BY profit DESC;
