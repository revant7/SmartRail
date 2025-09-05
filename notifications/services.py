"""
Notification service for sending notifications.
"""
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.template import Template, Context
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import Notification, NotificationTemplate, NotificationPreference

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for creating and sending notifications.
    """
    
    @staticmethod
    def create_notification(
        user,
        notification_type,
        title,
        message,
        priority='MEDIUM',
        content_object=None,
        action_url='',
        action_text='',
        metadata=None,
        scheduled_for=None
    ):
        """
        Create a new notification.
        """
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            content_object=content_object,
            action_url=action_url,
            action_text=action_text,
            metadata=metadata or {},
            scheduled_for=scheduled_for
        )
        
        # Send immediate notification if not scheduled
        if not scheduled_for or scheduled_for <= timezone.now():
            NotificationService.send_notification(notification)
        
        return notification
    
    @staticmethod
    def create_from_template(
        user,
        template_name,
        context_data=None,
        content_object=None,
        scheduled_for=None
    ):
        """
        Create notification from template.
        """
        try:
            template = NotificationTemplate.objects.get(
                name=template_name,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Notification template '{template_name}' not found")
            return None
        
        # Render template with context
        title_template = Template(template.title_template)
        message_template = Template(template.message_template)
        
        context = Context(context_data or {})
        
        title = title_template.render(context)
        message = message_template.render(context)
        
        action_url = ''
        if template.action_url_template:
            action_url_template = Template(template.action_url_template)
            action_url = action_url_template.render(context)
        
        return NotificationService.create_notification(
            user=user,
            notification_type=template.notification_type,
            title=title,
            message=message,
            content_object=content_object,
            action_url=action_url,
            action_text=template.action_text,
            scheduled_for=scheduled_for
        )
    
    @staticmethod
    def send_notification(notification):
        """
        Send notification through all enabled channels.
        """
        try:
            preferences = notification.user.notification_preferences
            
            # Send in-app notification
            if preferences.push_enabled:
                NotificationService._send_in_app(notification)
            
            # Send email if enabled
            if preferences.email_enabled and preferences.email_frequency == 'IMMEDIATE':
                NotificationService._send_email(notification)
            
            # Send SMS if enabled
            if preferences.sms_enabled and preferences.sms_phone:
                NotificationService._send_sms(notification)
                
        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {str(e)}")
    
    @staticmethod
    def _send_in_app(notification):
        """
        Send in-app notification (already created in database).
        """
        # In-app notifications are automatically available
        # when the notification is created in the database
        pass
    
    @staticmethod
    def _send_email(notification):
        """
        Send email notification.
        """
        try:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                fail_silently=False,
            )
            logger.info(f"Email sent for notification {notification.id}")
        except Exception as e:
            logger.error(f"Failed to send email for notification {notification.id}: {str(e)}")
    
    @staticmethod
    def _send_sms(notification):
        """
        Send SMS notification.
        """
        # Implement SMS sending logic here
        # This would integrate with SMS service providers like Twilio, AWS SNS, etc.
        logger.info(f"SMS notification {notification.id} would be sent to {notification.user.notification_preferences.sms_phone}")
    
    @staticmethod
    def send_bulk_notifications(notifications):
        """
        Send multiple notifications efficiently.
        """
        for notification in notifications:
            NotificationService.send_notification(notification)
    
    @staticmethod
    def mark_all_as_read(user):
        """
        Mark all notifications as read for a user.
        """
        Notification.objects.filter(
            user=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
    
    @staticmethod
    def get_unread_count(user):
        """
        Get count of unread notifications for a user.
        """
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).count()
    
    @staticmethod
    def cleanup_old_notifications(days=30):
        """
        Clean up old read notifications.
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        deleted_count = Notification.objects.filter(
            is_read=True,
            read_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old notifications")
        return deleted_count


class RequirementNotificationService:
    """
    Specialized service for requirement-related notifications.
    """
    
    @staticmethod
    def notify_new_requirement(requirement):
        """
        Notify all vendors about new requirement.
        """
        vendors = User.objects.filter(
            user_type='VENDOR',
            is_active=True
        )
        
        for vendor in vendors:
            NotificationService.create_from_template(
                user=vendor,
                template_name='new_requirement',
                context_data={
                    'requirement': requirement,
                    'vendor': vendor,
                    'zone': requirement.zone.name,
                    'division': requirement.division.name,
                },
                content_object=requirement
            )
    
    @staticmethod
    def notify_requirement_assigned(requirement, vendor):
        """
        Notify vendor when requirement is assigned to them.
        """
        NotificationService.create_from_template(
            user=vendor,
            template_name='requirement_assigned',
            context_data={
                'requirement': requirement,
                'vendor': vendor,
                'deadline': requirement.deadline_date,
            },
            content_object=requirement
        )
        
        # Also notify railway authority
        NotificationService.create_from_template(
            user=requirement.created_by,
            template_name='requirement_assigned_authority',
            context_data={
                'requirement': requirement,
                'vendor': vendor,
            },
            content_object=requirement
        )
    
    @staticmethod
    def notify_deadline_reminder(requirement, days_remaining):
        """
        Notify about deadline reminder.
        """
        # Notify vendor
        if requirement.assigned_vendor:
            NotificationService.create_from_template(
                user=requirement.assigned_vendor,
                template_name='deadline_reminder_vendor',
                context_data={
                    'requirement': requirement,
                    'days_remaining': days_remaining,
                },
                content_object=requirement
            )
        
        # Notify railway authority
        NotificationService.create_from_template(
            user=requirement.created_by,
            template_name='deadline_reminder_authority',
            context_data={
                'requirement': requirement,
                'days_remaining': days_remaining,
            },
            content_object=requirement
        )
    
    @staticmethod
    def notify_status_change(requirement, old_status, new_status, changed_by):
        """
        Notify about status change.
        """
        # Notify vendor if assigned
        if requirement.assigned_vendor:
            NotificationService.create_from_template(
                user=requirement.assigned_vendor,
                template_name='status_change_vendor',
                context_data={
                    'requirement': requirement,
                    'old_status': old_status,
                    'new_status': new_status,
                    'changed_by': changed_by,
                },
                content_object=requirement
            )
        
        # Notify railway authority
        NotificationService.create_from_template(
            user=requirement.created_by,
            template_name='status_change_authority',
            context_data={
                'requirement': requirement,
                'old_status': old_status,
                'new_status': new_status,
                'changed_by': changed_by,
            },
            content_object=requirement
        )
