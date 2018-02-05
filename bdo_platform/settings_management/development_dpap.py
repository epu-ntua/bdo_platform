from bdo_platform.settings_management.development import *

# use local mongo on dev
DOCUMENT_STORE_URL = 'mongodb://localhost:27017/'
DOCUMENT_STORE_DB = 'bdo_platform'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdo_platform_2',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# copernicus server
COPERNICUS_SERVER = {
    'HOST': 'http://nrtcmems.mercator-ocean.fr/mis-gateway-servlet/Motu',
    'USERNAME': 'dpapaspyros',
    'PASSWORD': 'DimitriosCMEMS2017',
}

# spark submit
SPARK_SUBMIT_PATH = 'C:\\opt\\spark\\spark-2.1.1-bin-hadoop2.7\\bin\\spark-submit.cmd'
