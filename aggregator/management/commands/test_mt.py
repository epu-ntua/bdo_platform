

from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import connection

from aggregator.converters.netcdf4 import NetCDF4Converter
from mongo_client import get_mongo_db


class Command(BaseCommand):
    help = 'Import dataset from nc file to postgres'

    def handle(self, *args, **options):
        from aggregator.models import Dataset
        Dataset.objects.filter(title='DE_SAMPLE').delete()
        from aggregator.converters.csv_mt import CSVMarineTrafficConverter
        from django.db import connection
        target_dict = {'type': 'postgres', 'cursor': connection.cursor(), 'with_indices': True}
        CSVMarineTrafficConverter('DE_SAMPLE.csv').store(target_dict)
