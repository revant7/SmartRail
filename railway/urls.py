"""
URL configuration for railway app.
"""
from django.urls import path
from . import views

app_name = 'railway'

urlpatterns = [
    # Requirements
    path('requirements/', views.requirement_list, name='requirement_list'),
    path('requirements/create/', views.create_requirement, name='create_requirement'),
    path('requirements/<int:requirement_id>/', views.requirement_detail, name='requirement_detail'),
    path('requirements/<int:requirement_id>/edit/', views.edit_requirement, name='edit_requirement'),
    path('requirements/<int:requirement_id>/status/', views.update_requirement_status, name='update_requirement_status'),
    
    # Vendor Requests
    path('vendor-requests/', views.vendor_request_list, name='vendor_request_list'),
    path('requirements/<int:requirement_id>/request/', views.create_vendor_request, name='create_vendor_request'),
    path('vendor-requests/<int:request_id>/approve/', views.approve_vendor_request, name='approve_vendor_request'),
    path('vendor-requests/<int:request_id>/reject/', views.reject_vendor_request, name='reject_vendor_request'),
    
    # Inspections
    path('requirements/<int:requirement_id>/inspection/', views.create_inspection, name='create_inspection'),
    
    # QR Code Tracking
    path('qr-tracking/', views.qr_tracking, name='qr_tracking'),
    path('qr-track/<uuid:uuid>/', views.qr_track, name='qr_track'),
    
    # API Endpoints
    path('api/requirements/<int:requirement_id>/', views.api_requirement_detail, name='api_requirement_detail'),
    path('api/scan/<uuid:requirement_uuid>/', views.api_scan_qr_code, name='api_scan_qr_code'),
    path('api/divisions/', views.api_divisions, name='api_divisions'),
    path('api/locations/', views.api_locations, name='api_locations'),
]
