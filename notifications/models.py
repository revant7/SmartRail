"""
Notification system models for alerts and tracking.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class Notification(models.Model):
    """
    System notifications for users.
    """
    NOTIFICATION_TYPES = [
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('SUCCESS', 'Success'),
        ('ALERT', 'Alert'),
        ('DEADLINE_REMINDER', 'Deadline Reminder'),
        ('STATUS_CHANGE', 'Status Change'),
        ('NEW_REQUIREMENT', 'New Requirement'),
        ('VENDOR_REQUEST', 'Vendor Request'),
        ('INSPECTION_DUE', 'Inspection Due'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    # Basic Information
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='INFO'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    
    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Target User
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Related Object (Generic Foreign Key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Action
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Schedule notification for later delivery"
    )
    
    # Additional Data
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional notification data"
    )
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type', 'created_at']),
            models.Index(fields=['priority', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """
        Mark notification as read.
        """
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def is_scheduled(self):
        """
        Check if notification is scheduled for future delivery.
        """
        return self.scheduled_for and self.scheduled_for > timezone.now()


class NotificationTemplate(models.Model):
    """
    Templates for different types of notifications.
    """
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(
        max_length=20,
        choices=Notification.NOTIFICATION_TYPES
    )
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    action_url_template = models.CharField(max_length=500, blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    # Template Variables
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of template variables that can be used"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
    
    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    """
    User notification preferences.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Email Preferences
    email_enabled = models.BooleanField(default=True)
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('IMMEDIATE', 'Immediate'),
            ('DAILY', 'Daily Digest'),
            ('WEEKLY', 'Weekly Digest'),
            ('NEVER', 'Never'),
        ],
        default='IMMEDIATE'
    )
    
    # SMS Preferences
    sms_enabled = models.BooleanField(default=False)
    sms_phone = models.CharField(max_length=15, blank=True)
    
    # Push Notification Preferences
    push_enabled = models.BooleanField(default=True)
    
    # Notification Type Preferences
    notification_types = models.JSONField(
        default=dict,
        blank=True,
        help_text="Preferences for each notification type"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"{self.user.username} - Notification Preferences"


class NotificationLog(models.Model):
    """
    Log of notification delivery attempts.
    """
    DELIVERY_METHODS = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
    ]
    
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='delivery_logs'
    )
    delivery_method = models.CharField(
        max_length=10,
        choices=DELIVERY_METHODS
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Delivery Details
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # External Service Details
    external_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="ID from external service (email provider, SMS service, etc.)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_logs'
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification.title} - {self.get_delivery_method_display()} ({self.status})"
