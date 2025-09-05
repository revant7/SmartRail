from django.contrib import admin
from .models import (
    InspectionStage, OnlineInspection, InspectionPhoto, InspectionDocument,
    InspectionChecklist, InspectionChecklistResponse, AITrainingData,
    InspectionSummary
)


@admin.register(InspectionStage)
class InspectionStageAdmin(admin.ModelAdmin):
    list_display = ['name', 'stage_type', 'is_active', 'order']
    list_filter = ['stage_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']


@admin.register(OnlineInspection)
class OnlineInspectionAdmin(admin.ModelAdmin):
    list_display = [
        'inspection_id', 'stage', 'requirement', 'part', 'status', 
        'result', 'quality_rating', 'inspection_date'
    ]
    list_filter = [
        'stage', 'status', 'result', 'inspection_date', 'stage__stage_type'
    ]
    search_fields = [
        'inspection_id', 'requirement__title', 
        'findings', 'issues_found'
    ]
    readonly_fields = ['inspection_id', 'created_at', 'updated_at']
    raw_id_fields = ['requirement']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('inspection_id', 'stage', 'requirement')
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
        ('Timing', {
            'fields': ('inspection_date', 'completed_at', 'created_at', 'updated_at')
        }),
        ('AI Data', {
            'fields': ('ai_training_data', 'ai_summary_generated', 'ai_summary')
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


@admin.register(InspectionSummary)
class InspectionSummaryAdmin(admin.ModelAdmin):
    list_display = ['inspection', 'ai_model_version', 'confidence_score', 'generated_at']
    list_filter = ['ai_model_version', 'generated_at']
    search_fields = ['inspection__inspection_id', 'executive_summary']
    raw_id_fields = ['inspection']
    readonly_fields = ['generated_at', 'updated_at']
