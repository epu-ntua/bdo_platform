from bdo_platform.settings_management.development import *

# use local mongo on dev
DOCUMENT_STORE_URL = 'mongodb://localhost:27017/'
DOCUMENT_STORE_DB = 'bdo'

DATABASES['default']['PASSWORD'] = '1234'

# copernicus server
COPERNICUS_SERVER = {
    'HOST': 'http://nrtcmems.mercator-ocean.fr/mis-gateway-servlet/Motu',
    'USERNAME': 'dpapaspyros',
    'PASSWORD': 'DimitriosCMEMS2017',
}
