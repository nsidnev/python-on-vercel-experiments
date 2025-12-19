"""
WSGI config for api project.

Exposes the WSGI callable as a module-level variable named ``app`` for Vercel.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Vercel expects the WSGI app to be named "app"
app = get_wsgi_application()
