from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import connection

from aggregator.converters.netcdf4 import NetCDF4Converter
from mongo_client import get_mongo_db


class Command(BaseCommand):
    help = 'Import dataset from nc file to postgres'
    option_list = BaseCommand.option_list + (
        make_option(
            "-f",
            "--file",
            dest="file",
            help="NC file",
            metavar="FILE"
        ),
        make_option(
            "-t",
            "--target",
            dest="target",
            help="Where data should be stored (either `postgres` or `mongo`)",
            metavar="TARGET"
        ),
    )

    def handle(self, *args, **options):
        target = options['target']
        target_dict = {
            'type': 'postgres',
            'cursor': connection.cursor(),
            'with_indices': False
        }

        if target == 'mongo':
            target_dict = {
                'type': 'mongo',
                'db': get_mongo_db()
            }

        cnv = NetCDF4Converter(options['file'])
        cnv.store(target=target_dict, stdout=self.stdout)

