import csv, tempfile
from pathlib import Path
import pandas as pd
import run as sql
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
    root = Path(tmp)
    sql.ROOT = root
    (root/'data/raw').mkdir(parents=True)
    (root/'sql').mkdir()
    for query in (ROOT/'sql').glob('*.sql'):
        (root/'sql'/query.name).write_text(query.read_text(), encoding='utf-8')
    fixtures = {
      'orders': [['order_id','customer_id','order_status','order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date'], ['o1','c1','delivered','2018-01-01','2018-01-12','2018-01-10'], ['o2','c2','delivered','2018-02-01','2018-02-05','2018-02-10']],
      'order_items': [['order_id','order_item_id','product_id','price'], ['o1','1','p1','10'],['o1','2','p1','20'], ['o2','1','p1','60']],
      'customers': [['customer_id','customer_state'],['c1','SP'],['c2','SP']],
      'products': [['product_id','product_category_name'],['p1','books']],
      'order_reviews': [['order_id','review_score'],['o1','1'],['o1','3'],['o2','5']]
    }
    for table, rows in fixtures.items():
        with (root/'data/raw'/f'olist_{table}_dataset.csv').open('w', newline='') as f:
            csv.writer(f).writerows(rows)
    sql.main()
    sales = pd.read_csv(root/'results/01_monthly_sales.csv')
    assert sales.sales_brl.tolist() == [30,60], sales
    assert sales.change_pct.iloc[1] == 100
    delivery = pd.read_csv(root/'results/03_delivery_reviews.csv')
    assert delivery.late_delivery_pct.iloc[0] == 50
    assert delivery.late_review_score.iloc[0] == 2
    assert pd.read_csv(root/'results/data_quality.csv').affected_records.sum() == 0
    fixtures['customers'].append(['c1','SP'])
    with (root/'data/raw/olist_customers_dataset.csv').open('w',newline='') as f:
        csv.writer(f).writerows(fixtures['customers'])
    try:
        sql.main()
    except ValueError:
        pass
    else:
        raise AssertionError('Duplicate customer key was not blocked')

print('PASS: SQL join grain, sales, reviews, dates, and duplicate-key guard')
