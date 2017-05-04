from pymongo import MongoClient

from aggregator.connectors.motu.client import motu_download
from aggregator.converters.base import BaseConverter
from aggregator.converters.netcdf4 import NetCDF4Converter
from bdo_platform.settings_management.development_dpap import DOCUMENT_STORE_URL, DOCUMENT_STORE_DB, COPERNICUS_SERVER

# get a mongodb client
client = MongoClient(DOCUMENT_STORE_URL)
db = client.get_database(name=DOCUMENT_STORE_DB)

# drop collections for the example
# DANGER!
db.datasets.drop()
db.dimensions.drop()
db.variables.drop()
db.data.drop()

# load nc file & write results
# cnv = NetCDF4Converter('global-analysis-forecast-wav-001-023_1493738249917.nc')
# cnv.write_to_disk()
# cnv.write_to_db(db=db)

# motu file
motu_args = (
    COPERNICUS_SERVER['USERNAME'],
    COPERNICUS_SERVER['PASSWORD'],
    COPERNICUS_SERVER['HOST'],
    BaseConverter.full_input_path(),
    'BALTICSEA_ANALYSIS_FORECAST_BIO_003_007-TDS--12345.nc',
)

motu_download(('-u %s -p %s -m %s ' +
               '-s BALTICSEA_ANALYSIS_FORECAST_BIO_003_007-TDS -d dataset-bal-analysis-forecast-bio-dailymeans -x 9.0416660308838 -X 30.319446563721 -y 53.024993896484 -Y 65.891662597656 -t "2017-05-01" -T "2017-05-04" -z 0 -Z 15.0001 -v Nitrate -v Phosphate -v Chl_a -v DO ' +
               '-o "%s" -f %s') % motu_args)
cnv = NetCDF4Converter(motu_args[4])
# cnv.write_to_disk()
cnv.write_to_db(db=db)
