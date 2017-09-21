from bdo_platform.settings_management.development import *

DATABASES['default']['user'] = 'postgres'
DATABASES['default']['password'] = 'bdo!'

SPARK_SUBMIT_PATH = '/usr/lib/spark/bin/spark-submit'
SERVER_URL = 'http://bdo-dev.epu.ntua.gr'
