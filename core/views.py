"""
Core views for the QRAIL system.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

from accounts.models import User
from parts.models import Part, PartCategory
from orders.models import PurchaseOrder, Project
from tracking.models import TrackingEvent, Alert, InspectionRecord
from core.models import QRCodeScan
from notifications.models import Notification


@login_required
def dashboard_view(request):
    """
    Main dashboard view.
    """
    user = request.user
    
    # Get recent activities based on user type
    recent_parts = Part.objects.all()[:5]
    recent_orders = PurchaseOrder.objects.all()[:5]
    recent_alerts = Alert.objects.filter(
        Q(target_users=user) | Q(target_users__isnull=True)
    ).filter(status='ACTIVE')[:5]
    
    # Get statistics
    stats = {
        'total_parts': Part.objects.count(),
        'active_parts': Part.objects.filter(status='ACTIVE').count(),
        'total_orders': PurchaseOrder.objects.count(),
        'pending_orders': PurchaseOrder.objects.filter(
            status__in=['DRAFT', 'PENDING_APPROVAL']
        ).count(),
        'active_alerts': Alert.objects.filter(status='ACTIVE').count(),
        'unread_notifications': Notification.objects.filter(
            user=user, is_read=False
        ).count(),
    }
    
    # Get user-specific data
    if user.is_vendor():
        stats['my_orders'] = PurchaseOrder.objects.filter(vendor__contact_person=user).count()
    elif user.is_railway_employee() or user.is_railway_authority():
        stats['my_parts'] = Part.objects.filter(created_by=user).count()
    
    context = {
        'recent_parts': recent_parts,
        'recent_orders': recent_orders,
        'recent_alerts': recent_alerts,
        'stats': stats,
        'user': user,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def qr_scanner_view(request):
    """
    QR code scanner view.
    """
    return render(request, 'core/qr_scanner.html')


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def scan_qr_code(request):
    """
    Handle QR code scan requests.
    """
    try:
        data = json.loads(request.body)
        qr_data = data.get('qr_data')
        
        if not qr_data:
            return JsonResponse({'error': 'QR data is required'}, status=400)
        
        # Log the scan
        scan_record = QRCodeScan.objects.create(
            qr_code_data=qr_data,
            scanned_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            scan_result={'status': 'processing'}
        )
        
        # Try to find the part
        try:
            part = Part.objects.get(qr_code_data=qr_data)
            scan_record.scan_result = {
                'status': 'success',
                'part_id': part.id,
                'part_number': part.part_number,
                'part_name': part.name
            }
            scan_record.save()
            
            return JsonResponse({
                'success': True,
                'part': {
                    'id': part.id,
                    'part_number': part.part_number,
                    'name': part.name,
                    'manufacturer': part.manufacturer,
                    'status': part.status,
                    'current_location': part.current_location,
                    'installation_date': part.installation_date,
                    'last_inspection_date': part.last_inspection_date,
                    'next_inspection_date': part.next_inspection_date,
                    'url': part.get_absolute_url(),
                }
            })
        
        except Part.DoesNotExist:
            scan_record.scan_result = {
                'status': 'not_found',
                'message': 'Part not found'
            }
            scan_record.save()
            
            return JsonResponse({
                'success': False,
                'error': 'Part not found',
                'message': 'No part found with this QR code'
            }, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def notifications_view(request):
    """
    User notifications view.
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all as read if requested
    if request.GET.get('mark_read') == 'all':
        notifications.update(is_read=True, read_at=timezone.now())
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'core/notifications.html', context)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read.
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)


@login_required
def search_view(request):
    """
    Global search view.
    """
    query = request.GET.get('q', '')
    results = {
        'parts': [],
        'orders': [],
        'projects': [],
        'users': [],
    }
    
    if query:
        # Search parts
        parts = Part.objects.filter(
            Q(part_number__icontains=query) |
            Q(name__icontains=query) |
            Q(manufacturer__icontains=query)
        )[:10]
        results['parts'] = parts
        
        # Search orders
        orders = PurchaseOrder.objects.filter(
            Q(order_number__icontains=query) |
            Q(vendor__company_name__icontains=query)
        )[:10]
        results['orders'] = orders
        
        # Search projects
        projects = Project.objects.filter(
            Q(project_code__icontains=query) |
            Q(name__icontains=query)
        )[:10]
        results['projects'] = projects
        
        # Search users (admin/authority only)
        if request.user.is_admin() or request.user.is_railway_authority():
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(employee_id__icontains=query)
            )[:10]
            results['users'] = users
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'core/search.html', context)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_stats(request):
    """
    API endpoint for dashboard statistics.
    """
    user = request.user
    
    stats = {
        'total_parts': Part.objects.count(),
        'active_parts': Part.objects.filter(status='ACTIVE').count(),
        'total_orders': PurchaseOrder.objects.count(),
        'pending_orders': PurchaseOrder.objects.filter(
            status__in=['DRAFT', 'PENDING_APPROVAL']
        ).count(),
        'active_alerts': Alert.objects.filter(status='ACTIVE').count(),
        'unread_notifications': Notification.objects.filter(
            user=user, is_read=False
        ).count(),
    }
    
    # User-specific stats
    if user.is_vendor():
        stats['my_orders'] = PurchaseOrder.objects.filter(
            vendor__contact_person=user
        ).count()
    elif user.is_railway_employee() or user.is_railway_authority():
        stats['my_parts'] = Part.objects.filter(created_by=user).count()
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_recent_activities(request):
    """
    API endpoint for recent activities.
    """
    activities = []
    
    # Recent parts
    recent_parts = Part.objects.all()[:5]
    for part in recent_parts:
        activities.append({
            'type': 'part_created',
            'title': f'New part created: {part.name}',
            'description': f'Part number: {part.part_number}',
            'timestamp': part.created_at,
            'url': part.get_absolute_url(),
        })
    
    # Recent orders
    recent_orders = PurchaseOrder.objects.all()[:5]
    for order in recent_orders:
        activities.append({
            'type': 'order_created',
            'title': f'New order: {order.order_number}',
            'description': f'Vendor: {order.vendor.company_name}',
            'timestamp': order.created_at,
            'url': f'/orders/{order.id}/',
        })
    
    # Recent tracking events
    recent_events = TrackingEvent.objects.all()[:5]
    for event in recent_events:
        activities.append({
            'type': 'tracking_event',
            'title': f'{event.get_event_type_display()}: {event.part.name}',
            'description': f'Location: {event.location}',
            'timestamp': event.event_date,
            'url': event.part.get_absolute_url(),
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response(activities[:10])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_notifications(request):
    """
    API endpoint for user notifications.
    """
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]
    
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'action_url': notification.action_url,
            'created_at': notification.created_at,
        })
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_mark_notification_read(request, notification_id):
    """
    API endpoint to mark notification as read.
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )