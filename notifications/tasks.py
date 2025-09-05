"""
Celery tasks for notification system.
"""
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

from .models import Notification, NotificationPreference
from .services import NotificationService, RequirementNotificationService
from railway.models import Requirement

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def send_scheduled_notifications():
    """
    Send notifications that are scheduled for delivery.
    """
    now = timezone.now()
    scheduled_notifications = Notification.objects.filter(
        scheduled_for__lte=now,
        is_read=False
    )
    
    for notification in scheduled_notifications:
        NotificationService.send_notification(notification)
    
    logger.info(f"Sent {scheduled_notifications.count()} scheduled notifications")


@shared_task
def send_deadline_reminders():
    """
    Send deadline reminder notifications.
    """
    now = timezone.now()
    
    # Find requirements with deadlines in 7, 3, and 1 days
    reminder_days = [7, 3, 1]
    
    for days in reminder_days:
        reminder_date = now + timezone.timedelta(days=days)
        start_date = reminder_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = reminder_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        requirements = Requirement.objects.filter(
            deadline_date__range=[start_date, end_date],
            status__in=['INACTIVE', 'ACTIVE', 'SHIPPED']
        )
        
        for requirement in requirements:
            RequirementNotificationService.notify_deadline_reminder(
                requirement, days
            )
    
    logger.info("Deadline reminder notifications sent")


@shared_task
def send_overdue_notifications():
    """
    Send notifications for overdue requirements.
    """
    now = timezone.now()
    overdue_requirements = Requirement.objects.filter(
        deadline_date__lt=now,
        status__in=['INACTIVE', 'ACTIVE', 'SHIPPED']
    )
    
    for requirement in overdue_requirements:
        # Send daily overdue notifications
        RequirementNotificationService.notify_deadline_reminder(
            requirement, 0  # 0 days remaining = overdue
        )
    
    logger.info(f"Overdue notifications sent for {overdue_requirements.count()} requirements")


@shared_task
def send_daily_digest():
    """
    Send daily digest emails to users who prefer daily notifications.
    """
    users_with_daily_digest = User.objects.filter(
        notification_preferences__email_frequency='DAILY',
        notification_preferences__email_enabled=True,
        is_active=True
    )
    
    for user in users_with_daily_digest:
        # Get unread notifications from yesterday
        yesterday = timezone.now() - timezone.timedelta(days=1)
        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False,
            created_at__gte=yesterday
        )
        
        if unread_notifications.exists():
            # Create digest notification
            NotificationService.create_from_template(
                user=user,
                template_name='daily_digest',
                context_data={
                    'user': user,
                    'notifications': unread_notifications,
                    'count': unread_notifications.count(),
                }
            )
    
    logger.info(f"Daily digest sent to {users_with_daily_digest.count()} users")


@shared_task
def send_weekly_digest():
    """
    Send weekly digest emails to users who prefer weekly notifications.
    """
    users_with_weekly_digest = User.objects.filter(
        notification_preferences__email_frequency='WEEKLY',
        notification_preferences__email_enabled=True,
        is_active=True
    )
    
    for user in users_with_weekly_digest:
        # Get unread notifications from last week
        week_ago = timezone.now() - timezone.timedelta(days=7)
        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False,
            created_at__gte=week_ago
        )
        
        if unread_notifications.exists():
            # Create digest notification
            NotificationService.create_from_template(
                user=user,
                template_name='weekly_digest',
                context_data={
                    'user': user,
                    'notifications': unread_notifications,
                    'count': unread_notifications.count(),
                }
            )
    
    logger.info(f"Weekly digest sent to {users_with_weekly_digest.count()} users")


@shared_task
def cleanup_old_notifications():
    """
    Clean up old read notifications.
    """
    deleted_count = NotificationService.cleanup_old_notifications(days=30)
    logger.info(f"Cleaned up {deleted_count} old notifications")


@shared_task
def send_inspection_reminders():
    """
    Send reminders for upcoming inspections.
    """
    # This would be implemented based on inspection scheduling logic
    # For now, just log that the task ran
    logger.info("Inspection reminder task executed")


@shared_task
def send_vendor_performance_alerts():
    """
    Send alerts about vendor performance issues.
    """
    # This would analyze vendor performance metrics and send alerts
    # For now, just log that the task ran
    logger.info("Vendor performance alert task executed")


@shared_task
def send_system_health_notifications():
    """
    Send system health notifications to software staff.
    """
    software_staff = User.objects.filter(
        user_type='SOFTWARE_STAFF',
        is_active=True
    )
    
    # Check for system issues and send notifications
    # This would integrate with system monitoring
    
    logger.info(f"System health notifications sent to {software_staff.count()} software staff")


@shared_task
def process_notification_queue():
    """
    Process pending notifications in the queue.
    """
    # This task would process any queued notifications
    # that couldn't be sent immediately
    
    pending_notifications = Notification.objects.filter(
        scheduled_for__isnull=True,
        is_read=False
    )[:100]  # Process in batches
    
    for notification in pending_notifications:
        try:
            NotificationService.send_notification(notification)
        except Exception as e:
            logger.error(f"Failed to process notification {notification.id}: {str(e)}")
    
    logger.info(f"Processed {pending_notifications.count()} notifications from queue")
