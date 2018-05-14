from bdo_platform.settings_management.development import *

SPARK_SUBMIT_PATH = 'C:\\spark\\bin\\spark-submit'

TEST_SERVICES = False

ZEPPELIN_URL = 'http://localhost:8080'
ZEPPELIN_DB = 'UBITECH_POSTGRES'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdo_platform',
        'USER': 'postgres',
        'PASSWORD': '13131313',
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
