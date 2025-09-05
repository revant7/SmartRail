"""
Streamlined inspection views for photo capture and QR code scanning.
"""
import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q

from .models import (
    EquipmentBatch, OnlineInspection, InspectionPhoto, 
    InspectionStage, AISmartReport
)
from .streamlined_forms import StreamlinedInspectionForm, QRCodeScanForm
from .qr_utils import generate_qr_code_for_batch, create_qr_code_response, validate_qr_code_data


@login_required
def streamlined_inspection_home(request):
    """
    Home page for streamlined inspection system.
    """
    # Get user's recent inspections
    if request.user.user_type == 'VENDOR':
        inspections = OnlineInspection.objects.filter(
            equipment_batch__requirement__assigned_vendor=request.user
        )
    elif request.user.user_type == 'RAILWAY_AUTHORITY':
        inspections = OnlineInspection.objects.filter(
            Q(inspection_source='RAILWAY_AUTH') | 
            Q(equipment_batch__requirement__assigned_vendor__isnull=False)
        )
    elif request.user.user_type == 'RAILWAY_WORKER':
        inspections = OnlineInspection.objects.filter(inspection_source='WORKER')
    else:
        inspections = OnlineInspection.objects.all()
    
    recent_inspections = inspections.order_by('-inspection_date')[:10]
    
    # Get available stages for user
    available_stages = InspectionStage.objects.filter(is_active=True)
    
    context = {
        'recent_inspections': recent_inspections,
        'available_stages': available_stages,
        'user_type': request.user.user_type,
    }
    
    return render(request, 'inspections/streamlined_home.html', context)


@login_required
def start_streamlined_inspection(request):
    """
    Start a new streamlined inspection with QR code scanning or manual UUID entry.
    """
    # Check if UUID is provided via URL parameter (from QR scanner)
    initial_uuid = request.GET.get('uuid')
    
    if request.method == 'POST':
        form = StreamlinedInspectionForm(request.POST, user=request.user)
        if form.is_valid():
            batch_uuid = form.cleaned_data['batch_uuid']
            stage = form.cleaned_data['stage']
            
            try:
                # Get or create equipment batch
                equipment_batch, created = EquipmentBatch.objects.get_or_create(
                    batch_uuid=batch_uuid,
                    defaults={
                        'batch_name': f"Equipment Batch {batch_uuid}",
                        'equipment_type': 'Railway Equipment',
                    }
                )
                
                # Determine inspection source based on user type
                inspection_source = 'VENDOR'
                if request.user.user_type == 'RAILWAY_AUTHORITY':
                    inspection_source = 'RAILWAY_AUTH'
                elif request.user.user_type == 'RAILWAY_WORKER':
                    inspection_source = 'WORKER'
                
                # Create inspection
                inspection = OnlineInspection.objects.create(
                    equipment_batch=equipment_batch,
                    stage=stage,
                    inspection_source=inspection_source,
                    status='IN_PROGRESS',
                    inspection_location='Field Inspection',
                    inspection_date=timezone.now(),
                    vendor=request.user if request.user.user_type == 'VENDOR' else None,
                    railway_auth=request.user if request.user.user_type == 'RAILWAY_AUTHORITY' else None,
                    worker=request.user if request.user.user_type == 'RAILWAY_WORKER' else None,
                )
                
                messages.success(request, 'Inspection started successfully.')
                return redirect('inspections:streamlined_capture', inspection_id=inspection.inspection_id)
                
            except Exception as e:
                messages.error(request, f'Error starting inspection: {str(e)}')
    else:
        # Pre-fill form with UUID if provided
        initial_data = {}
        if initial_uuid:
            initial_data['batch_uuid'] = initial_uuid
        form = StreamlinedInspectionForm(user=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'stages': InspectionStage.objects.filter(is_active=True),
        'initial_uuid': initial_uuid,
    }
    
    return render(request, 'inspections/start_streamlined_inspection.html', context)


