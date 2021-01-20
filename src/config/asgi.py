import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')

from configurations.management import execute_from_command_line

application = get_asgi_application()
