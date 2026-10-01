# Methods and quality decisions

## Population and grain
99,441 orders, 112,650 item rows, 32,951 products, and 99,224 review rows are read from Olist CSVs. The customer table has 99,441 rows. Sales use 96,478 delivered orders and 110,197 item rows. Canceled and other statuses remain in the status summary but are excluded from delivered sales. Item prices are merchandise value in BRL, not profit or platform revenue; freight is excluded.

## Dates
Original timestamps have no explicit timezone conversion. Lateness compares calendar dates: a delivery on the promised date counts as on time regardless of hour. Eight delivered orders lack an actual delivery date and are excluded only from delivery metrics. The rate denominator is 96,470, not all source orders.

## Join controls
Primary order/customer/product keys are nonmissing and unique. Item keys (order_id, order_item_id) have no duplicates. No item-to-order, item-to-product, or order-to-customer orphan records were found; every delivered order has items. No missing/nonpositive prices were found. Raw numeric columns are read as text into SQLite and cast in queries; the current extract is reconciled with pandas numeric parsing, which would fail on malformed prices.

547 source orders have multiple review rows. Reviews are averaged within each order before averaging across orders, so each reviewed order has equal weight. These are not 547 duplicate rows; raw full-row duplicate counts are zero. Missing reviews stay missing rather than becoming zero stars.

1,537 delivered item rows have a missing product category. They remain in the `Unknown` category and all totals; they are not silently dropped. Category order counts overlap when an order contains several categories and should not be summed.

## Validation
An independent pandas calculation recomputes delivered merchandise value directly from eligible item rows. Every monthly total, all category totals combined, state denominator totals, late counts, and the review means reconcile with SQL. Source SHA-256 hashes and counts are saved in results/summary.json. The quality query output is retained even when checks are nonzero.

## Interpretation limits
The data is historical and observational. Delivered-order filtering excludes canceled or unresolved experiences. Review respondents can differ from nonrespondents; reviews can precede completion and may reflect other problems. Seller, geography, category, and timing confound the delivery-review comparison. No causal impact, profit, campaign lift, or current business result is claimed.
