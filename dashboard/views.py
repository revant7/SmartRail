"""
Dashboard views for different user types.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from railway.models import Requirement, VendorRequest, RailwayZone, RailwayDivision
from notifications.models import Notification
from notifications.services import NotificationService

User = get_user_model()


@login_required
def dashboard(request):
    """
    Main dashboard view that redirects based on user type.
    """
    user = request.user
    
    if user.is_railway_authority():
        return redirect('dashboard:railway_authority_dashboard')
    elif user.is_vendor():
        return redirect('dashboard:vendor_dashboard')
    elif user.is_railway_worker():
        return redirect('dashboard:railway_worker_dashboard')
    elif user.is_software_staff():
        return redirect('dashboard:software_staff_dashboard')
    else:
        return redirect('accounts:login')


@login_required
def railway_authority_dashboard(request):
    """
    Dashboard for Railway Authority users.
    """
    user = request.user
    
    # Get requirements created by this authority
    requirements = Requirement.objects.filter(created_by=user)
    
    # Dashboard statistics
    stats = {
        'total_requirements': requirements.count(),
        'active_requirements': requirements.filter(status='ACTIVE').count(),
        'completed_requirements': requirements.filter(status='COMPLETED').count(),
        'overdue_requirements': requirements.filter(
            deadline_date__lt=timezone.now(),
            status__in=['INACTIVE', 'ACTIVE', 'SHIPPED']
        ).count(),
        'pending_vendor_requests': VendorRequest.objects.filter(
            requirement__created_by=user,
            status='PENDING'
        ).count(),
    }
    
    # Recent requirements
    recent_requirements = requirements.order_by('-created_at')[:10]
    
    # Overdue requirements
    overdue_requirements = requirements.filter(
        deadline_date__lt=timezone.now(),
        status__in=['INACTIVE', 'ACTIVE', 'SHIPPED']
    ).order_by('deadline_date')[:5]
    
    # Recent vendor requests
    recent_vendor_requests = VendorRequest.objects.filter(
        requirement__created_by=user
    ).order_by('-created_at')[:10]
    
    # Notifications
    notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'stats': stats,
        'recent_requirements': recent_requirements,
        'overdue_requirements': overdue_requirements,
        'recent_vendor_requests': recent_vendor_requests,
        'notifications': notifications,
    }
    
    return render(request, 'dashboard/railway_authority_dashboard.html', context)


@login_required
def vendor_dashboard(request):
    """
    Dashboard for Vendor users.
    """
    user = request.user
    
    # Get vendor's requests and assigned requirements
    vendor_requests = VendorRequest.objects.filter(vendor=user)
    assigned_requirements = Requirement.objects.filter(assigned_vendor=user)
    
    # Dashboard statistics
    stats = {
        'total_requests': vendor_requests.count(),
        'approved_requests': vendor_requests.filter(status='APPROVED').count(),
        'pending_requests': vendor_requests.filter(status='PENDING').count(),
        'assigned_requirements': assigned_requirements.count(),
        'active_requirements': assigned_requirements.filter(status='ACTIVE').count(),
        'completed_requirements': assigned_requirements.filter(status='COMPLETED').count(),
    }
    
    # Recent vendor requests
    recent_requests = vendor_requests.order_by('-created_at')[:10]
    
    # Assigned requirements
    active_requirements = assigned_requirements.filter(
        status__in=['ACTIVE', 'SHIPPED', 'RECEIVED']
    ).order_by('deadline_date')[:5]
    
    # Available requirements (not yet requested by this vendor)
    available_requirements = Requirement.objects.filter(
        status='INACTIVE',
        assigned_vendor__isnull=True
    ).exclude(
        vendor_requests__vendor=user
    ).order_by('-created_at')[:10]
    
    # Notifications
    notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'stats': stats,
        'recent_requests': recent_requests,
        'active_requirements': active_requirements,
        'available_requirements': available_requirements,
        'notifications': notifications,
    }
    
    return render(request, 'dashboard/vendor_dashboard.html', context)


@login_required
def railway_worker_dashboard(request):
    """
    Dashboard for Railway Worker users.
    """
    user = request.user
    
    # Get requirements in worker's zone/division
    # This would be filtered based on worker's location
    requirements = Requirement.objects.all()  # Filter by worker's zone/division
    
    # Dashboard statistics
    stats = {
        'total_requirements': requirements.count(),
        'requirements_to_inspect': requirements.filter(status='RECEIVED').count(),
        'requirements_to_install': requirements.filter(status='RECEIVED').count(),
        'completed_installations': requirements.filter(status='INSTALLED').count(),
    }
    
    # Requirements requiring inspection
    inspection_required = requirements.filter(status='RECEIVED').order_by('deadline_date')[:10]
    
    # Requirements requiring installation
    installation_required = requirements.filter(status='RECEIVED').order_by('deadline_date')[:10]
    
    # Recent inspections
    recent_inspections = getattr(user, 'conducted_requirement_inspections', None)
    if recent_inspections is not None:
        recent_inspections = recent_inspections.order_by('-inspection_date')[:10]
    else:
        recent_inspections = []
    
    # Notifications
    notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'stats': stats,
        'inspection_required': inspection_required,
        'installation_required': installation_required,
        'recent_inspections': recent_inspections,
        'notifications': notifications,
    }
    
    return render(request, 'dashboard/railway_worker_dashboard.html', context)


@login_required
def software_staff_dashboard(request):
    """
    Dashboard for Software Staff/Moderator users.
    """
    user = request.user
    
    # System-wide statistics
    stats = {
        'total_users': User.objects.count(),
        'total_requirements': Requirement.objects.count(),
        'total_vendor_requests': VendorRequest.objects.count(),
        'active_requirements': Requirement.objects.filter(status='ACTIVE').count(),
        'overdue_requirements': Requirement.objects.filter(
            deadline_date__lt=timezone.now(),
            status__in=['INACTIVE', 'ACTIVE', 'SHIPPED']
        ).count(),
        'pending_vendor_requests': VendorRequest.objects.filter(status='PENDING').count(),
    }
    
    # Recent system activity
    recent_requirements = Requirement.objects.order_by('-created_at')[:10]
    recent_vendor_requests = VendorRequest.objects.order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # System alerts
    system_alerts = Notification.objects.filter(
        notification_type__in=['ERROR', 'WARNING', 'ALERT'],
        is_read=False
    ).order_by('-created_at')[:10]
    
    # Zone-wise statistics
    zone_stats = RailwayZone.objects.annotate(
        requirement_count=Count('requirements'),
        division_count=Count('divisions')
    ).order_by('name')
    
    context = {
        'user': user,
        'stats': stats,
        'recent_requirements': recent_requirements,
        'recent_vendor_requests': recent_vendor_requests,
        'recent_users': recent_users,
        'system_alerts': system_alerts,
        'zone_stats': zone_stats,
    }
    
    return render(request, 'dashboard/software_staff_dashboard.html', context)


@login_required
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
    except Notification.DoesNotExist:
        pass
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:dashboard'))


@login_required
def mark_all_notifications_read(request):
    """
    Mark all notifications as read for the current user.
    """
    NotificationService.mark_all_as_read(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:dashboard'))