@login_required
def streamlined_capture(request, inspection_id):
    """
    Photo capture interface for streamlined inspection.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    # Check permissions
    if not can_edit_inspection(request.user, inspection):
        messages.error(request, 'You do not have permission to edit this inspection.')
        return redirect('inspections:streamlined_home')
    
    # Get existing photos
    photos = inspection.photos.all().order_by('-uploaded_at')
    
    context = {
        'inspection': inspection,
        'photos': photos,
        'equipment_batch': inspection.equipment_batch,
    }
    
    return render(request, 'inspections/streamlined_capture.html', context)


@login_required
@require_http_methods(["POST"])
def upload_streamlined_photo(request, inspection_id):
    """
    Upload photo for streamlined inspection.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    if not can_edit_inspection(request.user, inspection):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied.'
        })
    
    if 'photo' not in request.FILES:
        return JsonResponse({
            'success': False,
            'message': 'No photo provided.'
        })
    
    try:
        photo = request.FILES['photo']
        photo_type = request.POST.get('photo_type', 'EQUIPMENT_OVERVIEW')
        caption = request.POST.get('caption', '')
        qr_code_data = request.POST.get('qr_code_data', '')
        qr_code_uuid = request.POST.get('qr_code_uuid', '')
        
        # Create photo record
        inspection_photo = InspectionPhoto.objects.create(
            inspection=inspection,
            photo_type=photo_type,
            image=photo,
            caption=caption,
            qr_code_data=qr_code_data,
            qr_code_uuid=uuid.UUID(qr_code_uuid) if qr_code_uuid else None,
            uploaded_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Photo uploaded successfully.',
            'photo_id': inspection_photo.id,
            'photo_url': inspection_photo.image.url,
            'photo_type': inspection_photo.photo_type,
            'caption': inspection_photo.caption,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error uploading photo: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def submit_streamlined_inspection(request, inspection_id):
    """
    Submit streamlined inspection with photos.
    """
    inspection = get_object_or_404(OnlineInspection, inspection_id=inspection_id)
    
    if not can_edit_inspection(request.user, inspection):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied.'
        })
    
    try:
        # Update inspection with submission data
        inspection.status = 'COMPLETED'
        inspection.completed_at = timezone.now()
        inspection.result = request.POST.get('result', 'PASS')
        inspection.findings = request.POST.get('findings', '')
        inspection.issues_found = request.POST.get('issues_found', '')
        inspection.recommendations = request.POST.get('recommendations', '')
        inspection.save()
        
        # Update equipment batch stage if needed
        equipment_batch = inspection.equipment_batch
        if inspection.stage.stage_type == 'MANUFACTURING':
            equipment_batch.current_stage = 'SUPPLY'
        elif inspection.stage.stage_type == 'SUPPLY':
            equipment_batch.current_stage = 'RECEIVING'
        elif inspection.stage.stage_type == 'RECEIVING':
            equipment_batch.current_stage = 'FITTING'
        elif inspection.stage.stage_type == 'FITTING':
            equipment_batch.current_stage = 'FINAL'
        elif inspection.stage.stage_type == 'FINAL':
            equipment_batch.current_stage = 'COMPLETED'
        
        equipment_batch.save()
        
        # Trigger AI report generation if all stages are complete
        trigger_ai_report_generation(equipment_batch)
        
        return JsonResponse({
            'success': True,
            'message': 'Inspection submitted successfully.',
            'inspection_id': str(inspection.inspection_id),
            'equipment_batch_uuid': str(equipment_batch.batch_uuid),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error submitting inspection: {str(e)}'
        })


@login_required
def qr_code_scanner(request):
    """
    QR code scanner interface.
    """
    return render(request, 'inspections/qr_scanner.html')


@login_required
@require_http_methods(["POST"])
def process_qr_code(request):
    """
    Process scanned QR code data.
    """
    try:
        data = json.loads(request.body)
        qr_data = data.get('qr_data', '')
        
        if not qr_data:
            return JsonResponse({
                'success': False,
                'message': 'No QR code data provided.'
            })
        
        # Try to parse UUID from QR code
        try:
            batch_uuid = uuid.UUID(qr_data)
            equipment_batch = EquipmentBatch.objects.get(batch_uuid=batch_uuid)
            
            return JsonResponse({
                'success': True,
                'batch_uuid': str(batch_uuid),
                'equipment_batch': {
                    'batch_name': equipment_batch.batch_name,
                    'equipment_type': equipment_batch.equipment_type,
                    'current_stage': equipment_batch.current_stage,
                }
            })
            
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid UUID format in QR code.'
            })
        except EquipmentBatch.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Equipment batch not found.'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing QR code: {str(e)}'
        })


