from pymongo import MongoClient

from aggregator.connectors.motu.client import motu_download
from aggregator.converters.base import BaseConverter
from aggregator.converters.netcdf4 import NetCDF4Converter
from bdo_platform.settings_management.development_dpap import DOCUMENT_STORE_URL, DOCUMENT_STORE_DB, COPERNICUS_SERVER

# get a mongodb client
client = MongoClient(DOCUMENT_STORE_URL)
db = client.get_database(name=DOCUMENT_STORE_DB)

# load nc file & write results
cnv = NetCDF4Converter('global-analysis-forecast-wav-001-023_1493738249917.nc')
# cnv.write_to_disk()
cnv.write_to_db(db=db)

# motu file
motu_args = (
    COPERNICUS_SERVER['USERNAME'],
    COPERNICUS_SERVER['PASSWORD'],
    COPERNICUS_SERVER['HOST'],
    BaseConverter.full_input_path(),
    'MEDSEA_ANALYSIS_FORECAST_BIO_006_006-TDS--12345.nc',
)

# motu_download(('-u %s -p %s -m %s ' +
#                '-s MEDSEA_ANALYSIS_FORECAST_BIO_006_006-TDS -d cmemsv02-med-ogs-bio-an-fc-d ' +
#                '-x -5.5625 -X 36.25 -y 30.1875 -Y 45.9375 ' +
#                '-t "2017-05-11 12:00:00" -T "2017-05-11 12:00:00" -z 1.4721 -Z 1.4722 ' +
#                '-v ppn -v dox -o "%s" -f %s') % motu_args)
cnv = NetCDF4Converter(motu_args[4])
# cnv.write_to_disk()
cnv.write_to_db(db=db)
