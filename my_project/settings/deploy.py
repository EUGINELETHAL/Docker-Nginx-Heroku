import os

import dj_database_url

from . import *  # noqa: F403

# This is NOT a complete production settings file. For more, see:
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

DEBUG = True

ALLOWED_HOSTS = ['localhost']

DATABASES['default'] = dj_database_url.config(conn_max_age=600)  # noqa: F405

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405


