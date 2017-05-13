from django.db import connection
from pymongo import MongoClient

from aggregator.connectors.motu.client import motu_download
from aggregator.converters.base import BaseConverter
from aggregator.converters.netcdf4 import NetCDF4Converter
from bdo_platform.settings_management.development_dpap import DOCUMENT_STORE_URL, DOCUMENT_STORE_DB, COPERNICUS_SERVER

# get a mongodb client
client = MongoClient(DOCUMENT_STORE_URL)
db = client.get_database(name=DOCUMENT_STORE_DB)

# get a postgres cursor
cursor = connection.cursor()

# drop collections for the example
# DANGER!
# db.datasets.drop()
# db.dimensions.drop()
# db.variables.drop()
# db.data.drop()

# load nc file & write results
cnv = NetCDF4Converter('global-analysis-forecast-wav-001-023_1493738249917.nc')
# cnv.write_to_disk()
# cnv.write_to_mongo(db=db)
cnv.write_to_postgres(conn=connection)

# cnv = NetCDF4Converter('global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh_1494231860235.nc')
# cnv.write_to_db(db=db)

# motu file
motu_args = (
    COPERNICUS_SERVER['USERNAME'],
    COPERNICUS_SERVER['PASSWORD'],
    BaseConverter.full_input_path(),
    'GLOBAL_ANALYSIS_FORECAST_PHYS_001_015--12345.nc',
)

# motu_download(('-u %s -p %s ' +
#                '-m http://data.ncof.co.uk/mis-gateway-servlet/Motu -s http://purl.org/myocean/ontology/service/database#GLOBAL_ANALYSIS_FORECAST_PHYS_001_015 -d MetO-GLO-PHYS-daily -x 0 -X -0.25 -y -83 -Y 89.75 -t "2016-11-06" -T "2016-11-18" -z 0 -Z 0.0001 -v itzocrtx -v sossheig -v vosaline -v sotemper -v vomecrty -v sokaraml -v votemper -v iicethic -v iiceconc -v itmecrty -v vozocrtx ' +
#                '-o "%s" -f %s') % motu_args)
# cnv = NetCDF4Converter(motu_args[3])
# cnv.write_to_disk()
# cnv.write_to_mongo(db=db)


def pg_example():
    fcnv = NetCDF4Converter('global-analysis-forecast-wav-001-023_1493738249917.nc')
    # cnv.write_to_disk()
    # cnv.write_to_mongo(db=db)
    fcnv.write_to_postgres(conn=connection)
