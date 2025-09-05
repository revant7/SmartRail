"""
URL configuration for orders app.
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Projects
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail'),
    
    # Vendors
    path('vendors/', views.vendor_list_view, name='vendor_list'),
    path('vendors/<int:vendor_id>/', views.vendor_detail_view, name='vendor_detail'),
    
    # Orders
    path('', views.order_list_view, name='order_list'),
    path('create/', views.order_create_view, name='order_create'),
    path('<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('<int:order_id>/edit/', views.order_update_view, name='order_update'),
    path('<int:order_id>/approve/', views.order_approve_view, name='order_approve'),
    
    # API Endpoints
    path('api/', views.api_order_list, name='api_order_list'),
    path('api/<int:order_id>/', views.api_order_detail, name='api_order_detail'),
    path('api/vendors/', views.api_vendor_list, name='api_vendor_list'),
]
