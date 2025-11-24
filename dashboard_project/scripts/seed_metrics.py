from django.utils import timezone
from datetime import timedelta
from dashboard.models import Metric

# Crear 5 métricas de ejemplo en los últimos 5 días
created = []
for i in range(5):
    name = f"Metric {i+1}"
    value = float(100 + i * 12 + (i % 3) * 5)
    recorded_at = timezone.now() - timedelta(days=i)
    m = Metric.objects.create(name=name, value=value, recorded_at=recorded_at)
    created.append(m)

print(f"Created {len(created)} metrics:")
for m in created:
    print(m.id, m.name, m.value, m.recorded_at)
