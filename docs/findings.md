# Findings and proposed actions

## 1. Focus delivery investigation using count and rate
RJ records 1,495 late orders out of 12,350 eligible delivered orders (12.11%), compared with an overall 6.77%. SP records 1,820 late orders but a 4.49% rate across 40,494 deliveries. These are customer destination states, not carrier territories.

**Proposed action:** review the high-volume seller-to-customer lanes serving RJ, split transit time from seller handling time, and compare promised delivery windows. Monitor SP for absolute workload. This prioritizes investigation; the dataset does not establish which carrier or process caused delays.

**Test:** pilot an operational change on comparable lanes and track late-order count/rate, fulfillment cost, review coverage, and low-score share. Avoid promising a numerical sales uplift from this observational study.

## 2. Late orders have substantially lower reviews
Of 6,534 late orders, 6,381 have reviews; their order-average score is 2.27. Of 89,936 on-time orders, 89,443 have reviews; their average is 4.29. The difference is about 2.02 points on a five-point scale. Low order-average scores (<=2) occur on 3,979 reviewed late orders (62.36%) and 8,257 reviewed on-time orders (9.23%).

**Proposed action:** investigate delivery-related customer communication and post-purchase support. Compare within seller/category and review timing before attributing the score gap to lateness.

## 3. Sales are distributed across several categories
The top five categories contribute 39.83% of R$13.22m in delivered merchandise value. Health & Beauty leads (R$1.23m), followed by Watches & Gifts (R$1.17m), Bed Bath & Table (R$1.02m), Sports & Leisure (R$0.95m), and Computers & Accessories (R$0.89m).

**Proposed action:** include leading categories in an operational pilot so it covers meaningful sales volume. Category profitability cannot be ranked without costs.

## 4. The monthly series contains boundary effects
November 2017 is the highest displayed month at R$987,765.37. Opening 2016 months are sparse and November 2016 has no delivered-order sales row. The final sales month may be cut short. The raw output's percentage change compares the prior observed month; it must not be treated as calendar-month growth where a month is absent. The main chart avoids the sparse opening period and does not use the final month to infer a downturn.

## Evidence map
- Sales: `sql/01_monthly_sales.sql`, `sql/02_category_sales.sql`, `sql/06_sales_reconciliation.sql`.
- Delivery: `sql/03_delivery_reviews.sql`, `sql/04_review_comparison.sql`.
- Inclusion and quality: `sql/00_data_quality.sql`, `sql/05_order_status.sql`, `results/summary.json`.
- Independent reconciliations: `build_portfolio.py`.
