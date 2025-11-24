from django.urls import path
from .views import public_landing, home, tabla, chart_data, register, metrics_list

urlpatterns = [
    # Root of the site: public landing for unauthenticated users
    path("", public_landing, name="public_landing"),
    # Dashboard area (requires login)
    path("dashboard/", home, name="home"),
    path("dashboard/tabla/", tabla, name="tabla"),
    path("dashboard/api/chart-data/", chart_data, name="api_chart_data"),
    path("dashboard/api/metrics/", metrics_list, name="api_metrics_list"),
    # Registro de usuarios
    path("register/", register, name="register"),
]
