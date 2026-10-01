WITH categories AS (
    SELECT COALESCE(p.product_category_name, 'Unknown') AS category,
           COUNT(DISTINCT i.order_id) AS orders_containing_category,
           SUM(CAST(i.price AS REAL)) AS sales_brl
    FROM order_items i JOIN orders o USING(order_id)
    LEFT JOIN products p USING(product_id)
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT category, orders_containing_category, ROUND(sales_brl, 2) AS sales_brl,
       DENSE_RANK() OVER (ORDER BY sales_brl DESC) AS sales_rank
FROM categories ORDER BY sales_rank, category;
-- An order can contain multiple categories; category order counts are not additive.

