from dashboard.forms import BasicUserCreationForm
from django.contrib.auth.models import Group

data = {
    'username': 'testreg2',
    'email': 'testreg2@example.com',
    'password1': 'Testpass123',
    'password2': 'Testpass123',
}

print('Creating form with data:', data)
f = BasicUserCreationForm(data)
print('is_valid:', f.is_valid())
try:
    print('errors:', f.errors.as_json())
except Exception:
    print('errors (repr):', repr(f.errors))
print('cleaned_data present?:', hasattr(f, 'cleaned_data'))
if f.is_valid():
    user = f.save(commit=False)
    user.is_staff = False
    user.is_superuser = False
    # ensure password is hashed when using commit=False
    user.set_password(f.cleaned_data['password1'])
    user.save()
    group, created = Group.objects.get_or_create(name='BasicUsers')
    user.groups.add(group)
    print('Created user id:', user.id, 'username:', user.username)
    print('Group:', group.name, 'created?', created)
else:
    print('Form invalid, user not created')
