from bdo_platform.settings_management.development import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bdo_platform',
        'USER': 'postgres',
        'PASSWORD': 'engage1!',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}

# copernicus server
COPERNICUS_SERVER = {
    'HOST': 'http://nrtcmems.mercator-ocean.fr/mis-gateway-servlet/Motu',
    'USERNAME': 'smouzakitis',
    'PASSWORD': 'SpirosCMEMS2017',
}

SPARK_SUBMIT_PATH = ''
