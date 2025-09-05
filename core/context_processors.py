"""
Context processors for the core app.
"""
from notifications.models import Notification


def notifications(request):
    """
    Add notification-related context to all templates.
    """
    context = {}
    
    if request.user.is_authenticated:
        # Get unread notification count
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        # Get recent unread notifications (for dropdown)
        recent_unread = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:5]
        
        context.update({
            'unread_notification_count': unread_count,
            'recent_unread_notifications': recent_unread,
        })
    
    return context
