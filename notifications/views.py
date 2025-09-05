"""
Views for notifications app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Notification, NotificationPreference
from .services import NotificationService


@login_required
def notification_list(request):
    """
    List user's notifications.
    """
    notifications = Notification.objects.filter(user=request.user)
    
    # Filter by read status
    read_filter = request.GET.get('read')
    if read_filter == 'unread':
        notifications = notifications.filter(is_read=False)
    elif read_filter == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        notifications = notifications.filter(notification_type=type_filter)
    
    paginator = Paginator(notifications.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'notification_types': Notification.NOTIFICATION_TYPES,
        'read_filter': read_filter,
        'type_filter': type_filter,
        'unread_count': NotificationService.get_unread_count(request.user),
    }
    
    return render(request, 'notifications/notification_list.html', context)


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
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': True})
        else:
            messages.success(request, 'Notification marked as read.')
    except Notification.DoesNotExist:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({'error': 'Notification not found'}, status=404)
        else:
            messages.error(request, 'Notification not found.')
    
    return redirect(request.META.get('HTTP_REFERER', 'notifications:notification_list'))


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """
    Mark all notifications as read for the current user.
    """
    NotificationService.mark_all_as_read(request.user)
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'success': True})
    else:
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:notification_list')


@login_required
def notification_preferences(request):
    """
    Manage notification preferences.
    """
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        # Update preferences
        preferences.email_enabled = request.POST.get('email_enabled') == 'on'
        preferences.email_frequency = request.POST.get('email_frequency', 'IMMEDIATE')
        preferences.sms_enabled = request.POST.get('sms_enabled') == 'on'
        preferences.sms_phone = request.POST.get('sms_phone', '')
        preferences.push_enabled = request.POST.get('push_enabled') == 'on'
        
        # Update notification type preferences
        notification_types = {}
        for notification_type, _ in Notification.NOTIFICATION_TYPES:
            notification_types[notification_type] = {
                'email': request.POST.get(f'{notification_type}_email') == 'on',
                'sms': request.POST.get(f'{notification_type}_sms') == 'on',
                'push': request.POST.get(f'{notification_type}_push') == 'on',
            }
        preferences.notification_types = notification_types
        
        preferences.save()
        messages.success(request, 'Notification preferences updated successfully!')
        return redirect('notifications:notification_preferences')
    
    context = {
        'preferences': preferences,
        'notification_types': Notification.NOTIFICATION_TYPES,
        'email_frequencies': [
            ('IMMEDIATE', 'Immediate'),
            ('DAILY', 'Daily Digest'),
            ('WEEKLY', 'Weekly Digest'),
            ('NEVER', 'Never'),
        ],
    }
    
    return render(request, 'notifications/preferences.html', context)
