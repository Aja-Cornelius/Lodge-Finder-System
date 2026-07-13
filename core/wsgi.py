"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Execute database migrations when the serverless function spins up
from django.core.management import call_command
try:
    print("Executing migrations at runtime startup...")
    call_command('migrate', interactive=False)
    print("Migrations executed successfully!")
except Exception as e:
    print(f"Error running migration at startup: {e}")

application = get_wsgi_application()
