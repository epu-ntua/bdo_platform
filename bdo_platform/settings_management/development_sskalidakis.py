from bdo_platform.settings_management.development import *
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bdo_local_database',
        'USER': 'postgres',
        'PASSWORD': 'sssshmmy',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'UBITECH_POSTGRES': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'bigdataocean',
            'USER': 'bdo',
            'PASSWORD': 'df195715HBdhahfP',
            'HOST': '212.101.173.21',
            'PORT': '5432',
        }
}

SPARK_SUBMIT_PATH = ''
#
# # dev server URL
# SERVER_URL = 'http://127.0.0.1:8000'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True