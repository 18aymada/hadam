"""
WSGI config for hadam_ict project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

# IMPORTANT: must match your INNER project folder name
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hadam_ict.settings')

application = get_wsgi_application()