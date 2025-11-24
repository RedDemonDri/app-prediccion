from django.test import Client
from django.contrib.auth.models import User
import uuid

client = Client()
username = f'retrial_{uuid.uuid4().hex[:6]}'
password = 'TryAgainPass123'
email = f'{username}@example.com'

data = {'username': username, 'email': email, 'password1': password, 'password2': password}

print('Registering user:', username, email)
resp = client.post('/register/', data, HTTP_HOST='127.0.0.1', follow=True)
print('register status:', resp.status_code)
print('register final path:', resp.request.get('PATH_INFO'))
print('redirect_chain:', resp.redirect_chain)
print('contains success message:', b'Cuenta creada correctamente' in resp.content)

u = User.objects.filter(username=username).first()
print('user created in DB?', bool(u))
if u:
    print('user id:', u.id, 'is_staff:', u.is_staff, 'is_superuser:', u.is_superuser)

print('\nAttempt login using username...')
resp2 = client.post('/login/', {'username': username, 'password': password}, HTTP_HOST='127.0.0.1', follow=True)
print('login status:', resp2.status_code)
print('login final path:', resp2.request.get('PATH_INFO'))
print('session _auth_user_id:', client.session.get('_auth_user_id'))

print('\nAttempt login using email as username (expected to fail unless configured):')
client2 = Client()
resp3 = client2.post('/login/', {'username': email, 'password': password}, HTTP_HOST='127.0.0.1', follow=True)
print('login(email) status:', resp3.status_code)
print('login(email) final path:', resp3.request.get('PATH_INFO'))
print('session _auth_user_id (email login):', client2.session.get('_auth_user_id'))
