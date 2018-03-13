from bdo_platform.settings_management.development import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bdo-django',
        'USER': 'bdo',
        'PASSWORD': 'df195715HBdhahfP',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

EMAIL_BACKEND = ''

CONTACT_EMAIL = ''

SPARK_SUBMIT_PATH = ''

PARSER_JWT = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJiZG8iLCJleHAiOjE1NTIzODQ1NDYsInJvbGUiOiJST0xFX0FETUlOIn0.wI8o1voaOJMUHbAxziKzWBTADPLx2sMLohedavoxhOVauQtI8DDEKxUBJm6MQw02962alVn_Xqus4jGSB_Adew'
PARSER_URL = 'http://127.0.0.1:8080'
UPLOAD_URL = PARSER_URL + '/file/upload'
DOWNLOAD_URL = PARSER_URL + '/file/download'
PARSE_URL = PARSER_URL + '/parse'
PARSABLE_FILES_URL = PARSER_URL + "/parsable"
