from django.core.management.base import BaseCommand, CommandError
from aggregator.models import *
from django.conf import settings
import prestodb
import time


class Command(BaseCommand):
    help = 'Collects the datasets/tables on Presto and updates all the metadata'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--dataset', nargs='+', type=int, help='Define the dataset to be used')
        parser.add_argument('-i', '--variable', type=str, help='Define the variable name of the identifier')
        parser.add_argument('-t', '--type', type=str, help='Define the variable type of the identifier')

    def handle(self, *args, **options):
        ds = options['dataset']
        col_name = options['variable']
        type = options['type']

        for d in ds:
            dataset = Dataset.objects.get(pk=int(d))

            table_name = dataset.table_name

            # GET THE TABLES FROM PRESTO
            presto_credentials = settings.DATABASES['UBITECH_PRESTO']
            conn_presto = prestodb.dbapi.connect(
                host=presto_credentials['HOST'],
                port=presto_credentials['PORT'],
                user=presto_credentials['USER'],
                catalog=presto_credentials['CATALOG'],
                schema=presto_credentials['SCHEMA'],
            )
            cursor_presto = conn_presto.cursor()
            cursor_presto.execute("SELECT DISTINCT " + col_name + " FROM  " + table_name + " ")
            start = time.time()
            result = cursor_presto.fetchall()
            end = time.time()
            self.stdout.write(self.style.SUCCESS("--- %s seconds ---" % (end - start)))

            vis = Vessel_Identifier.objects.filter(dataset=dataset, column_name=col_name)
            if len(vis) > 0:
                vi = vis[0]
            else:
                vi = Vessel_Identifier(dataset=dataset, column_name=col_name)

            if type == "str":
                vi.values_list = [[str(x[0])] for x in result]
            elif type == "int":
                vi.values_list = [[int(x[0])] for x in result]
            vi.save()

            self.stdout.write(self.style.SUCCESS("--- %s ids ---" % (str(len(vi.values_list)))))
            self.stdout.write(self.style.SUCCESS('Successfully collected and updated the vessel identifiers'))
