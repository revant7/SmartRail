"""
Views for parts management.
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

from .models import Part, PartCategory, PartSpecification, PartImage, PartDocument, PartMaintenanceRecord
from .forms import PartForm, PartSpecificationFormSet
from core.models import QRCodeScan


@login_required
def part_list_view(request):
    """
    List all parts with filtering and search.
    """
    parts = Part.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        parts = parts.filter(
            Q(part_number__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        parts = parts.filter(category_id=category_filter)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        parts = parts.filter(status=status_filter)
    
    # Filter by location
    location_filter = request.GET.get('location')
    if location_filter:
        parts = parts.filter(current_location__icontains=location_filter)
    
    paginator = Paginator(parts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = PartCategory.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'location_filter': location_filter,
        'status_choices': Part.STATUS_CHOICES,
    }
    return render(request, 'parts/part_list.html', context)


@login_required
def part_detail_view(request, part_id):
    """
    Detailed view of a part.
    """
    part = get_object_or_404(Part, id=part_id)
    
    # Get related data
    specifications = part.specifications.all()
    images = part.images.all()
    documents = part.documents.all()
    maintenance_records = part.maintenance_records.all()[:10]
    tracking_events = part.tracking_events.all()[:10]
    
    context = {
        'part': part,
        'specifications': specifications,
        'images': images,
        'documents': documents,
        'maintenance_records': maintenance_records,
        'tracking_events': tracking_events,
    }
    return render(request, 'parts/part_detail.html', context)


@login_required
def part_create_view(request):
    """
    Create a new part.
    """
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES)
        if form.is_valid():
            part = form.save(commit=False)
            part.created_by = request.user
            part.save()
            
            # Handle specifications
            specification_formset = PartSpecificationFormSet(
                request.POST,
                instance=part
            )
            if specification_formset.is_valid():
                specification_formset.save()
            
            messages.success(request, f'Part {part.part_number} created successfully!')
            return redirect('part_detail', part_id=part.id)
    else:
        form = PartForm()
        specification_formset = PartSpecificationFormSet()
    
    context = {
        'form': form,
        'specification_formset': specification_formset,
    }
    return render(request, 'parts/part_form.html', context)


@login_required
def part_update_view(request, part_id):
    """
    Update an existing part.
    """
    part = get_object_or_404(Part, id=part_id)
    
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES, instance=part)
        if form.is_valid():
            part = form.save(commit=False)
            part.updated_by = request.user
            part.save()
            
            # Handle specifications
            specification_formset = PartSpecificationFormSet(
                request.POST,
                instance=part
            )
            if specification_formset.is_valid():
                specification_formset.save()
            
            messages.success(request, f'Part {part.part_number} updated successfully!')
            return redirect('part_detail', part_id=part.id)
    else:
        form = PartForm(instance=part)
        specification_formset = PartSpecificationFormSet(instance=part)
    
    context = {
        'form': form,
        'specification_formset': specification_formset,
        'part': part,
    }
    return render(request, 'parts/part_form.html', context)


@login_required
@require_http_methods(["POST"])
def part_delete_view(request, part_id):
    """
    Delete a part.
    """
    part = get_object_or_404(Part, id=part_id)
    
    if not (request.user.is_admin() or request.user.is_railway_authority()):
        messages.error(request, 'You do not have permission to delete parts.')
        return redirect('part_detail', part_id=part.id)
    
    part_number = part.part_number
    part.delete()
    
    messages.success(request, f'Part {part_number} deleted successfully!')
    return redirect('part_list')


@login_required
def part_qr_view(request, part_id):
    """
    Display QR code for a part.
    """
    part = get_object_or_404(Part, id=part_id)
    
    # Generate QR code if it doesn't exist
    if not part.qr_code:
        part.generate_qr_code()
    
    context = {
        'part': part,
    }
    return render(request, 'parts/part_qr.html', context)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_part_list(request):
    """
    API endpoint to list parts.
    """
    parts = Part.objects.all().order_by('-created_at')
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        parts = parts.filter(
            Q(part_number__icontains=search) |
            Q(name__icontains=search) |
            Q(manufacturer__icontains=search)
        )
    
    category = request.GET.get('category')
    if category:
        parts = parts.filter(category_id=category)
    
    status_filter = request.GET.get('status')
    if status_filter:
        parts = parts.filter(status=status_filter)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    parts_page = parts[start:end]
    
    data = []
    for part in parts_page:
        data.append({
            'id': part.id,
            'part_number': part.part_number,
            'name': part.name,
            'manufacturer': part.manufacturer,
            'status': part.status,
            'current_location': part.current_location,
            'qr_code_data': part.qr_code_data,
            'url': part.get_absolute_url(),
        })
    
    return Response({
        'results': data,
        'count': parts.count(),
        'page': page,
        'page_size': page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_part_detail(request, part_id):
    """
    API endpoint to get part details.
    """
    try:
        part = Part.objects.get(id=part_id)
        
        # Get specifications
        specifications = []
        for spec in part.specifications.all():
            specifications.append({
                'name': spec.name,
                'value': spec.value,
                'unit': spec.unit,
            })
        
        # Get recent maintenance records
        maintenance_records = []
        for record in part.maintenance_records.all()[:5]:
            maintenance_records.append({
                'id': record.id,
                'type': record.maintenance_type,
                'description': record.description,
                'performed_by': record.performed_by.get_full_name(),
                'performed_date': record.performed_date,
                'cost': record.cost,
            })
        
        # Get recent tracking events
        tracking_events = []
        for event in part.tracking_events.all()[:5]:
            tracking_events.append({
                'id': event.id,
                'type': event.event_type,
                'description': event.description,
                'location': event.location,
                'event_date': event.event_date,
                'recorded_by': event.recorded_by.get_full_name(),
            })
        
        data = {
            'id': part.id,
            'part_number': part.part_number,
            'name': part.name,
            'description': part.description,
            'manufacturer': part.manufacturer,
            'model_number': part.model_number,
            'serial_number': part.serial_number,
            'material': part.material,
            'weight': part.weight,
            'dimensions': part.dimensions,
            'status': part.status,
            'installation_date': part.installation_date,
            'expected_lifespan': part.expected_lifespan,
            'last_inspection_date': part.last_inspection_date,
            'next_inspection_date': part.next_inspection_date,
            'current_location': part.current_location,
            'railway_zone': part.railway_zone,
            'railway_division': part.railway_division,
            'track_section': part.track_section,
            'kilometer_marker': part.kilometer_marker,
            'unit_cost': part.unit_cost,
            'currency': part.currency,
            'qr_code_data': part.qr_code_data,
            'qr_code_url': part.qr_code.url if part.qr_code else None,
            'specifications': specifications,
            'maintenance_records': maintenance_records,
            'tracking_events': tracking_events,
            'created_at': part.created_at,
            'updated_at': part.updated_at,
        }
        
        return Response(data)
    
    except Part.DoesNotExist:
        return Response(
            {'error': 'Part not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_part_by_qr(request, qr_data):
    """
    API endpoint to get part by QR code data.
    """
    try:
        part = Part.objects.get(qr_code_data=qr_data)
        
        # Log the scan
        QRCodeScan.objects.create(
            qr_code_data=qr_data,
            scanned_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            scan_result={'status': 'success', 'part_id': part.id}
        )
        
        # Return part data
        data = {
            'id': part.id,
            'part_number': part.part_number,
            'name': part.name,
            'manufacturer': part.manufacturer,
            'status': part.status,
            'current_location': part.current_location,
            'installation_date': part.installation_date,
            'last_inspection_date': part.last_inspection_date,
            'next_inspection_date': part.next_inspection_date,
            'is_due_for_inspection': part.is_due_for_inspection(),
            'age_in_months': part.get_age_in_months(),
            'url': part.get_absolute_url(),
        }
        
        return Response(data)
    
    except Part.DoesNotExist:
        # Log failed scan
        QRCodeScan.objects.create(
            qr_code_data=qr_data,
            scanned_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            scan_result={'status': 'not_found'}
        )
        
        return Response(
            {'error': 'Part not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_part_categories(request):
    """
    API endpoint to get part categories.
    """
    categories = PartCategory.objects.filter(is_active=True)
    
    data = []
    for category in categories:
        data.append({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'parent_category': category.parent_category.name if category.parent_category else None,
        })
    
    return Response(data)
