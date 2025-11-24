import sqlite3
import os
import sys

# DB path: dashboard_project/db.sqlite3
HERE = os.path.dirname(__file__)
DB = os.path.join(os.path.dirname(HERE), 'db.sqlite3')
print('Using DB path:', DB)
if not os.path.exists(DB):
    print('MISSING_DB')
    sys.exit(2)

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
rows = cur.fetchall()
tables = [r[0] for r in rows]
print('TABLE_COUNT:', len(tables))
print('TABLES:', tables)

required = [
    'auth_user', 'auth_group', 'auth_permission',
    'django_content_type', 'django_session', 'django_migrations'
]
for t in required:
    print(f"{t}:", 'YES' if t in tables else 'NO')

# Check superuser count
if 'auth_user' in tables:
    try:
        cur.execute('SELECT COUNT(*) FROM auth_user WHERE is_superuser=1;')
        cnt = cur.fetchone()[0]
        print('SUPERUSER_COUNT:', cnt)
    except Exception as e:
        print('SUPERUSER_COUNT: ERROR -', e)

# List first 5 users if available
if 'auth_user' in tables:
    try:
        cur.execute('SELECT id, username, email, is_superuser FROM auth_user LIMIT 5;')
        for r in cur.fetchall():
            print('USER:', r)
    except Exception as e:
        print('USER_LIST_ERROR:', e)

conn.close()
