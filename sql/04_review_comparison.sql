-- Aggregate reviews first so multiple reviews do not multiply order counts.
WITH reviews AS (
 SELECT order_id, AVG(CAST(review_score AS REAL)) AS score
 FROM order_reviews WHERE CAST(review_score AS REAL) BETWEEN 1 AND 5 GROUP BY order_id
), eligible AS (
 SELECT o.order_id, r.score,
 CASE WHEN date(order_delivered_customer_date) > date(order_estimated_delivery_date)
 THEN 'Late' ELSE 'On time' END AS delivery_group
 FROM orders o LEFT JOIN reviews r USING(order_id)
 WHERE order_status = 'delivered' AND date(order_delivered_customer_date) IS NOT NULL
 AND date(order_estimated_delivery_date) IS NOT NULL
)
SELECT delivery_group, COUNT(*) AS orders, COUNT(score) AS reviewed_orders,
 AVG(score) AS mean_review_score,
 SUM(CASE WHEN score <= 2 THEN 1 ELSE 0 END) AS low_score_orders,
 100.0 * SUM(CASE WHEN score <= 2 THEN 1 ELSE 0 END) / NULLIF(COUNT(score),0) AS low_score_pct
FROM eligible GROUP BY delivery_group;
