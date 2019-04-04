from django.core.management.base import BaseCommand, CommandError
from aggregator.models import *
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'Collects the datasets/tables on Presto and updates all the metadata'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--dataset', nargs='+', type=int, help='Define the dataset to be used')
        parser.add_argument('-c', '--dimension', nargs='+', type=str, help='Define the dimension name to be altered')

    def handle(self, *args, **options):
        ds = options['dataset']
        dims = options['dimension']

        for d in ds:
            dataset = Dataset.objects.get(pk=int(d))
            for dim in dims:
                try:
                    a_variable = dataset.variables.first()
                    dimension = Dimension.objects.get(variable=a_variable, name=dim)
                    new_var = Variable(dataset=dataset,
                                       name=dimension.name,
                                       title=dimension.title,
                                       unit=dimension.unit,
                                       description=dimension.description,
                                       sameAs=dimension.sameAs,
                                       dataType=dimension.dataType,
                                       original_column_name=dimension.original_column_name)
                    new_var.save()
                    for dimen in Dimension.objects.filter(variable=a_variable):
                        new_dim = Dimension(variable=new_var,
                                            name=dimen.name,
                                            title=dimen.title,
                                            unit=dimen.unit,
                                            description=dimen.description,
                                            sameAs=dimen.sameAs,
                                            dataType=dimen.dataType,
                                            original_column_name=dimen.original_column_name)
                        new_dim.save()
                    for var in dataset.variables.all():
                        dimension = Dimension.objects.get(variable=var, name=dim)
                        dimension.delete()

                    self.stdout.write(self.style.SUCCESS('Successfully altered dimension ' + str(dim) + " for dataset " + str(d)))
                except:
                    pass

            self.stdout.write(self.style.SUCCESS('Successfully altered all dimensions'))
