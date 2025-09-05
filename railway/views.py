"""
Views for railway management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import (
    RailwayZone, RailwayDivision, RailwayLocation, Requirement, 
    VendorRequest, RequirementInspection, RequirementStatusHistory
)
from .forms import (
    RequirementForm, VendorRequestForm, RequirementInspectionForm
)
from notifications.services import RequirementNotificationService


@login_required
def requirement_list(request):
    """
    List requirements based on user type.
    """
    user = request.user
    
    if user.is_railway_authority():
        # Show requirements created by this authority
        requirements = Requirement.objects.filter(created_by=user)
    elif user.is_vendor():
        # Show requirements assigned to this vendor or available for bidding
        requirements = Requirement.objects.filter(
            Q(assigned_vendor=user) | 
            Q(status='INACTIVE', assigned_vendor__isnull=True)
        )
    elif user.is_railway_worker():
        # Show requirements in worker's zone/division
        requirements = Requirement.objects.all()  # Filter by worker's location
    else:
        # Software staff can see all requirements
        requirements = Requirement.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        requirements = requirements.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        requirements = requirements.filter(status=status_filter)
    
    # Filter by zone
    zone_filter = request.GET.get('zone')
    if zone_filter:
        requirements = requirements.filter(zone_id=zone_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        requirements = requirements.filter(priority=priority_filter)
    
    paginator = Paginator(requirements.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'requirements': page_obj,
        'status_choices': Requirement.STATUS_CHOICES,
        'priority_choices': Requirement.PRIORITY_CHOICES,
        'zones': RailwayZone.objects.filter(is_active=True),
        'search_query': search_query,
        'status_filter': status_filter,
        'zone_filter': zone_filter,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'railway/requirement_list.html', context)


@login_required
def requirement_detail(request, requirement_id):
    """
    Detail view for a requirement.
    """
    requirement = get_object_or_404(Requirement, id=requirement_id)
    user = request.user
    
    # Check permissions
    if user.is_railway_authority() and requirement.created_by != user:
        messages.error(request, 'You do not have permission to view this requirement.')
        return redirect('railway:requirement_list')
    
    # Get vendor requests for this requirement
    vendor_requests = VendorRequest.objects.filter(requirement=requirement)
    
    # Get inspections
    inspections = RequirementInspection.objects.filter(requirement=requirement)
    
    # Get status history
    status_history = RequirementStatusHistory.objects.filter(requirement=requirement)
    
    context = {
        'requirement': requirement,
        'vendor_requests': vendor_requests,
        'inspections': inspections,
        'status_history': status_history,
        'can_edit': user.is_railway_authority() and requirement.created_by == user,
        'can_request': user.is_vendor() and requirement.status == 'INACTIVE' and not requirement.assigned_vendor,
        'can_inspect': user.is_railway_worker() or user.is_railway_authority(),
    }
    
    return render(request, 'railway/requirement_detail.html', context)


@login_required
def create_requirement(request):
    """
    Create a new requirement (Railway Authority only).
    """
    if not request.user.is_railway_authority():
        messages.error(request, 'You do not have permission to create requirements.')
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = RequirementForm(request.POST)
        if form.is_valid():
            # Check for duplicate requirement created by same user in last 5 minutes
            title = form.cleaned_data.get('title')
            recent_duplicate = Requirement.objects.filter(
                title__iexact=title,
                created_by=request.user,
                created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
            ).first()
            
            if recent_duplicate:
                messages.warning(request, 'A similar requirement was created recently. Please check if this is a duplicate.')
                return redirect('railway:requirement_detail', requirement_id=recent_duplicate.id)
            
            requirement = form.save(commit=False)
            requirement.created_by = request.user
            requirement.save()
            
            # Send notifications to vendors
            RequirementNotificationService.notify_new_requirement(requirement)
            
            messages.success(request, 'Requirement created successfully!')
            return redirect('railway:requirement_detail', requirement_id=requirement.id)
    else:
        form = RequirementForm()
    
    context = {
        'form': form,
        'zones': RailwayZone.objects.filter(is_active=True),
    }
    
    return render(request, 'railway/create_requirement.html', context)


@login_required
def edit_requirement(request, requirement_id):
    """
    Edit a requirement (Railway Authority only).
    """
    requirement = get_object_or_404(Requirement, id=requirement_id)
    
    if not (request.user.is_railway_authority() and requirement.created_by == request.user):
        messages.error(request, 'You do not have permission to edit this requirement.')
        return redirect('railway:requirement_detail', requirement_id=requirement_id)
    
    if request.method == 'POST':
        form = RequirementForm(request.POST, instance=requirement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Requirement updated successfully!')
            return redirect('railway:requirement_detail', requirement_id=requirement.id)
    else:
        form = RequirementForm(instance=requirement)
    
    context = {
        'form': form,
        'requirement': requirement,
        'zones': RailwayZone.objects.filter(is_active=True),
    }
    
    return render(request, 'railway/edit_requirement.html', context)


@login_required
def vendor_request_list(request):
    """
    List vendor requests.
    """
    user = request.user
    
    if user.is_railway_authority():
        # Show requests for requirements created by this authority
        vendor_requests = VendorRequest.objects.filter(
            requirement__created_by=user
        )
    elif user.is_vendor():
        # Show requests made by this vendor
        vendor_requests = VendorRequest.objects.filter(vendor=user)
    else:
        # Software staff can see all requests
        vendor_requests = VendorRequest.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        vendor_requests = vendor_requests.filter(status=status_filter)
    
    paginator = Paginator(vendor_requests.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'vendor_requests': page_obj,
        'status_choices': VendorRequest.STATUS_CHOICES,
        'status_filter': status_filter,
    }
    
    return render(request, 'railway/vendor_request_list.html', context)


@login_required
def create_vendor_request(request, requirement_id):
    """
    Create a vendor request for a requirement.
    """
    requirement = get_object_or_404(Requirement, id=requirement_id)
    
    if not (request.user.is_vendor() and requirement.status == 'INACTIVE' and not requirement.assigned_vendor):
        messages.error(request, 'You cannot request this requirement.')
        return redirect('railway:requirement_detail', requirement_id=requirement_id)
    
    # Check if vendor already has a request for this requirement
    existing_request = VendorRequest.objects.filter(
        requirement=requirement,
        vendor=request.user
    ).first()
    
    if existing_request:
        messages.info(request, 'You have already submitted a request for this requirement.')
        return redirect('railway:requirement_detail', requirement_id=requirement_id)
    
    if request.method == 'POST':
        form = VendorRequestForm(request.POST)
        if form.is_valid():
            vendor_request = form.save(commit=False)
            vendor_request.requirement = requirement
            vendor_request.vendor = request.user
            vendor_request.save()
            
            messages.success(request, 'Vendor request submitted successfully!')
            return redirect('railway:requirement_detail', requirement_id=requirement_id)
    else:
        form = VendorRequestForm()
    
    context = {
        'form': form,
        'requirement': requirement,
    }
    
    return render(request, 'railway/create_vendor_request.html', context)


@login_required
@require_http_methods(["POST"])
def approve_vendor_request(request, request_id):
    """
    Approve a vendor request (Railway Authority only).
    """
    vendor_request = get_object_or_404(VendorRequest, id=request_id)
    
    if not (request.user.is_railway_authority() and 
            vendor_request.requirement.created_by == request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if vendor_request.status != 'PENDING':
        return JsonResponse({'error': 'Request is not pending'}, status=400)
    
    # Update vendor request status
    vendor_request.status = 'APPROVED'
    vendor_request.reviewed_by = request.user
    vendor_request.reviewed_at = timezone.now()
    vendor_request.save()
    
    # Assign requirement to vendor
    requirement = vendor_request.requirement
    requirement.assigned_vendor = vendor_request.vendor
    requirement.status = 'ACTIVE'
    requirement.assigned_at = timezone.now()
    requirement.save()
    
    # Create status history
    RequirementStatusHistory.objects.create(
        requirement=requirement,
        from_status='INACTIVE',
        to_status='ACTIVE',
        changed_by=request.user,
        notes=f'Assigned to vendor {vendor_request.vendor.get_full_name()}'
    )
    
    # Send notifications
    RequirementNotificationService.notify_requirement_assigned(requirement, vendor_request.vendor)
    
    return JsonResponse({
        'success': True,
        'message': 'Vendor request approved successfully'
    })


@login_required
@require_http_methods(["POST"])
def reject_vendor_request(request, request_id):
    """
    Reject a vendor request (Railway Authority only).
    """
    vendor_request = get_object_or_404(VendorRequest, id=request_id)
    
    if not (request.user.is_railway_authority() and 
            vendor_request.requirement.created_by == request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if vendor_request.status != 'PENDING':
        return JsonResponse({'error': 'Request is not pending'}, status=400)
    
    # Update vendor request status
    vendor_request.status = 'REJECTED'
    vendor_request.reviewed_by = request.user
    vendor_request.reviewed_at = timezone.now()
    vendor_request.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Vendor request rejected'
    })


@login_required
def update_requirement_status(request, requirement_id):
    """
    Update requirement status.
    """
    requirement = get_object_or_404(Requirement, id=requirement_id)
    user = request.user
    
    # Check permissions
    can_update = (
        (user.is_railway_authority() and requirement.created_by == user) or
        (user.is_vendor() and requirement.assigned_vendor == user) or
        user.is_railway_worker()
    )
    
    if not can_update:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status not in [choice[0] for choice in Requirement.STATUS_CHOICES]:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        old_status = requirement.status
        requirement.status = new_status
        requirement.save()
        
        # Create status history
        RequirementStatusHistory.objects.create(
            requirement=requirement,
            from_status=old_status,
            to_status=new_status,
            changed_by=user,
            notes=notes
        )
        
        # Send notifications
        RequirementNotificationService.notify_status_change(
            requirement, old_status, new_status, user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Status updated successfully'
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def create_inspection(request, requirement_id):
    """
    Create an inspection record.
    """
    requirement = get_object_or_404(Requirement, id=requirement_id)
    
    if not (request.user.is_railway_worker() or request.user.is_railway_authority()):
        messages.error(request, 'You do not have permission to create inspections.')
        return redirect('railway:requirement_detail', requirement_id=requirement_id)
    
    if request.method == 'POST':
        form = RequirementInspectionForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.requirement = requirement
            inspection.inspected_by = request.user
            inspection.save()
            
            messages.success(request, 'Inspection record created successfully!')
            return redirect('railway:requirement_detail', requirement_id=requirement_id)
    else:
        form = RequirementInspectionForm()
    
    context = {
        'form': form,
        'requirement': requirement,
    }
    
    return render(request, 'railway/create_inspection.html', context)


@login_required
def qr_tracking(request):
    """
    QR code tracking page with scanner and manual entry.
    """
    # Get recent scans for the current user
    from core.models import QRCodeScan
    recent_scans = QRCodeScan.objects.filter(
        scanned_by=request.user
    ).order_by('-scan_timestamp')[:5]
    
    context = {
        'recent_scans': recent_scans,
    }
    
    return render(request, 'railway/qr_tracking.html', context)


@login_required
def qr_track(request, uuid):
    """
    Track requirement by UUID from QR code.
    """
    try:
        requirement = Requirement.objects.get(requirement_id=uuid)
        
        # Log the scan
        from core.models import QRCodeScan
        QRCodeScan.objects.create(
            qr_code_data=str(uuid),
            scanned_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            scan_result={
                'requirement_found': True, 
                'requirement_id': requirement.id,
                'requirement_title': requirement.title
            }
        )
        
        # Redirect to requirement detail page
        return redirect('railway:requirement_detail', requirement_id=requirement.id)
        
    except Requirement.DoesNotExist:
        messages.error(request, f'Requirement with UUID "{uuid}" not found.')
        return redirect('railway:qr_tracking')
    except Exception as e:
        messages.error(request, f'Error tracking requirement: {str(e)}')
        return redirect('railway:qr_tracking')


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_requirement_detail(request, requirement_id):
    """
    API endpoint to get requirement details.
    """
    requirement = get_object_or_404(Requirement, id=requirement_id)
    
    data = {
        'id': requirement.id,
        'requirement_id': str(requirement.requirement_id),
        'title': requirement.title,
        'description': requirement.description,
        'category': requirement.category,
        'status': requirement.status,
        'priority': requirement.priority,
        'zone': {
            'id': requirement.zone.id,
            'name': requirement.zone.name,
        },
        'division': {
            'id': requirement.division.id,
            'name': requirement.division.name,
        },
        'location': requirement.location,
        'deadline_date': requirement.deadline_date,
        'days_remaining': requirement.get_days_remaining(),
        'is_overdue': requirement.is_overdue(),
        'assigned_vendor': {
            'id': requirement.assigned_vendor.id,
            'name': requirement.assigned_vendor.get_full_name(),
        } if requirement.assigned_vendor else None,
        'created_by': {
            'id': requirement.created_by.id,
            'name': requirement.created_by.get_full_name(),
        },
        'qr_code_url': requirement.qr_code.url if requirement.qr_code else None,
    }
    
    return Response(data)


@api_view(['GET'])
def api_scan_qr_code(request, requirement_uuid):
    """
    API endpoint for QR code scanning.
    """
    try:
        requirement = Requirement.objects.get(requirement_id=requirement_uuid)
        
        # Log the scan
        from core.models import QRCodeScan
        QRCodeScan.objects.create(
            qr_code_data=str(requirement_uuid),
            scanned_by=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            scan_result={'requirement_found': True, 'requirement_id': requirement.id}
        )
        
        data = {
            'success': True,
            'type': 'railway_requirement',
            'requirement': {
                'id': requirement.id,
                'title': requirement.title,
                'status': requirement.status,
                'zone': requirement.zone.name,
                'division': requirement.division.name,
                'location': requirement.location,
            }
        }
        
        return Response(data)
        
    except Requirement.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Requirement not found'
        }, status=404)


@api_view(['GET'])
def api_divisions(request):
    """
    API endpoint to get divisions by zone.
    """
    zone_id = request.GET.get('zone')
    if not zone_id:
        return Response({'divisions': []})
    
    try:
        divisions = RailwayDivision.objects.filter(
            zone_id=zone_id, 
            is_active=True
        ).values('id', 'name', 'division_code')
        return Response({'divisions': list(divisions)})
    except ValueError:
        return Response({'divisions': []})


@api_view(['GET'])
def api_locations(request):
    """
    API endpoint to get locations by division.
    """
    division_id = request.GET.get('division')
    if not division_id:
        return Response({'locations': []})
    
    try:
        locations = RailwayLocation.objects.filter(
            division_id=division_id, 
            is_active=True
        ).values('id', 'name', 'location_code', 'location_type')
        return Response({'locations': list(locations)})
    except ValueError:
        return Response({'locations': []})
