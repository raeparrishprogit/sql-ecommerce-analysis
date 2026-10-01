"""Run SQL, independently reconcile results, and render portfolio figures."""
import hashlib
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import run

ROOT=Path(__file__).resolve().parent
BLUE,GOLD='#245A81','#C48A22'

def build():
    run.main()
    raw=ROOT/'data/raw'; results=ROOT/'results'
    orders=pd.read_csv(raw/'olist_orders_dataset.csv')
    items=pd.read_csv(raw/'olist_order_items_dataset.csv')
    reviews=pd.read_csv(raw/'olist_order_reviews_dataset.csv')
    products=pd.read_csv(raw/'olist_products_dataset.csv')
    delivered=orders[orders.order_status.eq('delivered')].copy()
    direct=items[items.order_id.isin(delivered.order_id)]
    actual=pd.to_datetime(delivered.order_delivered_customer_date).dt.normalize()
    expected=pd.to_datetime(delivered.order_estimated_delivery_date).dt.normalize()
    eligible=delivered[actual.notna()&expected.notna()].copy()
    eligible['late']=actual[actual.notna()&expected.notna()]>expected[actual.notna()&expected.notna()]
    review_avg=reviews.groupby('order_id').review_score.mean()
    eligible['score']=eligible.order_id.map(review_avg)
    totals=pd.read_csv(results/'06_sales_reconciliation.csv').iloc[0]
    assert np.isclose(direct.price.sum(),totals.merchandise_value_brl)
    assert len(delivered)==totals.delivered_orders_with_items
    monthly=pd.read_csv(results/'01_monthly_sales.csv')
    categories=pd.read_csv(results/'02_category_sales.csv')
    assert np.isclose(monthly.sales_brl.sum(),direct.price.sum())
    assert np.isclose(categories.sales_brl.sum(),direct.price.sum())
    states=pd.read_csv(results/'03_delivery_reviews.csv')
    assert states.eligible_delivered_orders.sum()==len(eligible)
    assert states.late_orders.sum()==eligible.late.sum()
    comparison=pd.read_csv(results/'04_review_comparison.csv').set_index('delivery_group')
    for label,flag in [('Late',True),('On time',False)]:
        group=eligible[eligible.late.eq(flag)]
        assert len(group)==comparison.loc[label,'orders']
        assert np.isclose(group.score.mean(),comparison.loc[label,'mean_review_score'])
    # Compare every monthly total through an independent pandas join and grouping.
    independent=direct.merge(delivered[['order_id','order_purchase_timestamp']],on='order_id',validate='many_to_one')
    independent['month']=independent.order_purchase_timestamp.str[:7]
    monthly_check=independent.groupby('month').price.sum()
    assert np.allclose(monthly.set_index('month').sales_brl.sort_index(),monthly_check.sort_index())
    unknown=direct.merge(products[['product_id','product_category_name']],on='product_id',validate='many_to_one').product_category_name.isna().sum()
    summary={
      'analysis_date':'2026-10-01','source_start':orders.order_purchase_timestamp.min(),'source_end':orders.order_purchase_timestamp.max(),
      'raw_orders':len(orders),'raw_items':len(items),'raw_products':len(products),'raw_reviews':len(reviews),
      'delivered_orders':len(delivered),'delivered_item_rows':len(direct),
      'merchandise_value_brl':float(direct.price.sum()),'average_order_value_brl':float(direct.price.sum()/len(delivered)),
      'delivery_eligible_orders':len(eligible),'late_orders':int(eligible.late.sum()),'late_pct':float(100*eligible.late.mean()),
      'missing_delivery_dates':int(len(delivered)-len(eligible)),
      'orders_with_multiple_reviews':int((reviews.groupby('order_id').size()>1).sum()),
      'delivered_items_missing_category':int(unknown),
      'top_five_category_sales_share_pct':float(100*categories.head(5).sales_brl.sum()/direct.price.sum()),
      'late_mean_review':float(eligible.loc[eligible.late,'score'].mean()),'on_time_mean_review':float(eligible.loc[~eligible.late,'score'].mean()),
      'validation':'PASS: independent pandas totals, each month, category reconciliation, state denominators and review means',
      'source_files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(raw.glob('*.csv')) if 'geolocation' not in p.name}
    }
    (results/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

def charts():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    out=ROOT/'charts';out.mkdir(exist_ok=True);figs=[]
    def save(fig,name,note):
        fig.text(.02,.02,note,fontsize=9,color='#555555');fig.tight_layout(rect=[0,.065,1,1])
        fig.savefig(out/f'{name}.svg');fig.savefig(out/f'{name}.png',dpi=140);figs.append(fig)
    m=pd.read_csv(ROOT/'results/01_monthly_sales.csv')
    m=m[m.month.between('2017-01','2018-08')]
    fig,ax=plt.subplots(figsize=(11,5.6));ax.plot(range(len(m)),m.sales_brl,color=BLUE,marker='o',linewidth=2)
    positions=sorted(set([0,len(m)-1]+list(range(0,len(m)-2,3))))
    ax.set_xticks(positions,[m.month.iloc[i] for i in positions]);ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v/1000:,.0f}k'))
    ax.set(title='Delivered merchandise sales by purchase month',xlabel='Purchase month',ylabel='Merchandise value (BRL)')
    save(fig,'monthly_sales','Olist • Jan 2017–Aug 2018 • Delivered orders only; freight excluded • Final month may be incomplete')
    c=pd.read_csv(ROOT/'results/02_category_sales.csv').head(8).sort_values('sales_brl')
    trans=pd.read_csv(ROOT/'data/raw/product_category_name_translation.csv').set_index('product_category_name').product_category_name_english
    labels=c.category.map(trans).fillna(c.category).str.replace('_',' ').str.title()
    fig,ax=plt.subplots(figsize=(11,5.6));ax.barh(labels,c.sales_brl,color=BLUE)
    ax.set(title='Top eight product categories by merchandise sales',xlabel='Merchandise value (BRL)');ax.xaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v/1e6:.1f}m'))
    ax.set_xlim(0,c.sales_brl.max()*1.22)
    for i,v in enumerate(c.sales_brl):ax.text(v+c.sales_brl.max()*.015,i,f'{v/1e6:.2f}m',va='center')
    save(fig,'category_sales','Olist • All delivered orders in source • Category names translated with Olist mapping • Freight excluded')
    s=pd.read_csv(ROOT/'results/03_delivery_reviews.csv').nlargest(8,'late_orders').sort_values('late_orders')
    fig,ax=plt.subplots(figsize=(11,5.6));ax.barh(s.state,s.late_orders,color=GOLD);ax.set_xlim(0,s.late_orders.max()*1.55)
    ax.set(title='States with the most late delivered orders',xlabel='Late orders',ylabel='Customer state')
    for i,row in enumerate(s.itertuples()):ax.text(row.late_orders+s.late_orders.max()*.02,i,f'{row.late_orders:,} | {row.late_delivery_pct:.1f}% late',va='center')
    save(fig,'delivery_states','Olist • Both delivery dates required • Labels show count and within-state rate • Late = after promised calendar date')
    r=pd.read_csv(ROOT/'results/04_review_comparison.csv').set_index('delivery_group').loc[['On time','Late']]
    fig,ax=plt.subplots(figsize=(9,5.6));ax.bar(r.index,r.mean_review_score,color=[BLUE,GOLD],width=.55)
    ax.set(title='Customer review scores by delivery outcome',ylabel='Mean order-level review score (1–5)',ylim=(0,5))
    for i,row in enumerate(r.itertuples()):ax.text(i,row.mean_review_score+.1,f'{row.mean_review_score:.2f}\nn={row.reviewed_orders:,}',ha='center')
    save(fig,'delivery_reviews','Olist • Reviewed delivered orders with both dates • Multiple reviews averaged per order\nAssociation, not causation')
    return figs

if __name__=='__main__':
    print(json.dumps(build(),indent=2));charts()
