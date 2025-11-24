# dashboard/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify

CHART_TYPE_CHOICES = [
    ('line', 'Line'),
    ('bar', 'Bar'),
    ('area', 'Area'),
    ('pie', 'Pie'),
]

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
    # new dashboard fields
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPE_CHOICES, default='line')
    visible_on_dashboard = models.BooleanField(default=True)
    default_granularity = models.CharField(max_length=10, default='daily')

    class Meta:
        unique_together = ('name', 'category')
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.unit})"

    def save(self, *args, **kwargs):
        # auto-fill slug if missing
        if not self.slug:
            base = slugify(self.name) or 'metric'
            slug = base
            i = 1
            while Metric.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

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


class DashboardView(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=140, unique=True)
    metrics = models.ManyToManyField(Metric, related_name='dashboard_views', blank=True)
    default_granularity = models.CharField(max_length=10, default='daily')
    default_from = models.DateField(blank=True, null=True)
    default_to = models.DateField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
