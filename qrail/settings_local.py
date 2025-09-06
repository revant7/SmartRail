"""
Local development settings for QRAIL project.
"""
from .settings import *

# Override settings for local development
DEBUG = True

# SQLite configuration is now controlled by USE_SQLITE in .env
# Database settings are handled in the main settings.py file


# Disable Redis for local development (use dummy cache)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Disable Celery for local development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Simplified logging for local development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Allow all hosts for local development
ALLOWED_HOSTS = ['*']

# Disable security settings for local development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Login redirect URL
LOGIN_REDIRECT_URL = '/dashboard/'
LOGIN_URL = '/accounts/login/'
