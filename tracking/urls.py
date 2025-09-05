"""
URL configuration for tracking app.
"""
from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    # Tracking Events
    path('events/', views.tracking_event_list_view, name='tracking_event_list'),
    path('events/<int:event_id>/', views.tracking_event_detail_view, name='tracking_event_detail'),
    path('events/create/', views.tracking_event_create_view, name='tracking_event_create'),
    
    # Inspections
    path('inspections/', views.inspection_list_view, name='inspection_list'),
    path('inspections/<int:inspection_id>/', views.inspection_detail_view, name='inspection_detail'),
    path('inspections/create/', views.inspection_create_view, name='inspection_create'),
    
    # Quality Checks
    path('quality-checks/', views.quality_check_list_view, name='quality_check_list'),
    path('quality-checks/<int:check_id>/', views.quality_check_detail_view, name='quality_check_detail'),
    path('quality-checks/create/', views.quality_check_create_view, name='quality_check_create'),
    
    # Alerts
    path('alerts/', views.alert_list_view, name='alert_list'),
    path('alerts/<int:alert_id>/', views.alert_detail_view, name='alert_detail'),
    path('alerts/<int:alert_id>/acknowledge/', views.alert_acknowledge_view, name='alert_acknowledge'),
    path('alerts/<int:alert_id>/resolve/', views.alert_resolve_view, name='alert_resolve'),
    
    # API Endpoints
    path('api/events/', views.api_tracking_event_list, name='api_tracking_event_list'),
    path('api/events/<int:event_id>/', views.api_tracking_event_detail, name='api_tracking_event_detail'),
    path('api/inspections/', views.api_inspection_list, name='api_inspection_list'),
    path('api/quality-checks/', views.api_quality_check_list, name='api_quality_check_list'),
    path('api/alerts/', views.api_alert_list, name='api_alert_list'),
]
