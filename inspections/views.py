"""
Views for online inspection system.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid

from .models import (
    OnlineInspection, InspectionPhoto, InspectionDocument,
    InspectionStage, InspectionChecklist, InspectionChecklistResponse,
    AITrainingData, InspectionSummary
)
from .forms import (
    OnlineInspectionForm, InspectionPhotoForm, MultiplePhotoUploadForm,
    InspectionDocumentForm, InspectionChecklistResponseForm,
    InspectionSearchForm, InspectionStageForm
)
from railway.models import Requirement
from parts.models import Part
from orders.models import PurchaseOrder


@login_required
def inspection_dashboard(request):
    """
    Dashboard showing inspection overview and statistics.
    """
    # Get user's inspections based on user type
    if request.user.user_type == 'VENDOR':
        inspections = OnlineInspection.objects.filter(vendor=request.user)
    elif request.user.user_type == 'RAILWAY_AUTHORITY':
        inspections = OnlineInspection.objects.filter(
            Q(receiver=request.user) | Q(railway_auth=request.user)
        )
    elif request.user.user_type == 'RAILWAY_WORKER':
        inspections = OnlineInspection.objects.filter(worker=request.user)
    else:
        inspections = OnlineInspection.objects.all()
    
    # Statistics
    total_inspections = inspections.count()
    pending_inspections = inspections.filter(status='PENDING').count()
    completed_inspections = inspections.filter(status='COMPLETED').count()
    failed_inspections = inspections.filter(result='FAIL').count()
    
    # Recent inspections
    recent_inspections = inspections.order_by('-inspection_date')[:10]
    
    # Stage-wise statistics
    stage_stats = inspections.values('stage__name').annotate(
        count=Count('id'),
        avg_quality=Avg('quality_rating')
    ).order_by('-count')
    
    context = {
        'total_inspections': total_inspections,
        'pending_inspections': pending_inspections,
        'completed_inspections': completed_inspections,
        'failed_inspections': failed_inspections,
        'recent_inspections': recent_inspections,
        'stage_stats': stage_stats,
    }
    
    return render(request, 'inspections/dashboard.html', context)


@login_required
def inspection_list(request):
    """
    List all inspections with search and filter functionality.
    """
    form = InspectionSearchForm(request.GET)
    inspections = OnlineInspection.objects.all()
    
    # Apply user-based filtering
    if request.user.user_type == 'VENDOR':
        inspections = inspections.filter(vendor=request.user)
    elif request.user.user_type == 'RAILWAY_AUTHORITY':
        inspections = inspections.filter(
            Q(receiver=request.user) | Q(railway_auth=request.user)
        )
    elif request.user.user_type == 'RAILWAY_WORKER':
        inspections = inspections.filter(worker=request.user)
    
    # Apply search filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        stage = form.cleaned_data.get('stage')
        status = form.cleaned_data.get('status')
        result = form.cleaned_data.get('result')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if search:
            inspections = inspections.filter(
                Q(inspection_id__icontains=search) |
                Q(requirement__title__icontains=search) |
                Q(part__name__icontains=search) |
                Q(findings__icontains=search) |
                Q(issues_found__icontains=search)
            )
        
        if stage:
            inspections = inspections.filter(stage=stage)
        
        if status:
            inspections = inspections.filter(status=status)
        
        if result:
            inspections = inspections.filter(result=result)
        
        if date_from:
            inspections = inspections.filter(inspection_date__date__gte=date_from)
        
        if date_to:
            inspections = inspections.filter(inspection_date__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(inspections.order_by('-inspection_date'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'inspections': page_obj,
    }
    
    return render(request, 'inspections/inspection_list.html', context)


@login_required
def inspection_detail(request, inspection_id):
    """
    Detailed view of a specific inspection.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    # Get checklist items for this stage
    checklist_items = InspectionChecklist.objects.filter(
        stage=inspection.stage,
        is_active=True
    ).order_by('order')
    
    # Get responses for this inspection
    checklist_responses = InspectionChecklistResponse.objects.filter(
        inspection=inspection
    ).select_related('checklist_item')
    
    # Get photos and documents
    photos = inspection.photos.all().order_by('-uploaded_at')
    documents = inspection.documents.all().order_by('-uploaded_at')
    
    # Get AI summary if available
    ai_summary = getattr(inspection, 'ai_summary_record', None)
    
    context = {
        'inspection': inspection,
        'checklist_items': checklist_items,
        'checklist_responses': checklist_responses,
        'photos': photos,
        'documents': documents,
        'ai_summary': ai_summary,
    }
    
    return render(request, 'inspections/inspection_detail.html', context)


