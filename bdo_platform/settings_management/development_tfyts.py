from bdo_platform.settings_management.development import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bdo_platform',
        'USER': 'postgres',
        'PASSWORD': '1234567',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SPARK_SUBMIT_PATH = 'C:\\Spark\\spark-2.2.0-bin-hadoop2.7\\bin\\spark-submit'

INSTALLED_APPS += (
    'djgeojson',
    'requestservice.apps.RequestserviceConfig',
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, os.path.join(BASE_DIR, 'requestservice/templates/requestservice')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bdo_platform.wsgi.application'




