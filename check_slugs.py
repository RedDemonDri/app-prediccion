import sqlite3
p='dashboard_project/db.sqlite3'
conn=sqlite3.connect(p)
c=conn.cursor()
rows=c.execute("SELECT count(*) FROM dashboard_metric").fetchone()[0]
unique=c.execute("SELECT count(distinct slug) FROM dashboard_metric").fetchone()[0]
nulls=c.execute("SELECT count(*) FROM dashboard_metric WHERE slug IS NULL OR slug='' ").fetchone()[0]
dups=c.execute("SELECT slug, count(*) FROM dashboard_metric GROUP BY slug HAVING count(*)>1").fetchall()
print('total_metrics=', rows)
print('unique_slugs=', unique)
print('null_or_empty_slugs=', nulls)
print('duplicate_slugs=', dups)
conn.close()
