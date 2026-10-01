-- All orders, including those excluded from delivered merchandise sales.
SELECT order_status, COUNT(*) AS orders,
 MIN(order_purchase_timestamp) AS first_purchase,
 MAX(order_purchase_timestamp) AS last_purchase
FROM orders GROUP BY order_status ORDER BY orders DESC;
