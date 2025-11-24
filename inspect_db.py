import sqlite3, json
p = 'dashboard_project/db.sqlite3'
conn = sqlite3.connect(p)
cur = conn.cursor()
rows = cur.execute("PRAGMA table_info('dashboard_metric')").fetchall()
print(json.dumps(rows, default=str, indent=2))
conn.close()
