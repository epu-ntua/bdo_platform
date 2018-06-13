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

PARSER_JWT = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJiZG8iLCJleHAiOjE1NTIzODQ1NDYsInJvbGUiOiJST0xFX0FETUlOIn0.wI8o1voaOJMUHbAxziKzWBTADPLx2sMLohedavoxhOVauQtI8DDEKxUBJm6MQw02962alVn_Xqus4jGSB_Adew'
# PARSER_URL = 'http://127.0.0.1:8080'
PARSER_URL = 'http://212.101.173.21:8085'
UPLOAD_URL = PARSER_URL + '/file/upload'
DOWNLOAD_URL = PARSER_URL + '/file/download'
PARSE_URL = PARSER_URL + '/parse'
PARSABLE_FILES_URL = PARSER_URL + "/parsable"



ZEPPELIN_URL = 'http://localhost:8080'
ZEPPELIN_DB = 'default'
