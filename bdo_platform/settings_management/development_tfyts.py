from bdo_platform.settings_management.development import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bdo_platform',
        'USER': 'postgres',
        'PASSWORD': '1832009',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SPARK_SUBMIT_PATH = 'C:\\Spark\\spark-2.2.0-bin-hadoop2.7\\bin\\spark-submit'



