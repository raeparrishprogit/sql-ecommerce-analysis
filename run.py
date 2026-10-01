"""Load Olist CSVs into SQLite and export the SQL result tables."""
import csv
from contextlib import closing
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TABLES = ("orders", "order_items", "customers", "products", "order_reviews")

def main():
    paths = {t: ROOT / "data" / "raw" / f"olist_{t}_dataset.csv" for t in TABLES}
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise SystemExit("Download the Olist CSVs first. Missing:\n" + "\n".join(missing))
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    with closing(sqlite3.connect(ROOT / "data" / "portfolio.sqlite")) as con, con:
        for table, path in paths.items():
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream)
                columns = next(reader)
                # CSV headers are quoted identifiers, never executable SQL.
                quoted = ['"' + name.replace('"', '""') + '"' for name in columns]
                con.execute(f'DROP TABLE IF EXISTS "{table}"')
                con.execute(f'CREATE TABLE "{table}" (' + ", ".join(c + " TEXT" for c in quoted) + ")")
                marks = ",".join("?" for _ in columns)
                con.executemany(f'INSERT INTO "{table}" VALUES ({marks})',
                                ([value if value != "" else None for value in row] for row in reader))
        for table, key in (("orders", "order_id"), ("customers", "customer_id"), ("products", "product_id")):
            bad = con.execute(f'SELECT "{key}" FROM "{table}" GROUP BY "{key}" HAVING COUNT(*) > 1 OR "{key}" IS NULL LIMIT 1').fetchone()
            if bad:
                raise ValueError(f"Missing or duplicate {table}.{key}; repair before joining.")
        for table, key in (("orders", "order_id"), ("order_items", "order_id"), ("customers", "customer_id"), ("products", "product_id"), ("order_reviews", "order_id")):
            con.execute(f'CREATE INDEX IF NOT EXISTS "idx_{table}_{key}" ON "{table}" ("{key}")')
        for query in sorted((ROOT / "sql").glob("*.sql")):
            cursor = con.execute(query.read_text(encoding="utf-8"))
            with (output / (query.stem + ".csv").replace("00_data_quality", "data_quality")).open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow([col[0] for col in cursor.description])
                writer.writerows(cursor)
    print("Done. Review results/data_quality.csv before interpreting results.")

if __name__ == "__main__":
    main()
