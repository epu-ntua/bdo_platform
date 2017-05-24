from django.db import connection
from aggregator.converters.random_cnv import RandomDataConverter
from mongo_client import get_mongo_db

to_postgres = {
    'type': 'postgres',
    'cursor': connection.cursor(),
    'with_indices': False
}

to_mongo = {
    'type': 'mongo',
    'db': get_mongo_db(),
}

dimensions = {
    'time': {
        'unit': 'hours since 2016-01-01',
        'min': 0,
        'max': 9,
        'step': 1
    },
    'lat': {
        'unit': 'degree_east',
        'min': -10,
        'max': 39.8,
        'step': 0.2
    },
    'lng': {
        'unit': 'degree_north',
        'min': 10,
        'max': 49.8,
        'step': 0.2
    }
}

cnv = RandomDataConverter(dimensions)
