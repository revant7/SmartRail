"""
URL configuration for orders app.
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Projects
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_update_view, name='project_update'),
    
    # Vendors
    path('vendors/', views.vendor_list_view, name='vendor_list'),
    path('vendors/create/', views.vendor_create_view, name='vendor_create'),
    path('vendors/<int:vendor_id>/', views.vendor_detail_view, name='vendor_detail'),
    path('vendors/<int:vendor_id>/edit/', views.vendor_update_view, name='vendor_update'),
    
    # Orders
    path('', views.order_list_view, name='order_list'),
    path('create/', views.order_create_view, name='order_create'),
    path('<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('<int:order_id>/edit/', views.order_update_view, name='order_update'),
    path('<int:order_id>/approve/', views.order_approve_view, name='order_approve'),
    path('<int:order_id>/vendor-confirm/', views.order_vendor_confirm_view, name='order_vendor_confirm'),
    
    # API Endpoints
    path('api/', views.api_order_list, name='api_order_list'),
    path('api/<int:order_id>/', views.api_order_detail, name='api_order_detail'),
    path('api/vendors/', views.api_vendor_list, name='api_vendor_list'),
]
