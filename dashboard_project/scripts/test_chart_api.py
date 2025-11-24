from django.test import Client
from django.utils import timezone
from django.contrib.auth.models import User

client = Client()
# ensure we are authenticated (create or get a test user)
u, created = User.objects.get_or_create(username='apitest')
if created:
	u.set_password('apitestpass')
	u.save()
client.force_login(u)
# sample request: last 7 days daily
resp = client.get('/dashboard/api/chart-data/?granularity=daily', HTTP_HOST='127.0.0.1')
print('status:', resp.status_code)
print('json:', resp.json())

# sample monthly range
today = timezone.localdate()
start = (today.replace(day=1)).isoformat()
end = today.isoformat()
resp2 = client.get(f'/dashboard/api/chart-data/?granularity=monthly&from={start}&to={end}', HTTP_HOST='127.0.0.1')
print('status2:', resp2.status_code)
print('json2:', resp2.json())
