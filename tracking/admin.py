"""
Admin configuration for tracking app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    TrackingEvent, InspectionRecord, QualityCheck, Alert, AuditLog
)


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    """
    Admin for TrackingEvent model.
    """
    list_display = (
        'part', 'event_type', 'location', 'event_date', 'recorded_by'
    )
    list_filter = (
        'event_type', 'event_date', 'part__category', 'railway_zone'
    )
    search_fields = (
        'part__part_number', 'part__name', 'description', 
        'location', 'recorded_by__username'
    )
    ordering = ('-event_date',)
    
    fieldsets = (
        ('Event Information', {
            'fields': (
                'part', 'event_type', 'description', 'event_date'
            )
        }),
        ('Location Information', {
            'fields': (
                'location', 'railway_zone', 'railway_division',
                'track_section', 'kilometer_marker'
            )
        }),
        ('GPS Coordinates', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Related Information', {
            'fields': ('related_order',)
        }),
        ('Recorded By', {
            'fields': ('recorded_by',)
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )


@admin.register(InspectionRecord)
class InspectionRecordAdmin(admin.ModelAdmin):
    """
    Admin for InspectionRecord model.
    """
    list_display = (
        'part', 'inspection_type', 'result', 'score', 
        'inspector', 'inspection_date'
    )
    list_filter = (
        'inspection_type', 'result', 'inspection_date', 'part__category'
    )
    search_fields = (
        'part__part_number', 'part__name', 'findings', 
        'inspector__username'
    )
    ordering = ('-inspection_date',)
    
    fieldsets = (
        ('Inspection Information', {
            'fields': (
                'part', 'inspection_type', 'inspection_date', 'inspector'
            )
        }),
        ('Results', {
            'fields': ('result', 'score', 'findings', 'recommendations')
        }),
        ('Defects', {
            'fields': ('defects_found',)
        }),
        ('Next Actions', {
            'fields': (
                'next_inspection_date', 'corrective_actions_required',
                'corrective_actions'
            )
        }),
        ('Documentation', {
            'fields': ('inspection_report', 'photos')
        }),
    )


@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    """
    Admin for QualityCheck model.
    """
    list_display = (
        'check_number', 'check_type', 'status', 'passed', 
        'checked_by', 'check_date'
    )
    list_filter = (
        'check_type', 'status', 'passed', 'check_date'
    )
    search_fields = (
        'check_number', 'part__part_number', 'order__order_number',
        'checked_by__username', 'remarks'
    )
    ordering = ('-check_date',)
    
    fieldsets = (
        ('Check Information', {
            'fields': (
                'check_number', 'check_type', 'status', 'check_date', 'checked_by'
            )
        }),
        ('Related Objects', {
            'fields': ('part', 'order')
        }),
        ('Results', {
            'fields': ('passed', 'score', 'remarks')
        }),
        ('Non-conformities', {
            'fields': ('non_conformities', 'corrective_actions', 'preventive_actions')
        }),
        ('Documentation', {
            'fields': ('test_results', 'certificates'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """
    Admin for Alert model.
    """
    list_display = (
        'alert_type', 'priority', 'status', 'title', 
        'created_at', 'created_by'
    )
    list_filter = (
        'alert_type', 'priority', 'status', 'created_at'
    )
    search_fields = (
        'title', 'message', 'created_by__username'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Alert Information', {
            'fields': (
                'alert_type', 'priority', 'status', 'title', 'message'
            )
        }),
        ('Related Objects', {
            'fields': ('part', 'order')
        }),
        ('Target Users', {
            'fields': ('target_users',)
        }),
        ('Management', {
            'fields': (
                'created_by', 'acknowledged_by', 'acknowledged_at'
            )
        }),
        ('Timing', {
            'fields': ('created_at', 'resolved_at')
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'acknowledged_at', 'resolved_at')
    
    filter_horizontal = ('target_users',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('target_users')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin for AuditLog model.
    """
    list_display = (
        'user', 'action_type', 'model_name', 'object_repr', 
        'ip_address', 'timestamp'
    )
    list_filter = (
        'action_type', 'model_name', 'timestamp'
    )
    search_fields = (
        'user__username', 'object_id', 'object_repr', 
        'ip_address', 'request_path'
    )
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Action Information', {
            'fields': (
                'user', 'action_type', 'model_name', 'object_id', 'object_repr'
            )
        }),
        ('Changes', {
            'fields': ('old_values', 'new_values'),
            'classes': ('collapse',)
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent', 'request_path'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )
    
    readonly_fields = ('timestamp',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
