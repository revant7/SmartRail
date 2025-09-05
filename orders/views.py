"""
Views for orders management.
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

from .models import Project, Vendor, PurchaseOrder, OrderLineItem, OrderDocument, OrderStatusHistory
from .forms import ProjectForm, VendorForm, PurchaseOrderForm, OrderLineItemFormSet


@login_required
def project_list_view(request):
    """
    List all projects.
    """
    projects = Project.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        projects = projects.filter(
            Q(project_code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Project.PROJECT_STATUS_CHOICES,
    }
    return render(request, 'orders/project_list.html', context)


@login_required
def project_detail_view(request, project_id):
    """
    Detailed view of a project.
    """
    project = get_object_or_404(Project, id=project_id)
    orders = project.orders.all().order_by('-created_at')
    
    context = {
        'project': project,
        'orders': orders,
    }
    return render(request, 'orders/project_detail.html', context)


@login_required
def vendor_list_view(request):
    """
    List all vendors.
    """
    vendors = Vendor.objects.all().order_by('company_name')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        vendors = vendors.filter(
            Q(company_name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        vendors = vendors.filter(status=status_filter)
    
    paginator = Paginator(vendors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Vendor.VENDOR_STATUS_CHOICES,
    }
    return render(request, 'orders/vendor_list.html', context)


@login_required
def vendor_detail_view(request, vendor_id):
    """
    Detailed view of a vendor.
    """
    vendor = get_object_or_404(Vendor, id=vendor_id)
    orders = vendor.orders.all().order_by('-created_at')
    
    context = {
        'vendor': vendor,
        'orders': orders,
    }
    return render(request, 'orders/vendor_detail.html', context)


@login_required
def order_list_view(request):
    """
    List all purchase orders.
    """
    orders = PurchaseOrder.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(vendor__company_name__icontains=search_query) |
            Q(project__name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        orders = orders.filter(priority=priority_filter)
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': PurchaseOrder.ORDER_STATUS_CHOICES,
        'priority_choices': PurchaseOrder.PRIORITY_CHOICES,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail_view(request, order_id):
    """
    Detailed view of a purchase order.
    """
    order = get_object_or_404(PurchaseOrder, id=order_id)
    line_items = order.line_items.all()
    documents = order.documents.all()
    status_history = order.status_history.all()
    
    context = {
        'order': order,
        'line_items': line_items,
        'documents': documents,
        'status_history': status_history,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_create_view(request):
    """
    Create a new purchase order.
    """
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            
            # Handle line items
            line_item_formset = OrderLineItemFormSet(
                request.POST,
                instance=order
            )
            if line_item_formset.is_valid():
                line_item_formset.save()
                order.calculate_totals()
            
            messages.success(request, f'Order {order.order_number} created successfully!')
            return redirect('order_detail', order_id=order.id)
    else:
        form = PurchaseOrderForm()
        line_item_formset = OrderLineItemFormSet()
    
    context = {
        'form': form,
        'line_item_formset': line_item_formset,
    }
    return render(request, 'orders/order_form.html', context)


@login_required
def order_update_view(request, order_id):
    """
    Update an existing purchase order.
    """
    order = get_object_or_404(PurchaseOrder, id=order_id)
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            
            # Handle line items
            line_item_formset = OrderLineItemFormSet(
                request.POST,
                instance=order
            )
            if line_item_formset.is_valid():
                line_item_formset.save()
                order.calculate_totals()
            
            messages.success(request, f'Order {order.order_number} updated successfully!')
            return redirect('order_detail', order_id=order.id)
    else:
        form = PurchaseOrderForm(instance=order)
        line_item_formset = OrderLineItemFormSet(instance=order)
    
    context = {
        'form': form,
        'line_item_formset': line_item_formset,
        'order': order,
    }
    return render(request, 'orders/order_form.html', context)


@login_required
@require_http_methods(["POST"])
def order_approve_view(request, order_id):
    """
    Approve a purchase order.
    """
    order = get_object_or_404(PurchaseOrder, id=order_id)
    
    if not (request.user.is_admin() or request.user.is_railway_authority()):
        messages.error(request, 'You do not have permission to approve orders.')
        return redirect('order_detail', order_id=order.id)
    
    if order.status != 'PENDING_APPROVAL':
        messages.error(request, 'This order is not pending approval.')
        return redirect('order_detail', order_id=order.id)
    
    order.status = 'APPROVED'
    order.approved_by = request.user
    order.approved_at = timezone.now()
    order.save()
    
    # Record status change
    OrderStatusHistory.objects.create(
        order=order,
        from_status='PENDING_APPROVAL',
        to_status='APPROVED',
        changed_by=request.user,
        notes='Order approved'
    )
    
    messages.success(request, f'Order {order.order_number} approved successfully!')
    return redirect('order_detail', order_id=order.id)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_order_list(request):
    """
    API endpoint to list orders.
    """
    orders = PurchaseOrder.objects.all().order_by('-created_at')
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(vendor__company_name__icontains=search)
        )
    
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    orders_page = orders[start:end]
    
    data = []
    for order in orders_page:
        data.append({
            'id': order.id,
            'order_number': order.order_number,
            'project': {
                'id': order.project.id,
                'name': order.project.name,
                'code': order.project.project_code,
            },
            'vendor': {
                'id': order.vendor.id,
                'company_name': order.vendor.company_name,
            },
            'status': order.status,
            'priority': order.priority,
            'total_amount': order.total_amount,
            'currency': order.currency,
            'created_at': order.created_at,
            'url': f'/orders/{order.id}/',
        })
    
    return Response({
        'results': data,
        'count': orders.count(),
        'page': page,
        'page_size': page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_order_detail(request, order_id):
    """
    API endpoint to get order details.
    """
    try:
        order = PurchaseOrder.objects.get(id=order_id)
        
        # Get line items
        line_items = []
        for item in order.line_items.all():
            line_items.append({
                'id': item.id,
                'part_number': item.part_number,
                'part_name': item.part_name,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price,
                'status': item.status,
                'expected_delivery_date': item.expected_delivery_date,
                'actual_delivery_date': item.actual_delivery_date,
            })
        
        # Get status history
        status_history = []
        for history in order.status_history.all():
            status_history.append({
                'id': history.id,
                'from_status': history.from_status,
                'to_status': history.to_status,
                'changed_by': history.changed_by.get_full_name(),
                'changed_at': history.changed_at,
                'notes': history.notes,
            })
        
        data = {
            'id': order.id,
            'order_number': order.order_number,
            'project': {
                'id': order.project.id,
                'name': order.project.name,
                'code': order.project.project_code,
            },
            'vendor': {
                'id': order.vendor.id,
                'company_name': order.vendor.company_name,
                'contact_person': order.vendor.contact_person,
                'email': order.vendor.email,
                'phone': order.vendor.phone,
            },
            'status': order.status,
            'priority': order.priority,
            'subtotal': order.subtotal,
            'tax_amount': order.tax_amount,
            'total_amount': order.total_amount,
            'currency': order.currency,
            'delivery_address': order.delivery_address,
            'expected_delivery_date': order.expected_delivery_date,
            'actual_delivery_date': order.actual_delivery_date,
            'payment_terms': order.payment_terms,
            'delivery_terms': order.delivery_terms,
            'warranty_period': order.warranty_period,
            'created_by': order.created_by.get_full_name(),
            'approved_by': order.approved_by.get_full_name() if order.approved_by else None,
            'approved_at': order.approved_at,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
            'line_items': line_items,
            'status_history': status_history,
        }
        
        return Response(data)
    
    except PurchaseOrder.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_vendor_list(request):
    """
    API endpoint to list vendors.
    """
    vendors = Vendor.objects.filter(status='ACTIVE').order_by('company_name')
    
    data = []
    for vendor in vendors:
        data.append({
            'id': vendor.id,
            'vendor_code': vendor.vendor_code,
            'company_name': vendor.company_name,
            'contact_person': vendor.contact_person,
            'email': vendor.email,
            'phone': vendor.phone,
            'vendor_type': vendor.vendor_type,
            'rating': vendor.rating,
            'specializations': vendor.specializations,
        })
    
    return Response(data)
