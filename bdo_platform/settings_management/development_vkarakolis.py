from bdo_platform.settings_management.development import *

SPARK_SUBMIT_PATH = ''

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bdo_platform',
        'USER': 'postgres',
        'PASSWORD': 'password',
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


