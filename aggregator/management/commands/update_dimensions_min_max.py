from django.core.management.base import BaseCommand, CommandError
from django.db import ProgrammingError
from aggregator.models import *
from django.conf import settings
import time
from datetime import datetime
import prestodb


def get_presto_cursor():
    presto_credentials = settings.DATABASES['UBITECH_PRESTO']
    conn = prestodb.dbapi.connect(
        host=presto_credentials['HOST'],
        port=presto_credentials['PORT'],
        user=presto_credentials['USER'],
        catalog=presto_credentials['CATALOG'],
        schema=presto_credentials['SCHEMA'],
    )
    cursor = conn.cursor()
    return cursor


def build_query_string(dim_dataset_name, dim_name):
    min_max_dimension_query = """
                SELECT
                    MIN(%s),
                    MAX(%s)
                FROM %s
            """ % (dim_name, dim_name, dim_dataset_name)
    return min_max_dimension_query


def get_query_results(cursor):
    res = cursor.fetchone()
    min_dim = res[0]
    max_dim = res[1]
    return max_dim, min_dim, res


def translate_time_dims_to_timestamps(res):
    min_dim = time.mktime(datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S.%f").timetuple())
    max_dim = time.mktime(datetime.strptime(res[1], "%Y-%m-%d %H:%M:%S.%f").timetuple())
    if min_dim > max_dim:
        min_dim = 0

    return max_dim, min_dim


class Command(BaseCommand):

    def handle(self, *args, **options):
        # dataset = Dataset.objects.get(pk=124)
        for dataset in Dataset.objects.filter(stored_at='UBITECH_PRESTO'):
            print 'Examining Dataset: ' + str(dataset.title)
            dimensions = dataset.variables.first().dimensions.all()
            cursor = get_presto_cursor()
            for dim in dimensions:
                print 'Examining Dimension: ' + str(dim.title)
                query = build_query_string(dataset.table_name, dim.data_column_name)
                try:
                    cursor.execute(query)
                except ProgrammingError as e:
                    print "query execution failed due to: ", e
                    continue
                max_dim, min_dim, res = get_query_results(cursor)
                if isinstance(res[0], unicode):
                    try:
                        max_dim, min_dim = translate_time_dims_to_timestamps(res)
                    except Exception as e:
                        print "invalid date ", res[0], " or ", res[1], " due  to: ", e
                        continue
                # print 'results'
                # print max_dim, min_dim
                for var in dataset.variables.all():
                    for d in var.dimensions.filter(title=dim.title):
                        if min_dim is not None:
                            d.min = min_dim
                        if max_dim is not None:
                            d.max = max_dim
                        d.save()
                print 'Updated successfully'
        self.stdout.write(self.style.SUCCESS('Successfully updated min and max values for dimensions'))
