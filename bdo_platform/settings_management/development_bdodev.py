from bdo_platform.settings_management.development import *

DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['PASSWORD'] = 'bdo!'

SPARK_SUBMIT_PATH = '/usr/lib/spark/bin/spark-submit'
SERVER_URL = 'http://bdo-dev.epu.ntua.gr'
