# dashboard/admin.py
from django.contrib import admin
from .models import MetricCategory, Metric, MetricValue, LogEntry

@admin.register(MetricCategory)
class MetricCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'display_color')
    list_filter = ('category',)
    search_fields = ('name', 'description')

@admin.register(MetricValue)
class MetricValueAdmin(admin.ModelAdmin):
    list_display = ('metric', 'value', 'timestamp')
    list_filter = ('metric',)
    search_fields = ('metric__name',)
    date_hierarchy = 'timestamp'

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action')
    search_fields = ('action', 'detail')
    date_hierarchy = 'timestamp'

