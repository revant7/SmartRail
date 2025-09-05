"""
URL configuration for parts app.
"""
from django.urls import path
from . import views

app_name = 'parts'

urlpatterns = [
    # Parts CRUD
    path('', views.part_list_view, name='part_list'),
    path('create/', views.part_create_view, name='part_create'),
    path('<int:part_id>/', views.part_detail_view, name='part_detail'),
    path('<int:part_id>/edit/', views.part_update_view, name='part_update'),
    path('<int:part_id>/delete/', views.part_delete_view, name='part_delete'),
    path('<int:part_id>/qr/', views.part_qr_view, name='part_qr'),
    
    # Categories
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_update_view, name='category_update'),
    
    # API Endpoints
    path('api/', views.api_part_list, name='api_part_list'),
    path('api/<int:part_id>/', views.api_part_detail, name='api_part_detail'),
    path('api/qr/<str:qr_data>/', views.api_part_by_qr, name='api_part_by_qr'),
    path('api/categories/', views.api_part_categories, name='api_part_categories'),
]
