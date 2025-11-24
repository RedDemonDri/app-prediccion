# dashboard/admin.py
from django.contrib import admin
from .models import MetricCategory, Metric, MetricValue, LogEntry, DashboardView

@admin.register(MetricCategory)
class MetricCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'display_color', 'chart_type', 'visible_on_dashboard')
    list_filter = ('category', 'chart_type', 'visible_on_dashboard')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = { 'slug': ('name',) }
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'category', 'description', 'unit', 'display_color')}),
        ('Dashboard', {'fields': ('chart_type', 'visible_on_dashboard', 'default_granularity')}),
    )

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


@admin.register(DashboardView)
class DashboardViewAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_public', 'order')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('metrics',)
    list_filter = ('is_public',)