@login_required
def create_inspection(request):
    """
    Create a new inspection.
    """
    if request.method == 'POST':
        form = OnlineInspectionForm(request.POST, user=request.user)
        if form.is_valid():
            inspection = form.save(commit=False)
            
            # Set participants based on user type
            if request.user.user_type == 'VENDOR':
                inspection.vendor = request.user
            elif request.user.user_type == 'RAILWAY_AUTHORITY':
                inspection.receiver = request.user
                inspection.railway_auth = request.user
            elif request.user.user_type == 'RAILWAY_WORKER':
                inspection.worker = request.user
            
            inspection.save()
            messages.success(request, 'Inspection created successfully.')
            return redirect('inspections:inspection_detail', inspection_id=inspection.inspection_id)
    else:
        form = OnlineInspectionForm(user=request.user)
    
    context = {
        'form': form,
        'stages': InspectionStage.objects.filter(is_active=True),
    }
    
    return render(request, 'inspections/create_inspection.html', context)


@login_required
def update_inspection(request, inspection_id):
    """
    Update an existing inspection.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    # Check permissions
    if not can_edit_inspection(request.user, inspection):
        messages.error(request, 'You do not have permission to edit this inspection.')
        return redirect('inspections:inspection_detail', inspection_id=inspection_id)
    
    if request.method == 'POST':
        form = OnlineInspectionForm(request.POST, instance=inspection, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inspection updated successfully.')
            return redirect('inspections:inspection_detail', inspection_id=inspection_id)
    else:
        form = OnlineInspectionForm(instance=inspection, user=request.user)
    
    context = {
        'form': form,
        'inspection': inspection,
    }
    
    return render(request, 'inspections/update_inspection.html', context)


@login_required
def upload_photos(request, inspection_id):
    """
    Upload photos for an inspection.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    if request.method == 'POST':
        form = MultiplePhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photos = form.cleaned_data['photos']
            photo_type = form.cleaned_data['photo_type']
            caption = form.cleaned_data['caption']
            
            uploaded_count = 0
            for photo in photos:
                InspectionPhoto.objects.create(
                    inspection=inspection,
                    photo_type=photo_type,
                    image=photo,
                    caption=caption,
                    uploaded_by=request.user
                )
                uploaded_count += 1
            
            messages.success(request, f'{uploaded_count} photos uploaded successfully.')
            return redirect('inspections:inspection_detail', inspection_id=inspection_id)
    else:
        form = MultiplePhotoUploadForm()
    
    context = {
        'form': form,
        'inspection': inspection,
    }
    
    return render(request, 'inspections/upload_photos.html', context)


@login_required
def upload_documents(request, inspection_id):
    """
    Upload documents for an inspection.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    if request.method == 'POST':
        form = InspectionDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.inspection = inspection
            document.uploaded_by = request.user
            document.save()
            
            messages.success(request, 'Document uploaded successfully.')
            return redirect('inspections:inspection_detail', inspection_id=inspection_id)
    else:
        form = InspectionDocumentForm()
    
    context = {
        'form': form,
        'inspection': inspection,
    }
    
    return render(request, 'inspections/upload_documents.html', context)


@login_required
def respond_checklist(request, inspection_id, checklist_item_id):
    """
    Respond to a checklist item.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    checklist_item = get_object_or_404(InspectionChecklist, id=checklist_item_id)
    
    if request.method == 'POST':
        form = InspectionChecklistResponseForm(request.POST, inspection=inspection)
        if form.is_valid():
            response, created = InspectionChecklistResponse.objects.get_or_create(
                inspection=inspection,
                checklist_item=checklist_item,
                defaults={
                    'response': form.cleaned_data['response'],
                    'notes': form.cleaned_data['notes'],
                    'photo': form.cleaned_data.get('photo'),
                    'responded_by': request.user,
                }
            )
            
            if not created:
                response.response = form.cleaned_data['response']
                response.notes = form.cleaned_data['notes']
                response.photo = form.cleaned_data.get('photo')
                response.responded_by = request.user
                response.save()
            
            messages.success(request, 'Checklist item responded successfully.')
            return redirect('inspections:inspection_detail', inspection_id=inspection_id)
    else:
        form = InspectionChecklistResponseForm(inspection=inspection)
    
    context = {
        'form': form,
        'inspection': inspection,
        'checklist_item': checklist_item,
    }
    
    return render(request, 'inspections/respond_checklist.html', context)


@login_required
def complete_inspection(request, inspection_id):
    """
    Complete an inspection.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    if not can_edit_inspection(request.user, inspection):
        messages.error(request, 'You do not have permission to complete this inspection.')
        return redirect('inspections:inspection_detail', inspection_id=inspection_id)
    
    if not inspection.can_be_completed():
        messages.error(request, 'Inspection cannot be completed. Required participants are missing.')
        return redirect('inspections:inspection_detail', inspection_id=inspection_id)
    
    if request.method == 'POST':
        inspection.status = 'COMPLETED'
        inspection.completed_at = timezone.now()
        inspection.save()
        
        # Generate AI training data
        generate_ai_training_data(inspection)
        
        messages.success(request, 'Inspection completed successfully.')
        return redirect('inspections:inspection_detail', inspection_id=inspection_id)
    
    context = {
        'inspection': inspection,
    }
    
    return render(request, 'inspections/complete_inspection.html', context)


@login_required
def inspection_stages(request):
    """
    Manage inspection stages.
    """
    stages = InspectionStage.objects.all().order_by('order')
    
    if request.method == 'POST':
        form = InspectionStageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inspection stage created successfully.')
            return redirect('inspections:inspection_stages')
    else:
        form = InspectionStageForm()
    
    context = {
        'stages': stages,
        'form': form,
    }
    
    return render(request, 'inspections/inspection_stages.html', context)


@login_required
def ai_summary(request, inspection_id):
    """
    View AI-generated summary for an inspection.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    ai_summary = getattr(inspection, 'ai_summary_record', None)
    
    if not ai_summary:
        messages.info(request, 'No AI summary available for this inspection.')
        return redirect('inspections:inspection_detail', inspection_id=inspection_id)
    
    context = {
        'inspection': inspection,
        'ai_summary': ai_summary,
    }
    
    return render(request, 'inspections/ai_summary.html', context)


