"""
WSGI config for qrail project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrail.settings')

application = get_wsgi_application()
