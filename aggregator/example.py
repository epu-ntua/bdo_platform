from django.db import connection
from pymongo import MongoClient

from aggregator.connectors.motu.client import motu_download
from aggregator.converters.base import BaseConverter
from aggregator.converters.netcdf4 import NetCDF4Converter
from bdo_platform.settings_management.development_dpap import DOCUMENT_STORE_URL, DOCUMENT_STORE_DB, COPERNICUS_SERVER


def example():
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
    # cnv = NetCDF4Converter('global-analysis-forecast-wav-001-023_1493738249917.nc')
    # cnv.write_to_disk()
    # cnv.write_to_mongo(db=db)
    # cnv.write_to_postgres(conn=connection)

    # cnv = NetCDF4Converter('global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh_1494231860235.nc')
    # cnv.write_to_db(db=db)

    # motu file
    motu_args = (
        COPERNICUS_SERVER['USERNAME'],
        COPERNICUS_SERVER['PASSWORD'],
        BaseConverter.full_input_path(),
        'GLOBAL_ANALYSIS_FORECAST_PHYS_001_015--12345.nc',
    )

    motu_download(('-u %s -p %s ' +
                   '-m http://data.ncof.co.uk/motu-web/Motu -s NORTHWESTSHELF_ANALYSIS_FORECAST_BIO_004_002_b -d MetO-NWS-BIO-dm-ATTN -x -19.888889312744 -X 12.999670028687 -y 40.066669464111 -Y 65.001251220703 -t "2017-05-14 12:00:00" -T "2017-05-18 12:00:00" -z 0 -Z 3.0001 -v attn ' +
                   '-o "%s" -f %s') % motu_args)
    # cnv = NetCDF4Converter(motu_args[3])
    # cnv.write_to_disk()
    # cnv.write_to_mongo(db=db)


def pg_example(stdout=None):
    #fcnv = NetCDF4Converter('global-analysis-forecast-wav-001-023_1493738249917.nc')
    fcnv = NetCDF4Converter('sv03-med-ingv-cur-rean-d_1495100343588.nc')
    # fcnv = NetCDF4Converter('global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh_1494231860235.nc')
    # fcnv = NetCDF4Converter('METO-NWS-BIO-DM-ATTN--12345.nc')
    # cnv.write_to_disk()
    # cnv.write_to_mongo(db=db)
    fcnv.write_to_postgres(conn=connection, with_indices=False, stdout=stdout)

