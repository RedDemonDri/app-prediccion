from django.test import Client
from django.contrib.auth.models import User, Group

client = Client()

resp = client.post('/register/', {
    'username': 'testclient',
    'email': 'testclient@example.com',
    'password1': 'Clientpass123',
    'password2': 'Clientpass123',
})

print('status_code:', resp.status_code)
print('redirected to:', resp.headers.get('Location'))

# verify user created
u = User.objects.filter(username='testclient').first()
print('user exists:', bool(u))
if u:
    print('is_staff:', u.is_staff, 'is_superuser:', u.is_superuser)
    print('groups:', list(u.groups.values_list('name', flat=True)))
