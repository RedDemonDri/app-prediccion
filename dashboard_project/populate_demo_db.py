# populate_demo_db.py
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard_project.settings")
django.setup()

from dashboard.models import MetricCategory, Metric, MetricValue, LogEntry
from django.contrib.auth import get_user_model

User = get_user_model()

def create_demo_data(days=60):
    # Categorías
    cat_com = MetricCategory.objects.get_or_create(name="Comercial", defaults={"description": "Ventas y marketing"})[0]
    cat_users = MetricCategory.objects.get_or_create(name="Usuarios", defaults={"description": "Métricas de usuarios"})[0]
    cat_sys = MetricCategory.objects.get_or_create(name="Sistema", defaults={"description": "Logs y rendimiento"})[0]

    # Métricas
    ventas = Metric.objects.get_or_create(name="Ventas", category=cat_com, defaults={"unit":"$", "description":"Ingresos diarios"})[0]
    usuarios = Metric.objects.get_or_create(name="Usuarios Activos", category=cat_users, defaults={"unit":"usuarios", "description":"Usuarios únicos activos por día"})[0]
    visitas = Metric.objects.get_or_create(name="Visitas", category=cat_users, defaults={"unit":"visitas", "description":"Visitas diarias al sitio"})[0]

    # Valores: generar serie con tendencia para days días
    base_date = datetime.now()
    for i in range(days):
        d = base_date - timedelta(days=i)
        # ventas: tendencia ascendente con ruido
        ventas_val = max(0.0, 100 + (i % 7) * 3 + random.uniform(-10, 20))
        usuarios_val = max(0.0, 50 + (i % 5) * 2 + random.uniform(-5, 10))
        visitas_val = max(0.0, 200 + (i % 10) * 10 + random.uniform(-30, 60))

        timestamp = d.replace(hour=12, minute=0, second=0, microsecond=0)

        MetricValue.objects.create(metric=ventas, value=round(ventas_val, 2), timestamp=timestamp)
        MetricValue.objects.create(metric=usuarios, value=round(usuarios_val, 0), timestamp=timestamp)
        MetricValue.objects.create(metric=visitas, value=round(visitas_val, 0), timestamp=timestamp)

    # Logs de ejemplo
    if User.objects.filter(username='a1').exists():
        user = User.objects.get(username='a1')
    else:
        user = None

    LogEntry.objects.create(user=user, action="populate_demo", detail=f"Se generaron datos de ejemplo ({days} días).")

    print("Datos demo generados.")

if __name__ == "__main__":
    create_demo_data(days=60)  # ajuste a 60 días; puedes cambiar
