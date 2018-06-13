from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import connection

from aggregator.converters.netcdf4 import NetCDF4Converter
from mongo_client import get_mongo_db


class Command(BaseCommand):
    help = 'Import dataset from nc file to postgres'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("-f",
            "--file",
            dest="file",
            help="NC file",
            metavar="FILE")
        parser.add_argument("-t",
            "--target",
            dest="target",
            help="Where data should be stored (either `postgres` or `mongo`)",
            metavar="TARGET")



    def handle(self, *args, **options):
        target = options['target']
        target_dict = {
            'type': 'postgres',
            'cursor': connection.cursor(),
            'with_indices': True
        }

        if target == 'mongo':
            target_dict = {
                'type': 'mongo',
                'db': get_mongo_db(),
                'with_indices': True
            }

        cnv = NetCDF4Converter(options['file'])
        cnv.store(target=target_dict, stdout=self.stdout)

