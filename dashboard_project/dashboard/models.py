# dashboard/models.py
from django.db import models
from django.conf import settings

class MetricCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Metric(models.Model):
    name = models.CharField(max_length=120)
    category = models.ForeignKey(MetricCategory, on_delete=models.PROTECT, related_name='metrics')
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=30, default='unit')  # %, $, unidades, etc.
    display_color = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = ('name', 'category')
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.unit})"

class MetricValue(models.Model):
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='values')
    value = models.FloatField()
    timestamp = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.metric.name} @ {self.timestamp.date()}: {self.value}"

class LogEntry(models.Model):
    # Evitar colisión con admin.LogEntry reverse accessor añadiendo related_name
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='dashboard_logentries')
    action = models.CharField(max_length=120)
    detail = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.action}"
