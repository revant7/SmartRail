"""
Health check views for monitoring.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import time


def health_check(request):
    """
    Comprehensive health check endpoint.
    """
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = {
            'status': 'healthy',
            'response_time': 0
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Cache check
    try:
        start_time = time.time()
        cache.set('health_check', 'test', 10)
        cache.get('health_check')
        response_time = time.time() - start_time
        
        health_status['checks']['cache'] = {
            'status': 'healthy',
            'response_time': round(response_time * 1000, 2)  # Convert to milliseconds
        }
    except Exception as e:
        health_status['checks']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Redis check (if using Redis)
    try:
        if hasattr(settings, 'REDIS_URL'):
            r = redis.from_url(settings.REDIS_URL)
            start_time = time.time()
            r.ping()
            response_time = time.time() - start_time
            
            health_status['checks']['redis'] = {
                'status': 'healthy',
                'response_time': round(response_time * 1000, 2)
            }
    except Exception as e:
        health_status['checks']['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Return appropriate HTTP status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Readiness check for Kubernetes/Docker.
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check cache
        cache.set('readiness_check', 'test', 10)
        cache.get('readiness_check')
        
        return JsonResponse({'status': 'ready'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'not ready', 'error': str(e)}, status=503)


def liveness_check(request):
    """
    Liveness check for Kubernetes/Docker.
    """
    return JsonResponse({'status': 'alive'}, status=200)
