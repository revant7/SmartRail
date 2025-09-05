"""
API URL configuration for core app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'core_api'

urlpatterns = [
    # Dashboard API
    path('dashboard/stats/', views.api_dashboard_stats, name='dashboard_stats'),
    path('dashboard/activities/', views.api_recent_activities, name='recent_activities'),
    
    # QR Code API
    path('qr/scan/', views.scan_qr_code, name='scan_qr'),
    
    # Notifications API
    path('notifications/', views.api_notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.api_mark_notification_read, name='mark_notification_read'),
]
