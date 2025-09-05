"""
URL patterns for inspections app.
"""
from django.urls import path
from . import views

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
    
    # AJAX endpoints
    path('api/<uuid:inspection_id>/upload-photo/', views.upload_photo_ajax, name='upload_photo_ajax'),
    path('api/photo/<int:photo_id>/delete/', views.delete_photo_ajax, name='delete_photo_ajax'),
    path('api/<uuid:inspection_id>/data/', views.get_inspection_data_ajax, name='get_inspection_data_ajax'),
]
