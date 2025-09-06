"""
URL patterns for inspections app.
"""
from django.urls import path, include
from . import views, streamlined_views, ai_views, api_views, mock_esp32

app_name = 'inspections'

urlpatterns = [
    # Dashboard and listing
    path('', views.inspection_dashboard, name='dashboard'),
    path('list/', views.inspection_list, name='inspection_list'),
    
    # Inspection CRUD
    path('create/', views.create_inspection, name='create_inspection'),
    path('<uuid:inspection_id>/', views.inspection_detail, name='inspection_detail'),
    path('<uuid:inspection_id>/edit/', views.update_inspection, name='update_inspection'),
    path('<uuid:inspection_id>/complete/', views.complete_inspection, name='complete_inspection'),
    
    # Photo and document uploads
    path('<uuid:inspection_id>/photos/', views.upload_photos, name='upload_photos'),
    path('<uuid:inspection_id>/documents/', views.upload_documents, name='upload_documents'),
    
    # Checklist responses
    path('<uuid:inspection_id>/checklist/<int:checklist_item_id>/', 
         views.respond_checklist, name='respond_checklist'),
    
    # Management
    path('stages/', views.inspection_stages, name='inspection_stages'),
    path('<uuid:inspection_id>/ai-summary/', views.ai_summary, name='ai_summary'),
    
    # Streamlined Inspection System
    path('streamlined/', streamlined_views.streamlined_inspection_home, name='streamlined_home'),
    path('streamlined/start/', streamlined_views.start_streamlined_inspection, name='start_streamlined_inspection'),
    path('streamlined/<uuid:inspection_id>/capture/', streamlined_views.streamlined_capture, name='streamlined_capture'),
    path('streamlined/qr-scanner/', streamlined_views.qr_code_scanner, name='qr_scanner'),
    path('streamlined/qr-generator/', streamlined_views.qr_code_generator, name='qr_generator'),
    path('streamlined/qr-code/<uuid:batch_uuid>/', streamlined_views.generate_qr_code, name='generate_qr_code'),
    path('streamlined/ai-reports/', streamlined_views.ai_report_dashboard, name='ai_report_dashboard'),
    path('streamlined/ai-reports/<int:report_id>/', streamlined_views.view_ai_report, name='view_ai_report'),
    
    # AI Integration Endpoints
    path('ai/send-data/<uuid:batch_uuid>/', ai_views.send_inspection_data_to_ai, name='send_inspection_data_to_ai'),
    path('ai/report/<int:report_id>/', ai_views.get_ai_report, name='get_ai_report'),
    path('ai/batch-summary/<uuid:batch_uuid>/', ai_views.get_batch_inspection_summary, name='get_batch_inspection_summary'),
    path('ai/receive-report/', ai_views.receive_ai_report, name='receive_ai_report'),
    
    # AJAX endpoints
    path('api/<uuid:inspection_id>/upload-photo/', views.upload_photo_ajax, name='upload_photo_ajax'),
    path('api/photo/<int:photo_id>/delete/', views.delete_photo_ajax, name='delete_photo_ajax'),
    path('api/<uuid:inspection_id>/data/', views.get_inspection_data_ajax, name='get_inspection_data_ajax'),
    
    # Streamlined AJAX endpoints
    path('api/streamlined/<uuid:inspection_id>/upload-photo/', streamlined_views.upload_streamlined_photo, name='upload_streamlined_photo'),
    path('api/streamlined/<uuid:inspection_id>/submit/', streamlined_views.submit_streamlined_inspection, name='submit_streamlined_inspection'),
    path('api/streamlined/process-qr/', streamlined_views.process_qr_code, name='process_qr_code'),
    
    # QR Code API endpoints
    path('api/scan-qr/', api_views.scan_qr_code_api, name='scan_qr_code_api'),
    path('api/trigger-esp32/', api_views.trigger_esp32_camera, name='trigger_esp32_camera'),
    path('api/esp32-qr-scan/', api_views.scan_qr_from_esp32, name='scan_qr_from_esp32'),
    path('api/esp32-qr-status/', api_views.get_esp32_qr_status, name='get_esp32_qr_status'),
    path('api/direct-esp32-scan/', api_views.direct_esp32_scan, name='direct_esp32_scan'),
    
    # QR Scanner and ESP32 pages
    path('esp32-tools/', api_views.esp32_landing_page, name='esp32_landing_page'),
    path('qr-scanner/', api_views.qr_code_scanner_page, name='qr_code_scanner_page'),
    path('streamlined/qr-scanner/', api_views.qr_code_scanner_page, name='qr_code_scanner_streamlined'),
    
    # Mock ESP32 Camera endpoints (for testing only)
    path('mock-esp32/', include([
        path('', mock_esp32.mock_esp32_ui, name='mock_esp32_ui'),
        path('trigger/', mock_esp32.mock_esp32_trigger_endpoint, name='mock_esp32_trigger_endpoint'),
        path('check-trigger/', mock_esp32.mock_esp32_check_trigger, name='mock_esp32_check_trigger'),
        path('get-sample-qr/', mock_esp32.mock_esp32_get_sample_qr, name='mock_esp32_get_sample_qr'),
    ])),
    
    # ESP32 camera integration endpoints
    path('esp32/', include([
        path('receive/', mock_esp32.esp32_receive_endpoint, name='esp32_receive_endpoint'),
        path('capture/', mock_esp32.esp32_capture_endpoint, name='esp32_capture_endpoint'),
        path('controller/', mock_esp32.esp32_controller_page, name='esp32_controller_page'),
    ])),
]
