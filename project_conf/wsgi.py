import os
from django.core.wsgi import get_wsgi_application

CONF_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CONF_DIR)
CONF_DIR_NAME = os.path.relpath(CONF_DIR, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", CONF_DIR_NAME+".settings")
application = get_wsgi_application()
