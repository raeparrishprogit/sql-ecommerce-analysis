WITH item_totals AS (
    SELECT order_id, SUM(CAST(price AS REAL)) AS merchandise_value
    FROM order_items GROUP BY order_id
), monthly AS (
    SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS month,
           COUNT(*) AS delivered_orders, SUM(i.merchandise_value) AS sales_brl
    FROM orders o JOIN item_totals i USING(order_id)
    WHERE o.order_status = 'delivered'
    GROUP BY 1
), compared AS (
    SELECT *, LAG(sales_brl) OVER (ORDER BY month) AS prior_observed_month_sales
    FROM monthly
)
SELECT month, delivered_orders, ROUND(sales_brl, 2) AS sales_brl,
       ROUND(sales_brl / NULLIF(delivered_orders, 0), 2) AS average_order_value_brl,
       ROUND(100.0 * (sales_brl / NULLIF(prior_observed_month_sales, 0) - 1), 2) AS change_pct
FROM compared ORDER BY month;
