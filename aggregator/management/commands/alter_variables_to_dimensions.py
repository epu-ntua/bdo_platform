from django.core.management.base import BaseCommand, CommandError
from aggregator.models import *
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'Collects the datasets/tables on Presto and updates all the metadata'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--dataset', nargs='+', type=int, help='Define the dataset to be used')
        parser.add_argument('-c', '--variable', nargs='+', type=str, help='Define the variable name to be altered')

    def handle(self, *args, **options):
        ds = options['dataset']
        vs = options['variable']

        for d in ds:
            dataset = Dataset.objects.get(pk=int(d))
            for v in vs:
                try:
                    variable = dataset.variables.get(name=v)
                    for var in dataset.variables.all():
                        new_dim = Dimension(variable=var,
                                            name=variable.name,
                                            title=variable.title,
                                            unit=variable.unit,
                                            description=variable.description,
                                            sameAs=variable.sameAs,
                                            dataType=variable.dataType,
                                            original_column_name=variable.original_column_name)
                        new_dim.save()
                    variable.delete()
                    self.stdout.write(self.style.SUCCESS('Successfully altered dimension ' + str(v) + " for dataset " + str(d)))
                except:
                    pass

            self.stdout.write(self.style.SUCCESS('Successfully altered all variables'))
