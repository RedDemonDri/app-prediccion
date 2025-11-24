from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth views: login/logout
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # App routes: include app URLs at root so `/` serves the public landing
    path('', include('dashboard.urls')),
    # Also keep the explicit /dashboard/ prefix for backward compatibility
    path('dashboard/', include('dashboard.urls')),
]
