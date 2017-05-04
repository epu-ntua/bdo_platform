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
    'ARC-NERSC-ARC-TOPAZ4_PHYS-RAN-TDS--12345.nc',
)

motu_download(('-u %s -p %s -m %s ' +
               '-s ARC-NERSC-ARC-TOPAZ4_PHYS-RAN-TDS -d dataset-ran-arc-myoceanv2-be -x -180 -X 180 -y 34.69 -Y 90 -t "2015-11-15" -T "2015-12-15" -z 5 -Z 3000.0001 -v time -v ssh -v x -v y -v u -v bsfd -v latitude -v model_depth -v vice -v temperature -v hsnow -v longitude -v uice -v salinity -v v -v depth -v fice -v mlp -v btemp -v hice ' +
               '-o "%s" -f %s') % motu_args)
cnv = NetCDF4Converter(motu_args[4])
# cnv.write_to_disk()
cnv.write_to_db(db=db)
