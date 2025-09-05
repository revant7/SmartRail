"""
Celery configuration for QRailway project.
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrail.settings')

app = Celery('qrail')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'send-deadline-reminders': {
        'task': 'notifications.tasks.send_deadline_reminders',
        'schedule': 86400.0,  # Run daily
    },
    'send-overdue-notifications': {
        'task': 'notifications.tasks.send_overdue_notifications',
        'schedule': 86400.0,  # Run daily
    },
    'send-daily-digest': {
        'task': 'notifications.tasks.send_daily_digest',
        'schedule': 86400.0,  # Run daily at midnight
    },
    'send-weekly-digest': {
        'task': 'notifications.tasks.send_weekly_digest',
        'schedule': 604800.0,  # Run weekly
    },
    'cleanup-old-notifications': {
        'task': 'notifications.tasks.cleanup_old_notifications',
        'schedule': 2592000.0,  # Run monthly
    },
    'send-inspection-reminders': {
        'task': 'notifications.tasks.send_inspection_reminders',
        'schedule': 86400.0,  # Run daily
    },
    'send-vendor-performance-alerts': {
        'task': 'notifications.tasks.send_vendor_performance_alerts',
        'schedule': 604800.0,  # Run weekly
    },
    'send-system-health-notifications': {
        'task': 'notifications.tasks.send_system_health_notifications',
        'schedule': 3600.0,  # Run hourly
    },
    'process-notification-queue': {
        'task': 'notifications.tasks.process_notification_queue',
        'schedule': 300.0,  # Run every 5 minutes
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
