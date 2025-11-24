from django.test import Client
from django.contrib.auth.models import User

client = Client()
data = {
    'username': 'ui_testuser',
    'email': 'ui_testuser@example.com',
    'password1': 'UiTestPass123',
    'password2': 'UiTestPass123',
}

print('Posting to /register/ with HTTP_HOST=127.0.0.1')
resp = client.post('/register/', data, HTTP_HOST='127.0.0.1', follow=True)
print('status_code:', resp.status_code)
print('final_url:', resp.request.get('PATH_INFO'))
print('redirect_chain:', resp.redirect_chain)
print('response_contains_success:', b'Cuenta creada correctamente' in resp.content)

u = User.objects.filter(username='ui_testuser').first()
print('user created?', bool(u))
if u:
    print('is_staff=', u.is_staff, 'is_superuser=', u.is_superuser)
    print('groups=', list(u.groups.values_list('name', flat=True)))
    print('password_prefix=', u.password[:30])
