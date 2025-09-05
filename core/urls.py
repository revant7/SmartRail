"""
URL configuration for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # QR Scanner
    path('qr-scanner/', views.qr_scanner_view, name='qr_scanner'),
    path('api/scan-qr/', views.scan_qr_code, name='scan_qr_code'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Search
    path('search/', views.search_view, name='search'),
    
    # API Endpoints
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/recent-activities/', views.api_recent_activities, name='api_recent_activities'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/<int:notification_id>/mark-read/', views.api_mark_notification_read, name='api_mark_notification_read'),
]
