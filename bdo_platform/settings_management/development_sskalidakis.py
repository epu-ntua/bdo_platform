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

SPARK_SUBMIT_PATH = 'C:\\Spark\\spark-2.2.0-bin-hadoop2.7\\bin\\spark-submit'

TEST_SERVICES = False

ZEPPELIN_URL = 'http://localhost:8080'
ZEPPELIN_DB = 'UBITECH_POSTGRES'

LIVY_URL = 'http://212.101.173.18:55647'

SERVICE_BUILDER_BASE_NOTE = '2DUGVE329'
BASE_NOTE_ARG_PARAGRAPH = '20181012-165458_6385633'
DEBUG = True