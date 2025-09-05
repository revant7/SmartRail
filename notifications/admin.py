"""
Admin configuration for notifications app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, NotificationTemplate, NotificationPreference, NotificationLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'notification_type', 'priority', 
        'is_read', 'created_at'
    ]
    list_filter = [
        'notification_type', 'priority', 'is_read', 'created_at'
    ]
    search_fields = ['title', 'message', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'read_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'notification_type', 'priority', 'title', 'message')
        }),
        ('Content Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Action', {
            'fields': ('action_url', 'action_text'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'created_at')
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_active', 'created_at']
    search_fields = ['name', 'title_template', 'message_template']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_enabled', 'email_frequency', 
        'sms_enabled', 'push_enabled'
    ]
    list_filter = [
        'email_enabled', 'email_frequency', 'sms_enabled', 'push_enabled'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'notification', 'delivery_method', 'status', 
        'sent_at', 'delivered_at'
    ]
    list_filter = [
        'delivery_method', 'status', 'sent_at', 'delivered_at'
    ]
    search_fields = [
        'notification__title', 'notification__user__username',
        'external_id', 'error_message'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']