# API Views for AJAX requests

@login_required
@require_http_methods(["POST"])
def upload_photo_ajax(request, inspection_id):
    """
    AJAX endpoint for uploading a single photo.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        photo_type = request.POST.get('photo_type', 'OVERVIEW')
        caption = request.POST.get('caption', '')
        
        inspection_photo = InspectionPhoto.objects.create(
            inspection=inspection,
            photo_type=photo_type,
            image=photo,
            caption=caption,
            uploaded_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'photo_id': inspection_photo.id,
            'photo_url': inspection_photo.image.url,
            'message': 'Photo uploaded successfully.'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@login_required
@require_http_methods(["DELETE"])
def delete_photo_ajax(request, photo_id):
    """
    AJAX endpoint for deleting a photo.
    """
    photo = get_object_or_404(InspectionPhoto, id=photo_id)
    
    # Check permissions
    if not can_edit_inspection(request.user, photo.inspection):
        return JsonResponse({'success': False, 'message': 'Permission denied.'})
    
    photo.delete()
    return JsonResponse({'success': True, 'message': 'Photo deleted successfully.'})


@login_required
@require_http_methods(["GET"])
def get_inspection_data_ajax(request, inspection_id):
    """
    AJAX endpoint for getting inspection data.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    data = {
        'inspection_id': str(inspection.inspection_id),
        'stage': inspection.stage.name,
        'status': inspection.status,
        'result': inspection.result,
        'quality_rating': float(inspection.quality_rating) if inspection.quality_rating else None,
        'overall_score': float(inspection.overall_score) if inspection.overall_score else None,
        'findings': inspection.findings,
        'issues_found': inspection.issues_found,
        'recommendations': inspection.recommendations,
        'photos_count': inspection.photos.count(),
        'documents_count': inspection.documents.count(),
    }
    
    return JsonResponse(data)


# Helper functions

def can_edit_inspection(user, inspection):
    """
    Check if user can edit the inspection.
    """
    if user.is_superuser:
        return True
    
    # Check if user is a participant in the inspection
    if (inspection.vendor == user or 
        inspection.receiver == user or 
        inspection.railway_auth == user or 
        inspection.worker == user):
        return True
    
    return False


def generate_ai_training_data(inspection):
    """
    Generate AI training data from inspection.
    """
    training_data = {
        'inspection_id': str(inspection.inspection_id),
        'stage': inspection.stage.name,
        'stage_type': inspection.stage.stage_type,
        'quality_rating': float(inspection.quality_rating) if inspection.quality_rating else None,
        'overall_score': float(inspection.overall_score) if inspection.overall_score else None,
        'result': inspection.result,
        'findings': inspection.findings,
        'issues_found': inspection.issues_found,
        'recommendations': inspection.recommendations,
        'photos_data': [],
        'checklist_responses': [],
        'participants': inspection.get_participants(),
        'location_data': {
            'location': inspection.inspection_location,
            'zone': inspection.railway_zone,
            'division': inspection.railway_division,
            'track_section': inspection.track_section,
            'kilometer_marker': inspection.kilometer_marker,
            'coordinates': {
                'latitude': float(inspection.latitude) if inspection.latitude else None,
                'longitude': float(inspection.longitude) if inspection.longitude else None,
            }
        }
    }
    
    # Add photos data
    for photo in inspection.photos.all():
        training_data['photos_data'].append({
            'photo_type': photo.photo_type,
            'caption': photo.caption,
            'description': photo.description,
            'ai_tags': photo.ai_tags,
            'ai_analysis': photo.ai_analysis,
        })
    
    # Add checklist responses
    for response in inspection.checklist_responses.all():
        training_data['checklist_responses'].append({
            'item_text': response.checklist_item.item_text,
            'response': response.response,
            'notes': response.notes,
            'has_photo': response.photo is not None,
        })
    
    # Create or update AI training data record
    ai_data, created = AITrainingData.objects.get_or_create(
        inspection=inspection,
        defaults={'stage_data': training_data}
    )
    
    if not created:
        ai_data.stage_data = training_data
        ai_data.save()
    
    return ai_data
