"""
Views for tracking and monitoring.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

from .models import TrackingEvent, InspectionRecord, QualityCheck, Alert
from parts.models import Part
from orders.models import PurchaseOrder


@login_required
def tracking_event_list_view(request):
    """
    List all tracking events.
    """
    events = TrackingEvent.objects.all().order_by('-event_date')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        events = events.filter(
            Q(part__part_number__icontains=search_query) |
            Q(part__name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Filter by event type
    event_type_filter = request.GET.get('event_type')
    if event_type_filter:
        events = events.filter(event_type=event_type_filter)
    
    paginator = Paginator(events, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'event_type_filter': event_type_filter,
        'event_type_choices': TrackingEvent.EVENT_TYPES,
    }
    return render(request, 'tracking/tracking_event_list.html', context)


@login_required
def tracking_event_detail_view(request, event_id):
    """
    Detailed view of a tracking event.
    """
    event = get_object_or_404(TrackingEvent, id=event_id)
    
    context = {
        'event': event,
    }
    return render(request, 'tracking/tracking_event_detail.html', context)


@login_required
def tracking_event_create_view(request):
    """
    Create a new tracking event.
    """
    if request.method == 'POST':
        # Handle form submission
        part_id = request.POST.get('part')
        event_type = request.POST.get('event_type')
        description = request.POST.get('description')
        location = request.POST.get('location')
        
        if part_id and event_type and description:
            part = get_object_or_404(Part, id=part_id)
            event = TrackingEvent.objects.create(
                part=part,
                event_type=event_type,
                description=description,
                location=location,
                recorded_by=request.user
            )
            messages.success(request, 'Tracking event created successfully!')
            return redirect('tracking_event_detail', event_id=event.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    parts = Part.objects.all()
    context = {
        'parts': parts,
        'event_type_choices': TrackingEvent.EVENT_TYPES,
    }
    return render(request, 'tracking/tracking_event_form.html', context)


@login_required
def inspection_list_view(request):
    """
    List all inspection records.
    """
    inspections = InspectionRecord.objects.all().order_by('-inspection_date')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        inspections = inspections.filter(
            Q(part__part_number__icontains=search_query) |
            Q(part__name__icontains=search_query) |
            Q(findings__icontains=search_query)
        )
    
    # Filter by result
    result_filter = request.GET.get('result')
    if result_filter:
        inspections = inspections.filter(result=result_filter)
    
    paginator = Paginator(inspections, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'result_filter': result_filter,
        'result_choices': InspectionRecord.INSPECTION_RESULTS,
    }
    return render(request, 'tracking/inspection_list.html', context)


@login_required
def inspection_detail_view(request, inspection_id):
    """
    Detailed view of an inspection record.
    """
    inspection = get_object_or_404(InspectionRecord, id=inspection_id)
    
    context = {
        'inspection': inspection,
    }
    return render(request, 'tracking/inspection_detail.html', context)


@login_required
def inspection_create_view(request):
    """
    Create a new inspection record.
    """
    if request.method == 'POST':
        # Handle form submission
        part_id = request.POST.get('part')
        inspection_type = request.POST.get('inspection_type')
        result = request.POST.get('result')
        findings = request.POST.get('findings')
        
        if part_id and inspection_type and result and findings:
            part = get_object_or_404(Part, id=part_id)
            inspection = InspectionRecord.objects.create(
                part=part,
                inspection_type=inspection_type,
                result=result,
                findings=findings,
                inspector=request.user
            )
            messages.success(request, 'Inspection record created successfully!')
            return redirect('inspection_detail', inspection_id=inspection.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    parts = Part.objects.all()
    context = {
        'parts': parts,
        'inspection_type_choices': InspectionRecord.INSPECTION_TYPES,
        'result_choices': InspectionRecord.INSPECTION_RESULTS,
    }
    return render(request, 'tracking/inspection_form.html', context)


@login_required
def quality_check_list_view(request):
    """
    List all quality checks.
    """
    checks = QualityCheck.objects.all().order_by('-check_date')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        checks = checks.filter(
            Q(check_number__icontains=search_query) |
            Q(part__part_number__icontains=search_query) |
            Q(order__order_number__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        checks = checks.filter(status=status_filter)
    
    paginator = Paginator(checks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': QualityCheck.CHECK_STATUS,
    }
    return render(request, 'tracking/quality_check_list.html', context)


@login_required
def quality_check_detail_view(request, check_id):
    """
    Detailed view of a quality check.
    """
    check = get_object_or_404(QualityCheck, id=check_id)
    
    context = {
        'check': check,
    }
    return render(request, 'tracking/quality_check_detail.html', context)


@login_required
def quality_check_create_view(request):
    """
    Create a new quality check.
    """
    if request.method == 'POST':
        # Handle form submission
        check_type = request.POST.get('check_type')
        part_id = request.POST.get('part')
        order_id = request.POST.get('order')
        remarks = request.POST.get('remarks')
        
        if check_type and (part_id or order_id):
            part = None
            order = None
            
            if part_id:
                part = get_object_or_404(Part, id=part_id)
            if order_id:
                order = get_object_or_404(PurchaseOrder, id=order_id)
            
            check = QualityCheck.objects.create(
                check_type=check_type,
                part=part,
                order=order,
                remarks=remarks,
                checked_by=request.user
            )
            messages.success(request, 'Quality check created successfully!')
            return redirect('quality_check_detail', check_id=check.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    parts = Part.objects.all()
    orders = PurchaseOrder.objects.all()
    context = {
        'parts': parts,
        'orders': orders,
        'check_type_choices': QualityCheck.CHECK_TYPES,
    }
    return render(request, 'tracking/quality_check_form.html', context)


@login_required
def alert_list_view(request):
    """
    List all alerts.
    """
    alerts = Alert.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        alerts = alerts.filter(
            Q(title__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        alerts = alerts.filter(priority=priority_filter)
    
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': Alert.ALERT_STATUS,
        'priority_choices': Alert.ALERT_PRIORITIES,
    }
    return render(request, 'tracking/alert_list.html', context)


@login_required
def alert_detail_view(request, alert_id):
    """
    Detailed view of an alert.
    """
    alert = get_object_or_404(Alert, id=alert_id)
    
    context = {
        'alert': alert,
    }
    return render(request, 'tracking/alert_detail.html', context)


@login_required
@require_http_methods(["POST"])
def alert_acknowledge_view(request, alert_id):
    """
    Acknowledge an alert.
    """
    alert = get_object_or_404(Alert, id=alert_id)
    alert.acknowledge(request.user)
    messages.success(request, 'Alert acknowledged successfully!')
    return redirect('alert_detail', alert_id=alert.id)


@login_required
@require_http_methods(["POST"])
def alert_resolve_view(request, alert_id):
    """
    Resolve an alert.
    """
    alert = get_object_or_404(Alert, id=alert_id)
    alert.resolve()
    messages.success(request, 'Alert resolved successfully!')
    return redirect('alert_detail', alert_id=alert.id)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_tracking_event_list(request):
    """
    API endpoint to list tracking events.
    """
    events = TrackingEvent.objects.all().order_by('-event_date')
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        events = events.filter(
            Q(part__part_number__icontains=search) |
            Q(description__icontains=search)
        )
    
    event_type = request.GET.get('event_type')
    if event_type:
        events = events.filter(event_type=event_type)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    events_page = events[start:end]
    
    data = []
    for event in events_page:
        data.append({
            'id': event.id,
            'part': {
                'id': event.part.id,
                'part_number': event.part.part_number,
                'name': event.part.name,
            },
            'event_type': event.event_type,
            'description': event.description,
            'location': event.location,
            'event_date': event.event_date,
            'recorded_by': event.recorded_by.get_full_name(),
        })
    
    return Response({
        'results': data,
        'count': events.count(),
        'page': page,
        'page_size': page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_tracking_event_detail(request, event_id):
    """
    API endpoint to get tracking event details.
    """
    try:
        event = TrackingEvent.objects.get(id=event_id)
        
        data = {
            'id': event.id,
            'part': {
                'id': event.part.id,
                'part_number': event.part.part_number,
                'name': event.part.name,
            },
            'event_type': event.event_type,
            'description': event.description,
            'location': event.location,
            'railway_zone': event.railway_zone,
            'railway_division': event.railway_division,
            'track_section': event.track_section,
            'kilometer_marker': event.kilometer_marker,
            'latitude': event.latitude,
            'longitude': event.longitude,
            'event_date': event.event_date,
            'recorded_by': event.recorded_by.get_full_name(),
            'related_order': {
                'id': event.related_order.id,
                'order_number': event.related_order.order_number,
            } if event.related_order else None,
            'metadata': event.metadata,
        }
        
        return Response(data)
    
    except TrackingEvent.DoesNotExist:
        return Response(
            {'error': 'Tracking event not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_inspection_list(request):
    """
    API endpoint to list inspection records.
    """
    inspections = InspectionRecord.objects.all().order_by('-inspection_date')
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        inspections = inspections.filter(
            Q(part__part_number__icontains=search) |
            Q(findings__icontains=search)
        )
    
    result = request.GET.get('result')
    if result:
        inspections = inspections.filter(result=result)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    inspections_page = inspections[start:end]
    
    data = []
    for inspection in inspections_page:
        data.append({
            'id': inspection.id,
            'part': {
                'id': inspection.part.id,
                'part_number': inspection.part.part_number,
                'name': inspection.part.name,
            },
            'inspection_type': inspection.inspection_type,
            'result': inspection.result,
            'score': inspection.score,
            'findings': inspection.findings,
            'inspection_date': inspection.inspection_date,
            'inspector': inspection.inspector.get_full_name(),
        })
    
    return Response({
        'results': data,
        'count': inspections.count(),
        'page': page,
        'page_size': page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_quality_check_list(request):
    """
    API endpoint to list quality checks.
    """
    checks = QualityCheck.objects.all().order_by('-check_date')
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        checks = checks.filter(
            Q(check_number__icontains=search) |
            Q(part__part_number__icontains=search) |
            Q(order__order_number__icontains=search)
        )
    
    status_filter = request.GET.get('status')
    if status_filter:
        checks = checks.filter(status=status_filter)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    checks_page = checks[start:end]
    
    data = []
    for check in checks_page:
        data.append({
            'id': check.id,
            'check_number': check.check_number,
            'check_type': check.check_type,
            'status': check.status,
            'passed': check.passed,
            'score': check.score,
            'part': {
                'id': check.part.id,
                'part_number': check.part.part_number,
                'name': check.part.name,
            } if check.part else None,
            'order': {
                'id': check.order.id,
                'order_number': check.order.order_number,
            } if check.order else None,
            'check_date': check.check_date,
            'checked_by': check.checked_by.get_full_name(),
        })
    
    return Response({
        'results': data,
        'count': checks.count(),
        'page': page,
        'page_size': page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_alert_list(request):
    """
    API endpoint to list alerts.
    """
    alerts = Alert.objects.all().order_by('-created_at')
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        alerts = alerts.filter(
            Q(title__icontains=search) |
            Q(message__icontains=search)
        )
    
    status_filter = request.GET.get('status')
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    priority = request.GET.get('priority')
    if priority:
        alerts = alerts.filter(priority=priority)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    alerts_page = alerts[start:end]
    
    data = []
    for alert in alerts_page:
        data.append({
            'id': alert.id,
            'alert_type': alert.alert_type,
            'priority': alert.priority,
            'status': alert.status,
            'title': alert.title,
            'message': alert.message,
            'part': {
                'id': alert.part.id,
                'part_number': alert.part.part_number,
                'name': alert.part.name,
            } if alert.part else None,
            'order': {
                'id': alert.order.id,
                'order_number': alert.order.order_number,
            } if alert.order else None,
            'created_at': alert.created_at,
            'created_by': alert.created_by.get_full_name(),
            'acknowledged_by': alert.acknowledged_by.get_full_name() if alert.acknowledged_by else None,
            'acknowledged_at': alert.acknowledged_at,
        })
    
    return Response({
        'results': data,
        'count': alerts.count(),
        'page': page,
        'page_size': page_size,
    })
