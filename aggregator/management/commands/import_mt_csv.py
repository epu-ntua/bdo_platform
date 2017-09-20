

from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import connection

from mongo_client import get_mongo_db

from aggregator.models import Dataset
from aggregator.converters.csv_mt import CSVMarineTrafficConverter
from django.db import connection


class Command(BaseCommand):
    help = 'Import MarineTraffic CSV export'
    option_list = BaseCommand.option_list + (
        make_option(
            "-f",
            "--file",
            dest="file",
            help="CSV file name",
            metavar="FILE"
        ),
        make_option(
            "--variables",
            dest="variables",
            help="Comma-separated list of variables (choices are: speed, course, heading)",
            metavar="FILE"
        ),
    )

    def handle(self, *args, **options):
        dataset_title = 'MarineTraffic vessel positions'
        store_args = {
            'target': {
                'type': 'postgres',
                'cursor': connection.cursor(),
                'with_indices': True
            },
            'stdout': self.stdout,
        }

        # if already uploaded, update existing dataset
        if Dataset.objects.filter(title=dataset_title).exists():
            store_args['update_dataset'] = Dataset.objects.filter(title=dataset_title)[0]

        # convert & store
        CSVMarineTrafficConverter(name=options['file'], title=dataset_title,
                                  selected_variables=(options['variables'] or '*')).store(**store_args)
