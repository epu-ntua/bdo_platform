from bdo_platform.settings_management.base_settings import *

import dj_database_url

# Update database configuration with $DATABASE_URL.
DATABASES = {
    'default': dj_database_url.config()
}

ALLOWED_HOSTS = ["*"]
DEBUG = False

# heroku server URL
SERVER_URL = 'https://bigdataocea.herokuapp.com'
