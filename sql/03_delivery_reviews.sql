WITH reviews AS (
    SELECT order_id, AVG(CAST(review_score AS REAL)) AS score
    FROM order_reviews WHERE CAST(review_score AS REAL) BETWEEN 1 AND 5
    GROUP BY order_id
), eligible AS (
    SELECT o.order_id, COALESCE(c.customer_state, 'Unknown') AS state,
           CASE WHEN date(o.order_delivered_customer_date) > date(o.order_estimated_delivery_date)
                THEN 1 ELSE 0 END AS late, r.score
    FROM orders o LEFT JOIN customers c USING(customer_id)
    LEFT JOIN reviews r USING(order_id)
    WHERE o.order_status = 'delivered'
      AND date(o.order_delivered_customer_date) IS NOT NULL
      AND date(o.order_estimated_delivery_date) IS NOT NULL
)
SELECT state, COUNT(*) AS eligible_delivered_orders, SUM(late) AS late_orders,
       ROUND(100.0 * AVG(late), 2) AS late_delivery_pct,
       COUNT(CASE WHEN late = 1 THEN score END) AS reviewed_late_orders,
       ROUND(AVG(CASE WHEN late = 1 THEN score END), 2) AS late_review_score,
       COUNT(CASE WHEN late = 0 THEN score END) AS reviewed_on_time_orders,
       ROUND(AVG(CASE WHEN late = 0 THEN score END), 2) AS on_time_review_score
FROM eligible GROUP BY state ORDER BY late_delivery_pct DESC;
