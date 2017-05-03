from bdo_platform.settings_management.development import *

# use local mongo on dev
DOCUMENT_STORE_URL = 'mongodb://localhost:27017/'
DOCUMENT_STORE_DB = 'bdo'

# copernicus server
COPERNICUS_SERVER = {
    'HOST': 'http://cmems-med-mfc.eu/motu-web/Motu',
    'USERNAME': 'dpapaspyros',
    'PASSWORD': 'DimitriosCMEMS2017',
}
