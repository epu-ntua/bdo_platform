from bdo_platform.settings_management.base_settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdo_platform',
    }
}

# No emails should be sent on development
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
CONTACT_EMAIL = 'dipapaspyros@gmail.com'

# dev server URL
SERVER_URL = 'http://127.0.0.1:8000'

TEST_SERVICES = False
