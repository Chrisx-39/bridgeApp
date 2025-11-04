from django.contrib import admin
from .models import Bridge, TrafficData, MaintenanceRecord


@admin.register(Bridge)
class BridgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'bridge_type', 'length', 'width', 'lanes', 'year_built', 'condition_category']
    list_filter = ['bridge_type', 'material', 'year_built']
    search_fields = ['name', 'route']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TrafficData)
class TrafficDataAdmin(admin.ModelAdmin):
    list_display = ['bridge', 'heavy_vehicles', 'small_vehicles', 'total_vehicles', 'recorded_date']
    list_filter = ['recorded_date']
    search_fields = ['bridge__name']


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ['bridge', 'action_type', 'scheduled_date', 'is_completed', 'cost']
    list_filter = ['action_type', 'is_completed', 'scheduled_date']
    search_fields = ['bridge__name', 'description']
    date_hierarchy = 'scheduled_date'