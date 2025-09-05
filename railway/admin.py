"""
Admin configuration for railway models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    RailwayZone, RailwayDivision, Requirement, 
    VendorRequest, RequirementInspection, RequirementStatusHistory
)


@admin.register(RailwayZone)
class RailwayZoneAdmin(admin.ModelAdmin):
    list_display = ['zone_code', 'name', 'headquarters', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['zone_code', 'name', 'headquarters']
    ordering = ['name']


@admin.register(RailwayDivision)
class RailwayDivisionAdmin(admin.ModelAdmin):
    list_display = ['division_code', 'name', 'zone', 'headquarters', 'is_active']
    list_filter = ['zone', 'is_active', 'created_at']
    search_fields = ['division_code', 'name', 'headquarters']
    ordering = ['zone', 'name']


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'zone', 'division', 'status', 'priority', 
        'assigned_vendor', 'deadline_date', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'category', 'zone', 'division', 
        'created_at', 'deadline_date'
    ]
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['requirement_id', 'created_at', 'updated_at', 'qr_code_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('requirement_id', 'title', 'description', 'category')
        }),
        ('Location', {
            'fields': ('zone', 'division', 'location', 'track_section', 'kilometer_marker')
        }),
        ('Specifications', {
            'fields': ('specifications', 'quantity', 'unit')
        }),
        ('Timeline', {
            'fields': ('deadline_days', 'deadline_date')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Financial', {
            'fields': ('budget', 'currency')
        }),
        ('Assignment', {
            'fields': ('assigned_vendor', 'assigned_at')
        }),
        ('Management', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
        ('QR Code', {
            'fields': ('qr_code_preview',)
        }),
    )
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="200" height="200" />',
                obj.qr_code.url
            )
        return "No QR code generated"
    qr_code_preview.short_description = "QR Code Preview"


@admin.register(VendorRequest)
class VendorRequestAdmin(admin.ModelAdmin):
    list_display = [
        'requirement', 'vendor', 'proposed_price', 
        'delivery_time_days', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'requirement__zone']
    search_fields = ['requirement__title', 'vendor__username', 'vendor__first_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RequirementInspection)
class RequirementInspectionAdmin(admin.ModelAdmin):
    list_display = [
        'requirement', 'inspection_type', 'inspected_by', 
        'result', 'quality_rating', 'inspection_date'
    ]
    list_filter = [
        'inspection_type', 'result', 'inspection_date', 
        'requirement__zone'
    ]
    search_fields = ['requirement__title', 'inspected_by__username']
    readonly_fields = ['created_at']


@admin.register(RequirementStatusHistory)
class RequirementStatusHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'requirement', 'from_status', 'to_status', 
        'changed_by', 'changed_at'
    ]
    list_filter = ['to_status', 'changed_at', 'requirement__zone']
    search_fields = ['requirement__title', 'changed_by__username']
    readonly_fields = ['changed_at']
