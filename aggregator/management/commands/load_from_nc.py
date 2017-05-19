from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import connection

from aggregator.converters.netcdf4 import NetCDF4Converter


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
    )

    def handle(self, *args, **options):
        cnv = NetCDF4Converter(options['file'])
        cnv.write_to_postgres(conn=connection, with_indices=False, stdout=self.stdout)

