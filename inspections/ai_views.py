"""
AI integration views for streamlined inspection system.
"""
import json
import requests
import uuid
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from .models import (
    EquipmentBatch, OnlineInspection, InspectionPhoto, 
    AISmartReport, InspectionStage
)


@login_required
@require_http_methods(["POST"])
def send_inspection_data_to_ai(request, batch_uuid):
    """
    Send inspection data to AI model for processing.
    """
    try:
        batch_uuid_obj = uuid.UUID(batch_uuid)
        equipment_batch = get_object_or_404(EquipmentBatch, batch_uuid=batch_uuid_obj)
        
        # Get all inspections for this batch
        inspections = OnlineInspection.objects.filter(equipment_batch=equipment_batch)
        
        if not inspections.exists():
            return JsonResponse({
                'success': False,
                'message': 'No inspections found for this equipment batch.'
            })
        
        # Prepare data for AI model
        ai_data = prepare_inspection_data_for_ai(equipment_batch, inspections)
        
        # Send to AI model (replace with actual AI endpoint)
        ai_response = send_to_ai_model(ai_data)
        
        if ai_response.get('success'):
            # Create AI Smart Report
            smart_report = AISmartReport.objects.create(
                equipment_batch=equipment_batch,
                executive_summary=ai_response.get('executive_summary', ''),
                quality_assessment=ai_response.get('quality_assessment', ''),
                defect_analysis=ai_response.get('defect_analysis', {}),
                stage_comparison=ai_response.get('stage_comparison', {}),
                recommendations=ai_response.get('recommendations', []),
                risk_assessment=ai_response.get('risk_assessment', {}),
                compliance_status=ai_response.get('compliance_status', {}),
                vendor_inspections=ai_data.get('vendor_inspections', []),
                railway_auth_inspections=ai_data.get('railway_auth_inspections', []),
                worker_inspections=ai_data.get('worker_inspections', []),
                ai_model_version=ai_response.get('model_version', '1.0'),
                confidence_score=ai_response.get('confidence_score'),
                processing_time_seconds=ai_response.get('processing_time'),
                status='COMPLETED',
                completed_at=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'message': 'AI report generated successfully.',
                'report_id': smart_report.id,
                'report_url': f'/inspections/ai-report/{smart_report.id}/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'AI processing failed: {ai_response.get("error", "Unknown error")}'
            })
            
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid batch UUID format.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def get_ai_report(request, report_id):
    """
    Get AI-generated smart report.
    """
    smart_report = get_object_or_404(AISmartReport, id=report_id)
    
    # Check permissions
    if not can_view_report(request.user, smart_report):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied.'
        })
    
    report_data = {
        'id': smart_report.id,
        'equipment_batch': {
            'batch_name': smart_report.equipment_batch.batch_name,
            'batch_uuid': str(smart_report.equipment_batch.batch_uuid),
            'equipment_type': smart_report.equipment_batch.equipment_type,
            'current_stage': smart_report.equipment_batch.current_stage,
        },
        'executive_summary': smart_report.executive_summary,
        'quality_assessment': smart_report.quality_assessment,
        'defect_analysis': smart_report.defect_analysis,
        'stage_comparison': smart_report.stage_comparison,
        'recommendations': smart_report.recommendations,
        'risk_assessment': smart_report.risk_assessment,
        'compliance_status': smart_report.compliance_status,
        'ai_model_version': smart_report.ai_model_version,
        'confidence_score': float(smart_report.confidence_score) if smart_report.confidence_score else None,
        'processing_time_seconds': smart_report.processing_time_seconds,
        'status': smart_report.status,
        'generated_at': smart_report.generated_at.isoformat(),
        'completed_at': smart_report.completed_at.isoformat() if smart_report.completed_at else None,
    }
    
    return JsonResponse({
        'success': True,
        'report': report_data
    })


