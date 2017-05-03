from bdo_platform.settings_management.base_settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdo_platform',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# No emails should be sent on development
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
CONTACT_EMAIL = 'energymanagement.bemat@gmail.com'