@login_required
def ai_report_dashboard(request):
    """
    Dashboard for AI-generated reports.
    """
    # Get user's equipment batches
    if request.user.user_type == 'VENDOR':
        equipment_batches = EquipmentBatch.objects.filter(
            requirement__assigned_vendor=request.user
        )
    elif request.user.user_type in ['RAILWAY_AUTHORITY', 'RAILWAY_WORKER']:
        equipment_batches = EquipmentBatch.objects.all()
    else:
        equipment_batches = EquipmentBatch.objects.none()
    
    # Get AI reports for these batches
    ai_reports = AISmartReport.objects.filter(
        equipment_batch__in=equipment_batches
    ).order_by('-generated_at')
    
    context = {
        'ai_reports': ai_reports,
        'equipment_batches': equipment_batches,
    }
    
    return render(request, 'inspections/ai_report_dashboard.html', context)


@login_required
def view_ai_report(request, report_id):
    """
    View AI-generated smart report.
    """
    smart_report = get_object_or_404(AISmartReport, id=report_id)
    
    if not can_view_report(request.user, smart_report):
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('inspections:ai_report_dashboard')
    
    context = {
        'smart_report': smart_report,
        'equipment_batch': smart_report.equipment_batch,
    }
    
    return render(request, 'inspections/view_ai_report.html', context)


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


def can_view_report(user, smart_report):
    """
    Check if user can view the AI report.
    """
    if user.is_superuser:
        return True
    
    # Check if user is related to the equipment batch
    equipment_batch = smart_report.equipment_batch
    
    # Check if user is vendor, railway authority, or worker for this batch
    if (equipment_batch.requirement and 
        equipment_batch.requirement.assigned_vendor == user):
        return True
    
    if user.user_type in ['RAILWAY_AUTHORITY', 'RAILWAY_WORKER']:
        return True
    
    return False


@login_required
def generate_qr_code(request, batch_uuid):
    """
    Generate QR code for an equipment batch.
    """
    try:
        batch_uuid_obj = uuid.UUID(batch_uuid)
        equipment_batch = get_object_or_404(EquipmentBatch, batch_uuid=batch_uuid_obj)
        
        # Check permissions
        if not can_view_report(request.user, equipment_batch):
            return HttpResponse('Permission denied', status=403)
        
        size = request.GET.get('size', 200)
        try:
            size = int(size)
            if size < 100 or size > 500:
                size = 200
        except ValueError:
            size = 200
        
        return create_qr_code_response(batch_uuid, size)
        
    except ValueError:
        return HttpResponse('Invalid UUID format', status=400)
    except Exception as e:
        return HttpResponse(f'Error generating QR code: {str(e)}', status=500)


@login_required
def qr_code_generator(request):
    """
    QR code generator page for creating QR codes for equipment batches.
    """
    # Get user's equipment batches
    if request.user.user_type == 'VENDOR':
        equipment_batches = EquipmentBatch.objects.filter(
            requirement__assigned_vendor=request.user
        )
    elif request.user.user_type in ['RAILWAY_AUTHORITY', 'RAILWAY_WORKER']:
        equipment_batches = EquipmentBatch.objects.all()
    else:
        equipment_batches = EquipmentBatch.objects.none()
    
    context = {
        'equipment_batches': equipment_batches,
    }
    
    return render(request, 'inspections/qr_generator.html', context)


def trigger_ai_report_generation(equipment_batch):
    """
    Trigger AI report generation for equipment batch.
    """
    # Check if all required stages are complete
    required_stages = ['MANUFACTURING', 'SUPPLY', 'RECEIVING', 'FITTING', 'FINAL']
    completed_stages = OnlineInspection.objects.filter(
        equipment_batch=equipment_batch,
        status='COMPLETED'
    ).values_list('stage__stage_type', flat=True)
    
    if all(stage in completed_stages for stage in required_stages):
        # Check if report already exists
        if not AISmartReport.objects.filter(equipment_batch=equipment_batch).exists():
            # Create pending report
            AISmartReport.objects.create(
                equipment_batch=equipment_batch,
                status='PENDING',
                executive_summary='',
                quality_assessment='',
                ai_model_version='1.0'
            )
            
            # Trigger AI processing (this would be done asynchronously in production)
            # For now, we'll just mark it as ready for processing
            pass
