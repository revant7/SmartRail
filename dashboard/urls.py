"""
URL configuration for dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('railway-authority/', views.railway_authority_dashboard, name='railway_authority_dashboard'),
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('railway-worker/', views.railway_worker_dashboard, name='railway_worker_dashboard'),
    path('software-staff/', views.software_staff_dashboard, name='software_staff_dashboard'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
