import os, sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
import django
django.setup()
from django.test import Client
c = Client()
resp = c.get('/')
print('GET / ->', resp.status_code)
print(resp.content.decode('utf-8')[:400])
