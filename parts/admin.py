"""
Admin configuration for parts app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PartCategory, Part, PartSpecification, PartImage, 
    PartDocument, PartMaintenanceRecord
)


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    """
    Admin for PartCategory model.
    """
    list_display = ('name', 'parent_category', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent_category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'parent_category')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    """
    Admin for Part model.
    """
    list_display = (
        'part_number', 'name', 'manufacturer', 'status', 
        'current_location', 'created_at', 'qr_code_preview'
    )
    list_filter = (
        'status', 'category', 'manufacturer', 'railway_zone', 
        'railway_division', 'created_at'
    )
    search_fields = (
        'part_number', 'name', 'manufacturer', 'model_number',
        'serial_number', 'current_location'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'part_number', 'name', 'description', 'category',
                'manufacturer', 'model_number', 'serial_number'
            )
        }),
        ('Technical Details', {
            'fields': (
                'material', 'weight', 'dimensions', 'status'
            )
        }),
        ('Location Information', {
            'fields': (
                'current_location', 'railway_zone', 'railway_division',
                'track_section', 'kilometer_marker'
            )
        }),
        ('Lifecycle', {
            'fields': (
                'installation_date', 'expected_lifespan',
                'last_inspection_date', 'next_inspection_date'
            )
        }),
        ('Financial Information', {
            'fields': ('unit_cost', 'currency')
        }),
        ('QR Code', {
            'fields': ('qr_code_data', 'qr_code')
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('qr_code_data', 'created_at', 'updated_at')
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="50" height="50" />',
                obj.qr_code.url
            )
        return "No QR Code"
    qr_code_preview.short_description = 'QR Code'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        else:  # Updating existing object
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PartSpecification)
class PartSpecificationAdmin(admin.ModelAdmin):
    """
    Admin for PartSpecification model.
    """
    list_display = ('part', 'name', 'value', 'unit')
    list_filter = ('part__category', 'part__manufacturer')
    search_fields = ('part__part_number', 'part__name', 'name', 'value')
    ordering = ('part', 'name')


@admin.register(PartImage)
class PartImageAdmin(admin.ModelAdmin):
    """
    Admin for PartImage model.
    """
    list_display = ('part', 'caption', 'is_primary', 'uploaded_by', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at', 'part__category')
    search_fields = ('part__part_number', 'part__name', 'caption')
    ordering = ('-uploaded_at',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(PartDocument)
class PartDocumentAdmin(admin.ModelAdmin):
    """
    Admin for PartDocument model.
    """
    list_display = (
        'part', 'document_type', 'title', 'uploaded_by', 'uploaded_at'
    )
    list_filter = ('document_type', 'uploaded_at', 'part__category')
    search_fields = ('part__part_number', 'part__name', 'title', 'description')
    ordering = ('-uploaded_at',)


@admin.register(PartMaintenanceRecord)
class PartMaintenanceRecordAdmin(admin.ModelAdmin):
    """
    Admin for PartMaintenanceRecord model.
    """
    list_display = (
        'part', 'maintenance_type', 'performed_by', 
        'performed_date', 'cost'
    )
    list_filter = (
        'maintenance_type', 'performed_date', 'part__category'
    )
    search_fields = (
        'part__part_number', 'part__name', 'description', 
        'performed_by__username'
    )
    ordering = ('-performed_date',)
    
    fieldsets = (
        ('Maintenance Details', {
            'fields': (
                'part', 'maintenance_type', 'description', 
                'performed_by', 'performed_date'
            )
        }),
        ('Scheduling', {
            'fields': ('next_maintenance_date',)
        }),
        ('Financial', {
            'fields': ('cost',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )
