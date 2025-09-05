from django.contrib import admin
from .models import (
    InspectionStage, EquipmentBatch, OnlineInspection, InspectionPhoto, InspectionDocument,
    InspectionChecklist, InspectionChecklistResponse, AITrainingData,
    InspectionSummary, AISmartReport
)


@admin.register(InspectionStage)
class InspectionStageAdmin(admin.ModelAdmin):
    list_display = ['name', 'stage_type', 'is_active', 'order']
    list_filter = ['stage_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']


@admin.register(EquipmentBatch)
class EquipmentBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_name', 'batch_uuid', 'equipment_type', 'current_stage', 'created_at']
    list_filter = ['equipment_type', 'current_stage', 'created_at']
    search_fields = ['batch_name', 'batch_uuid', 'manufacturer', 'model_number', 'serial_number']
    readonly_fields = ['batch_uuid', 'created_at', 'updated_at']
    raw_id_fields = ['requirement', 'part']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('batch_uuid', 'batch_name', 'equipment_type')
        }),
        ('Equipment Details', {
            'fields': ('manufacturer', 'model_number', 'serial_number', 'manufacturing_date', 'warranty_expiry')
        }),
        ('Related Objects', {
            'fields': ('requirement', 'part')
        }),
        ('Status', {
            'fields': ('current_stage',)
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OnlineInspection)
class OnlineInspectionAdmin(admin.ModelAdmin):
    list_display = [
        'inspection_id', 'equipment_batch', 'stage', 'inspection_source', 'status', 
        'result', 'quality_rating', 'inspection_date'
    ]
    list_filter = [
        'stage', 'inspection_source', 'status', 'result', 'inspection_date', 'stage__stage_type'
    ]
    search_fields = [
        'inspection_id', 'equipment_batch__batch_name', 'equipment_batch__batch_uuid',
        'findings', 'issues_found'
    ]
    readonly_fields = ['inspection_id', 'created_at', 'updated_at']
    raw_id_fields = ['equipment_batch', 'requirement', 'part']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('inspection_id', 'equipment_batch', 'stage', 'inspection_source')
        }),
        ('Status & Results', {
            'fields': ('status', 'result', 'quality_rating', 'overall_score')
        }),
        ('Findings', {
            'fields': ('findings', 'issues_found', 'recommendations', 'corrective_actions', 'overview_notes')
        }),
        ('Location', {
            'fields': ('inspection_location', 'railway_zone', 'railway_division', 'track_section', 'kilometer_marker', 'latitude', 'longitude')
        }),
        ('Participants', {
            'fields': ('vendor', 'receiver', 'railway_auth', 'worker')
        }),
        ('Related Objects (Legacy)', {
            'fields': ('requirement', 'part', 'order'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('inspection_date', 'completed_at', 'created_at', 'updated_at')
        }),
        ('AI Data', {
            'fields': ('ai_training_data_json', 'ai_summary_generated', 'ai_summary_text')
        }),
    )


@admin.register(InspectionPhoto)
class InspectionPhotoAdmin(admin.ModelAdmin):
    list_display = ['inspection', 'photo_type', 'caption', 'uploaded_by', 'uploaded_at']
    list_filter = ['photo_type', 'uploaded_at']
    search_fields = ['inspection__inspection_id', 'caption', 'description']
    raw_id_fields = ['inspection', 'uploaded_by']


@admin.register(InspectionDocument)
class InspectionDocumentAdmin(admin.ModelAdmin):
    list_display = ['inspection', 'document_type', 'title', 'uploaded_by', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['inspection__inspection_id', 'title', 'description']
    raw_id_fields = ['inspection', 'uploaded_by']


@admin.register(InspectionChecklist)
class InspectionChecklistAdmin(admin.ModelAdmin):
    list_display = ['stage', 'item_text', 'is_required', 'is_active', 'order']
    list_filter = ['stage', 'is_required', 'is_active']
    search_fields = ['item_text', 'description']
    ordering = ['stage', 'order']


@admin.register(InspectionChecklistResponse)
class InspectionChecklistResponseAdmin(admin.ModelAdmin):
    list_display = ['inspection', 'checklist_item', 'response', 'responded_by', 'responded_at']
    list_filter = ['response', 'responded_at']
    search_fields = ['inspection__inspection_id', 'checklist_item__item_text', 'notes']
    raw_id_fields = ['inspection', 'checklist_item', 'responded_by', 'photo']


@admin.register(AITrainingData)
class AITrainingDataAdmin(admin.ModelAdmin):
    list_display = ['inspection', 'processed', 'ai_model_version', 'created_at']
    list_filter = ['processed', 'created_at']
    search_fields = ['inspection__inspection_id', 'ai_model_version']
    raw_id_fields = ['inspection']


@admin.register(AISmartReport)
class AISmartReportAdmin(admin.ModelAdmin):
    list_display = ['equipment_batch', 'status', 'ai_model_version', 'confidence_score', 'generated_at']
    list_filter = ['status', 'ai_model_version', 'generated_at']
    search_fields = ['equipment_batch__batch_name', 'equipment_batch__batch_uuid', 'executive_summary']
    raw_id_fields = ['equipment_batch']
    readonly_fields = ['generated_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('equipment_batch', 'status')
        }),
        ('Report Content', {
            'fields': ('executive_summary', 'quality_assessment', 'defect_analysis', 'stage_comparison', 'recommendations', 'risk_assessment', 'compliance_status')
        }),
        ('Data Sources', {
            'fields': ('vendor_inspections', 'railway_auth_inspections', 'worker_inspections'),
            'classes': ('collapse',)
        }),
        ('AI Processing', {
            'fields': ('ai_model_version', 'confidence_score', 'processing_time_seconds')
        }),
        ('Timing', {
            'fields': ('generated_at', 'completed_at', 'updated_at')
        }),
    )


@admin.register(InspectionSummary)
class InspectionSummaryAdmin(admin.ModelAdmin):
    list_display = ['inspection', 'ai_model_version', 'confidence_score', 'generated_at']
    list_filter = ['ai_model_version', 'generated_at']
    search_fields = ['inspection__inspection_id', 'executive_summary']
    raw_id_fields = ['inspection']
    readonly_fields = ['generated_at', 'updated_at']
