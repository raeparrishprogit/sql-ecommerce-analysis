WITH per_order AS (
 SELECT order_id, SUM(CAST(price AS REAL)) AS sales FROM order_items GROUP BY order_id
)
SELECT COUNT(*) AS delivered_orders_with_items, SUM(sales) AS merchandise_value_brl,
 AVG(sales) AS average_order_value_brl
FROM orders JOIN per_order USING(order_id) WHERE order_status='delivered';
