"""
WSGI config for ReadQuest project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')

# On Vercel, the filesystem is read-only except /tmp.
# Collect static files and run migrations on each cold start.
if os.environ.get('VERCEL'):
    import django
    django.setup()
    from django.core.management import call_command
    try:
        call_command('collectstatic', '--noinput', verbosity=0)
    except Exception:
        pass
    try:
        call_command('migrate', '--run-syncdb', verbosity=0)
    except Exception:
        pass

application = get_wsgi_application()
app = application
