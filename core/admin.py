"""
Admin configuration for core app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import SystemConfiguration, QRCodeScan, Notification, DashboardWidget


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """
    Admin for SystemConfiguration model.
    """
    list_display = ('key', 'value', 'data_type', 'is_public', 'updated_at')
    list_filter = ('data_type', 'is_public', 'updated_at')
    search_fields = ('key', 'description')
    ordering = ('key',)
    
    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'description', 'data_type')
        }),
        ('Access Control', {
            'fields': ('is_public',)
        }),
        ('Management', {
            'fields': ('updated_by', 'updated_at')
        }),
    )
    
    readonly_fields = ('updated_at',)
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(QRCodeScan)
class QRCodeScanAdmin(admin.ModelAdmin):
    """
    Admin for QRCodeScan model.
    """
    list_display = (
        'qr_code_data_short', 'scanned_by', 'ip_address', 
        'scan_result_status', 'scan_timestamp'
    )
    list_filter = ('scan_timestamp', 'scanned_by__user_type')
    search_fields = (
        'qr_code_data', 'scanned_by__username', 'ip_address'
    )
    ordering = ('-scan_timestamp',)
    
    fieldsets = (
        ('Scan Information', {
            'fields': (
                'qr_code_data', 'scanned_by', 'scan_timestamp'
            )
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent', 'location')
        }),
        ('Scan Result', {
            'fields': ('scan_result',)
        }),
    )
    
    readonly_fields = ('scan_timestamp',)
    
    def qr_code_data_short(self, obj):
        return obj.qr_code_data[:30] + '...' if len(obj.qr_code_data) > 30 else obj.qr_code_data
    qr_code_data_short.short_description = 'QR Code Data'
    
    def scan_result_status(self, obj):
        status = obj.scan_result.get('status', 'unknown')
        color = 'success' if status == 'success' else 'danger' if status == 'not_found' else 'warning'
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, status.title()
        )
    scan_result_status.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin for Notification model.
    """
    list_display = (
        'user', 'notification_type', 'title', 'is_read', 
        'created_at', 'read_at'
    )
    list_filter = (
        'notification_type', 'is_read', 'created_at'
    )
    search_fields = (
        'user__username', 'title', 'message'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Notification Information', {
            'fields': (
                'user', 'notification_type', 'title', 'message'
            )
        }),
        ('Action', {
            'fields': ('action_url',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timing', {
            'fields': ('created_at',)
        }),
    )
    
    readonly_fields = ('created_at', 'read_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """
    Admin for DashboardWidget model.
    """
    list_display = (
        'user', 'widget_type', 'title', 'position_x', 
        'position_y', 'is_active', 'created_at'
    )
    list_filter = (
        'widget_type', 'is_active', 'created_at'
    )
    search_fields = (
        'user__username', 'title'
    )
    ordering = ('user', 'position_y', 'position_x')
    
    fieldsets = (
        ('Widget Information', {
            'fields': (
                'user', 'widget_type', 'title', 'is_active'
            )
        }),
        ('Position and Size', {
            'fields': ('position_x', 'position_y', 'width', 'height')
        }),
        ('Configuration', {
            'fields': ('configuration',),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
