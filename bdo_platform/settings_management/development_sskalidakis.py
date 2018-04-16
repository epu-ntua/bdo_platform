from bdo_platform.settings_management.development import *
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bdo_platform',
        'USER': 'postgres',
        'PASSWORD': 'sssshmmy',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SPARK_SUBMIT_PATH = ''
#
# # dev server URL
# SERVER_URL = 'http://127.0.0.1:8000'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True