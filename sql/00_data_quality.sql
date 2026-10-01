-- Nonzero values need investigation, not automatic deletion.
SELECT 'duplicate_item_keys' AS check_name, COUNT(*) AS affected_records
FROM (SELECT order_id, order_item_id FROM order_items GROUP BY 1, 2 HAVING COUNT(*) > 1)
UNION ALL
SELECT 'items_without_orders', COUNT(*) FROM order_items i LEFT JOIN orders o USING(order_id) WHERE o.order_id IS NULL
UNION ALL
SELECT 'items_without_products', COUNT(*) FROM order_items i LEFT JOIN products p USING(product_id) WHERE p.product_id IS NULL
UNION ALL
SELECT 'orders_without_customers', COUNT(*) FROM orders o LEFT JOIN customers c USING(customer_id) WHERE c.customer_id IS NULL
UNION ALL
SELECT 'delivered_orders_without_items', COUNT(*) FROM orders o WHERE order_status = 'delivered'
AND NOT EXISTS (SELECT 1 FROM order_items i WHERE i.order_id = o.order_id)
UNION ALL
SELECT 'delivered_orders_missing_dates', COUNT(*) FROM orders WHERE order_status = 'delivered'
AND (date(order_delivered_customer_date) IS NULL OR date(order_estimated_delivery_date) IS NULL)
UNION ALL
SELECT 'missing_or_nonpositive_item_prices', COUNT(*) FROM order_items WHERE price IS NULL OR CAST(price AS REAL) <= 0;