@login_required
@require_http_methods(["GET"])
def get_batch_inspection_summary(request, batch_uuid):
    """
    Get summary of all inspections for a batch.
    """
    try:
        batch_uuid_obj = uuid.UUID(batch_uuid)
        equipment_batch = get_object_or_404(EquipmentBatch, batch_uuid=batch_uuid_obj)
        
        # Get all inspections grouped by source
        inspections = OnlineInspection.objects.filter(equipment_batch=equipment_batch)
        
        vendor_inspections = inspections.filter(inspection_source='VENDOR')
        railway_auth_inspections = inspections.filter(inspection_source='RAILWAY_AUTH')
        worker_inspections = inspections.filter(inspection_source='WORKER')
        
        # Get photos for each inspection
        photos_by_source = {}
        for source in ['VENDOR', 'RAILWAY_AUTH', 'WORKER']:
            source_inspections = inspections.filter(inspection_source=source)
            photos = InspectionPhoto.objects.filter(
                inspection__in=source_inspections
            ).order_by('-uploaded_at')
            photos_by_source[source] = [
                {
                    'id': photo.id,
                    'photo_type': photo.photo_type,
                    'image_url': photo.image.url,
                    'caption': photo.caption,
                    'qr_code_data': photo.qr_code_data,
                    'qr_code_uuid': str(photo.qr_code_uuid) if photo.qr_code_uuid else None,
                    'uploaded_at': photo.uploaded_at.isoformat(),
                    'uploaded_by': photo.uploaded_by.get_full_name(),
                }
                for photo in photos
            ]
        
        summary_data = {
            'equipment_batch': {
                'batch_name': equipment_batch.batch_name,
                'batch_uuid': str(equipment_batch.batch_uuid),
                'equipment_type': equipment_batch.equipment_type,
                'current_stage': equipment_batch.current_stage,
            },
            'inspections_summary': {
                'total_inspections': inspections.count(),
                'vendor_inspections': vendor_inspections.count(),
                'railway_auth_inspections': railway_auth_inspections.count(),
                'worker_inspections': worker_inspections.count(),
            },
            'photos_by_source': photos_by_source,
            'inspections_by_stage': [
                {
                    'stage': inspection.stage.name,
                    'source': inspection.inspection_source,
                    'status': inspection.status,
                    'result': inspection.result,
                    'quality_rating': float(inspection.quality_rating) if inspection.quality_rating else None,
                    'inspection_date': inspection.inspection_date.isoformat(),
                }
                for inspection in inspections.order_by('inspection_date')
            ]
        }
        
        return JsonResponse({
            'success': True,
            'summary': summary_data
        })
        
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid batch UUID format.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def receive_ai_report(request):
    """
    Receive AI-generated report from external AI service.
    This endpoint is called by the AI service when processing is complete.
    """
    try:
        data = json.loads(request.body)
        
        batch_uuid = data.get('batch_uuid')
        if not batch_uuid:
            return JsonResponse({
                'success': False,
                'message': 'Batch UUID is required.'
            })
        
        try:
            batch_uuid_obj = uuid.UUID(batch_uuid)
            equipment_batch = get_object_or_404(EquipmentBatch, batch_uuid=batch_uuid_obj)
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid batch UUID format.'
            })
        
        # Create or update AI Smart Report
        smart_report, created = AISmartReport.objects.get_or_create(
            equipment_batch=equipment_batch,
            defaults={
                'status': 'PROCESSING',
                'ai_model_version': data.get('model_version', '1.0'),
            }
        )
        
        if not created:
            smart_report.status = 'PROCESSING'
            smart_report.save()
        
        # Update report with AI data
        smart_report.executive_summary = data.get('executive_summary', '')
        smart_report.quality_assessment = data.get('quality_assessment', '')
        smart_report.defect_analysis = data.get('defect_analysis', {})
        smart_report.stage_comparison = data.get('stage_comparison', {})
        smart_report.recommendations = data.get('recommendations', [])
        smart_report.risk_assessment = data.get('risk_assessment', {})
        smart_report.compliance_status = data.get('compliance_status', {})
        smart_report.confidence_score = data.get('confidence_score')
        smart_report.processing_time_seconds = data.get('processing_time_seconds')
        smart_report.status = 'COMPLETED'
        smart_report.completed_at = timezone.now()
        smart_report.save()
        
        return JsonResponse({
            'success': True,
            'message': 'AI report received and saved successfully.',
            'report_id': smart_report.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing AI report: {str(e)}'
        })


