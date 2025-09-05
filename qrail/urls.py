"""
URL configuration for qrail project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from core.health import health_check, readiness_check, liveness_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('core/', include('core.urls')),
    path('api/', include('core.api_urls')),
    path('dashboard/', include('dashboard.urls')),
    path('railway/', include('railway.urls')),
    path('notifications/', include('notifications.urls')),
    path('parts/', include('parts.urls')),
    path('orders/', include('orders.urls')),
    path('tracking/', include('tracking.urls')),
    
    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/live/', liveness_check, name='liveness_check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
