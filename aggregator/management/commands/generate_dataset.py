import time
from optparse import make_option
from django.core.management.base import BaseCommand

from django.db import connection
from aggregator.converters.random_cnv import RandomDataConverter
from mongo_client import get_mongo_db


def generate_dataset(target, variable, sizes, index=False, stdout=None):
    target_dict = {
        'type': 'postgres',
        'cursor': connection.cursor(),
        'with_indices': index
    }

    if target == 'mongo':
        target_dict = {
            'type': 'mongo',
            'db': get_mongo_db(),
            'with_indices': index,
        }

    dimensions = {
        'time': {
            'unit': 'hours since 2016-01-01',
            'min': 0,
            'step': 1
        },
        'lat': {
            'unit': 'degree_east',
            'min': -30,
            'step': 0.2
        },
        'lng': {
            'unit': 'degree_north',
            'min': 10,
            'step': 0.2
        }
    }

    total_items = 1
    for idx, d_name in enumerate(['time', 'lat', 'lng']):
        n_of_steps = int(sizes.split(',')[idx].strip())
        dimensions[d_name]['max'] = dimensions[d_name]['min'] + (n_of_steps - 1) * dimensions[d_name]['step']
        total_items *= n_of_steps

    cnv = RandomDataConverter(v_name=variable, dimensions=dimensions)
    t1 = time.time()
    dataset = cnv.store(target=target_dict, stdout=stdout)
    t2 = time.time()

    return dataset, total_items, (t2 - t1)


class Command(BaseCommand):
    help = 'Generates a random dataset'
    option_list = BaseCommand.option_list + (
        make_option(
            "-V",
            "--variable",
            dest="variable",
            help="The name of the random variable",
            metavar="VARIABLE"
        ),
        make_option(
            "-s",
            "--sizes",
            dest="sizes",
            help="Comma-separate the number of entries for dimensions <time,lat,lng>",
            metavar="SIZES"
        ),
        make_option(
            "-t",
            "--target",
            dest="target",
            help="Where data should be stored (either `postgres` or `mongo`)",
            metavar="TARGET"
        ),
        make_option(
            "-i",
            "--index",
            dest="index",
            action="store_true",
            help="Add indices",
            metavar="INDEX"
        ),
    )

    def handle(self, *args, **options):
        _, items, total_time = generate_dataset(options['target'], options['variable'], options['sizes'],
                                                index=options['index'] or False, stdout=self.stdout)

        print('Type: %s' % options['target'])
        print('Number of items: %d (%s)' % (items, options['sizes']))
        print('Time to insert (sec): %.3f' % total_time)