def prepare_inspection_data_for_ai(equipment_batch, inspections):
    """
    Prepare inspection data for AI model processing.
    """
    # Group inspections by source
    vendor_inspections = []
    railway_auth_inspections = []
    worker_inspections = []
    
    for inspection in inspections:
        inspection_data = {
            'inspection_id': str(inspection.inspection_id),
            'stage': inspection.stage.name,
            'status': inspection.status,
            'result': inspection.result,
            'quality_rating': float(inspection.quality_rating) if inspection.quality_rating else None,
            'overall_score': float(inspection.overall_score) if inspection.overall_score else None,
            'findings': inspection.findings,
            'issues_found': inspection.issues_found,
            'recommendations': inspection.recommendations,
            'corrective_actions': inspection.corrective_actions,
            'inspection_date': inspection.inspection_date.isoformat(),
            'photos': []
        }
        
        # Add photos for this inspection
        photos = InspectionPhoto.objects.filter(inspection=inspection)
        for photo in photos:
            photo_data = {
                'photo_type': photo.photo_type,
                'image_url': photo.image.url,
                'caption': photo.caption,
                'description': photo.description,
                'qr_code_data': photo.qr_code_data,
                'qr_code_uuid': str(photo.qr_code_uuid) if photo.qr_code_uuid else None,
                'ai_tags': photo.ai_tags,
                'ai_analysis': photo.ai_analysis,
                'ai_confidence_score': float(photo.ai_confidence_score) if photo.ai_confidence_score else None,
                'uploaded_at': photo.uploaded_at.isoformat(),
                'uploaded_by': photo.uploaded_by.get_full_name(),
            }
            inspection_data['photos'].append(photo_data)
        
        # Add to appropriate source list
        if inspection.inspection_source == 'VENDOR':
            vendor_inspections.append(inspection_data)
        elif inspection.inspection_source == 'RAILWAY_AUTH':
            railway_auth_inspections.append(inspection_data)
        elif inspection.inspection_source == 'WORKER':
            worker_inspections.append(inspection_data)
    
    return {
        'equipment_batch': {
            'batch_uuid': str(equipment_batch.batch_uuid),
            'batch_name': equipment_batch.batch_name,
            'equipment_type': equipment_batch.equipment_type,
            'manufacturer': equipment_batch.manufacturer,
            'model_number': equipment_batch.model_number,
            'serial_number': equipment_batch.serial_number,
            'current_stage': equipment_batch.current_stage,
        },
        'vendor_inspections': vendor_inspections,
        'railway_auth_inspections': railway_auth_inspections,
        'worker_inspections': worker_inspections,
        'total_inspections': len(inspections),
        'total_photos': InspectionPhoto.objects.filter(inspection__in=inspections).count(),
    }


def send_to_ai_model(data):
    """
    Send data to AI model for processing.
    Replace this with actual AI service integration.
    """
    # This is a placeholder - replace with actual AI service call
    ai_endpoint = getattr(settings, 'AI_MODEL_ENDPOINT', 'http://localhost:8001/api/process-inspection/')
    
    try:
        # For now, return mock response
        return {
            'success': True,
            'executive_summary': f"Equipment batch {data['equipment_batch']['batch_name']} has been inspected across {data['total_inspections']} stages with {data['total_photos']} photos captured.",
            'quality_assessment': "Overall quality assessment based on inspection data.",
            'defect_analysis': {
                'total_defects': 0,
                'critical_defects': 0,
                'minor_defects': 0,
                'defect_locations': []
            },
            'stage_comparison': {
                'vendor_quality': 8.5,
                'railway_auth_quality': 8.2,
                'worker_quality': 8.8
            },
            'recommendations': [
                "Continue current quality standards",
                "Monitor equipment performance",
                "Schedule regular maintenance"
            ],
            'risk_assessment': {
                'risk_level': 'LOW',
                'risk_factors': [],
                'mitigation_actions': []
            },
            'compliance_status': {
                'standards_compliant': True,
                'certification_status': 'VALID',
                'compliance_score': 95
            },
            'model_version': '1.0',
            'confidence_score': 0.85,
            'processing_time': 45
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


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
