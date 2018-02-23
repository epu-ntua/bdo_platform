from bdo_platform.settings_management.development import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bdo-django',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

EMAIL_BACKEND = ''

CONTACT_EMAIL = ''

SPARK_SUBMIT_PATH = ''

PARSER_URL = 'http://127.0.0.1:8080/parser/parse'
