"""
Admin configuration for orders app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Project, Vendor, PurchaseOrder, OrderLineItem, 
    OrderDocument, OrderStatusHistory
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin for Project model.
    """
    list_display = (
        'project_code', 'name', 'project_type', 'status', 
        'railway_zone', 'start_date', 'project_manager'
    )
    list_filter = (
        'project_type', 'status', 'railway_zone', 'railway_division',
        'start_date', 'created_at'
    )
    search_fields = (
        'project_code', 'name', 'description', 'railway_zone',
        'railway_division', 'location'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'project_code', 'name', 'description', 'project_type', 'status'
            )
        }),
        ('Location', {
            'fields': ('railway_zone', 'railway_division', 'location')
        }),
        ('Timeline', {
            'fields': ('start_date', 'expected_end_date', 'actual_end_date')
        }),
        ('Budget', {
            'fields': ('budget', 'currency')
        }),
        ('Management', {
            'fields': ('project_manager', 'created_by')
        }),
    )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    """
    Admin for Vendor model.
    """
    list_display = (
        'vendor_code', 'company_name', 'contact_person', 
        'vendor_type', 'status', 'rating'
    )
    list_filter = (
        'vendor_type', 'status', 'rating', 'created_at'
    )
    search_fields = (
        'vendor_code', 'company_name', 'contact_person', 
        'email', 'phone', 'address'
    )
    ordering = ('company_name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'vendor_code', 'company_name', 'contact_person',
                'email', 'phone', 'address'
            )
        }),
        ('Business Details', {
            'fields': (
                'vendor_type', 'status', 'registration_number',
                'tax_id', 'website'
            )
        }),
        ('Performance', {
            'fields': ('rating', 'delivery_performance')
        }),
        ('Specializations', {
            'fields': ('specializations',)
        }),
        ('Management', {
            'fields': ('created_by',)
        }),
    )


class OrderLineItemInline(admin.TabularInline):
    """
    Inline admin for OrderLineItem.
    """
    model = OrderLineItem
    extra = 0
    fields = (
        'part_number', 'part_name', 'quantity', 'unit_price', 
        'total_price', 'status', 'expected_delivery_date'
    )
    readonly_fields = ('total_price',)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """
    Admin for PurchaseOrder model.
    """
    list_display = (
        'order_number', 'project', 'vendor', 'status', 
        'priority', 'total_amount', 'created_at'
    )
    list_filter = (
        'status', 'priority', 'project__railway_zone', 
        'vendor__vendor_type', 'created_at'
    )
    search_fields = (
        'order_number', 'project__name', 'vendor__company_name',
        'delivery_address'
    )
    ordering = ('-created_at',)
    inlines = [OrderLineItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number', 'project', 'vendor', 'status', 'priority'
            )
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'tax_amount', 'total_amount', 'currency')
        }),
        ('Delivery Information', {
            'fields': (
                'delivery_address', 'expected_delivery_date', 
                'actual_delivery_date'
            )
        }),
        ('Terms and Conditions', {
            'fields': (
                'payment_terms', 'delivery_terms', 'warranty_period'
            )
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Management', {
            'fields': ('created_by',)
        }),
    )
    
    readonly_fields = ('order_number', 'subtotal', 'total_amount', 'created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OrderLineItem)
class OrderLineItemAdmin(admin.ModelAdmin):
    """
    Admin for OrderLineItem model.
    """
    list_display = (
        'order', 'part_number', 'part_name', 'quantity', 
        'unit_price', 'total_price', 'status'
    )
    list_filter = ('status', 'order__status', 'order__vendor')
    search_fields = (
        'order__order_number', 'part_number', 'part_name', 
        'manufacturer'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Part Information', {
            'fields': (
                'part_number', 'part_name', 'part_description', 'manufacturer'
            )
        }),
        ('Quantity and Pricing', {
            'fields': ('quantity', 'unit_price', 'total_price')
        }),
        ('Delivery', {
            'fields': ('expected_delivery_date', 'actual_delivery_date')
        }),
        ('Status and Notes', {
            'fields': ('status', 'notes')
        }),
    )
    
    readonly_fields = ('total_price',)


@admin.register(OrderDocument)
class OrderDocumentAdmin(admin.ModelAdmin):
    """
    Admin for OrderDocument model.
    """
    list_display = (
        'order', 'document_type', 'title', 'uploaded_by', 'uploaded_at'
    )
    list_filter = ('document_type', 'uploaded_at', 'order__status')
    search_fields = (
        'order__order_number', 'title', 'description'
    )
    ordering = ('-uploaded_at',)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """
    Admin for OrderStatusHistory model.
    """
    list_display = (
        'order', 'from_status', 'to_status', 'changed_by', 'changed_at'
    )
    list_filter = ('to_status', 'changed_at', 'order__status')
    search_fields = (
        'order__order_number', 'changed_by__username', 'notes'
    )
    ordering = ('-changed_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Status Change', {
            'fields': ('from_status', 'to_status')
        }),
        ('Change Details', {
            'fields': ('changed_by', 'changed_at', 'notes')
        }),
    )
    
    readonly_fields = ('changed_at',)
