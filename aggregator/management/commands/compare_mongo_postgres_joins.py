import json
import random
import time
import traceback
from optparse import make_option

from django.core.management import call_command
from django.core.management.base import BaseCommand

from django.db import connection
from aggregator.converters.random_cnv import RandomDataConverter
from aggregator.management.commands.generate_dataset import generate_dataset
from mongo_client import get_mongo_db


class Command(BaseCommand):
    help = 'Compares Mongo & Postgres backends using random dataset generation'
    option_list = BaseCommand.option_list + (
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
            "-N",
            "--no-joins",
            dest="no_joins",
            action="store_true",
            help="Skip all join queries",
            metavar="NO_JOINS"
        ),
        make_option(
            "-n",
            "--no-mongo-joins",
            dest="no_mongo_joins",
            action="store_true",
            help="Skip join queries for mongo",
            metavar="NO_MONGO_JOINS"
        ),
    )

    def prepare_queries(self, pg_datasets, mongo_datasets):
        queries = [
            # simple select/filter
            {
                'title': 'Simple select/filter',
                'type': 'filter',

                'postgres':
                """
                SELECT * FROM (
                    SELECT <v1a>, <v2a>, <v3a>, value
                    FROM <t1>
                    WHERE <v1a> >= -9.8 AND <v1a> <= -9.6
                ) AS Q1
                ORDER BY value
                """,

                'mongo': {
                    'collection': "<c1>",
                    'find': {
                        'lat': {'$gte': -9.8, '$lte': -9.6},
                    },
                }
            },

            # strict join
            {
                'title': 'Value difference in exact location & time',
                'type': 'join',

                'postgres':
                """
                SELECT * FROM (
                    SELECT <v1a>, <v2a>, <v3a>, (<t2>.value - <t1>.value) AS difv
                    FROM <t1>
                    JOIN <t2> ON <v1a>=<v1b> AND <v2a>=<v2b> AND <v3a>=<v3b>
                ) AS Q1
                ORDER BY difv
                """,

                'mongo': {
                    'collection': "<c1>",
                    'aggregates': [
                        {
                            "$lookup":
                                {
                                    "from": "<c2>",
                                    "localField": "<v1>",
                                    "foreignField": "<v1>",
                                    "as": "c2"
                                }
                        }, {
                            "$unwind": "$c2"
                        }, {
                            "$project": {
                                'lat': 1,
                                'lng': 1,
                                'time': 1,
                                'isLatEqual': { "$eq" : [ "$lat", "$c2.lat" ] },
                                'isLngEqual': { "$eq" : [ "$lng", "$c2.lng" ] },
                                'isTimeEqual': { "$eq" : [ "$time", "$c2.time" ] },
                                'diff': {'$subtract': ["$value", "$c2.value"]},
                            },
                        },
                        {"$match": {'isLngEqual': True, 'isTimeEqual': True}},
                        {"$sort": {'diff': 1}},
                    ]
                }
            },

            {
                'title': 'Value difference at the same time',
                'type': 'join',

                'postgres':
                """
                SELECT * FROM (
                    SELECT <v1a>, <v2a>, <v3a>, (<t2>.value - <t1>.value) AS difv
                    FROM <t1>
                    JOIN <t2> ON <v3a>=<v3b>
                ) AS Q1
                ORDER BY difv
                """,

                'mongo': {
                    'collection': "<c1>",
                    'aggregates': [
                        {
                            "$lookup":
                                {
                                "from": "<c2>",
                                "localField": "<v3>",
                                "foreignField": "<v3>",
                                "as": "c2"
                                }
                        }, {
                            "$unwind": "$c2"
                        }, {
                            "$project": {
                                'lat': 1,
                                'lng': 1,
                                'time': 1,
                                'diff': {'$subtract': ["$value", "$c2.value"]},
                            },
                        },
                        {"$sort": {'diff': 1}},
                    ]
                }
            },
        ]

        for query in queries:
            # PG replacements
            q = query['postgres']

            for d_id in (['a', 'b'] if pg_datasets[1] else ['a']):
                # replace table names
                q = q.replace('<t%d>' % (['a', 'b'].index(d_id) + 1),
                              pg_datasets[['a', 'b'].index(d_id)].variables.get().data_table_name)

                # replace column names
                for dim_id in range(1, pg_datasets[['a', 'b'].index(d_id)].variables.get().dimensions.all().count() + 1):
                    q = q.replace('<v%d%s>' % (dim_id, d_id),
                                  pg_datasets[['a', 'b'].index(d_id)].variables.get().dimensions.all()[dim_id - 1].data_column_name)

            query['postgres'] = q

            # MONGO replacements
            q = json.dumps(query['mongo'])

            c1 = get_mongo_db().variables.find_one({'dataset_id': mongo_datasets[0]})
            if mongo_datasets[1]:
                c2 = get_mongo_db().variables.find_one({'dataset_id': mongo_datasets[1]})
            else:
                c2 = {'name': ''}

            q = q.replace('<c1>', c1['name']).replace('<c2>', c2['name'])

            for idx, dim in enumerate(c1['dimensions']):
                q = q.replace('<v%d>' % (idx + 1), dim)

            query['mongo'] = json.loads(q)

        return queries

    def handle(self, *args, **options):
        skip_mongo_joins = options['no_mongo_joins'] or False
        skip_joins = options['no_joins'] or False
        if skip_joins:
            skip_mongo_joins = True
        v_name = 'rnd_%s' % ''.join([str(random.choice(range(1, 10))) for _ in range(1, 5)])

        # call for postgres
        pd1, p_size, p_time = generate_dataset(target='postgres', variable=v_name + '_1', sizes=options['sizes'], stdout=self.stdout)
        if not skip_joins:
            pd2, _, _ = generate_dataset(target='postgres', variable=v_name + '_2', sizes=options['sizes'], stdout=self.stdout)
        else:
            pd2 = None

        # call for mongo
        md1, m_size, m_time = generate_dataset(target='mongo', variable=v_name + '_1', sizes=options['sizes'], stdout=self.stdout)
        if not skip_mongo_joins:
            md2, _, _ = generate_dataset(target='mongo', variable=v_name + '_2', sizes=options['sizes'], stdout=self.stdout)
        else:
            md2 = None

        # print insert times
        print('')
        print('Data import')
        print('===========')
        print('\tDatabase\tDuration\t\t#Rows')
        print ('\tPostgres\t%.3f sec\t\t%d' % (p_time, p_size))
        print ('\tMongoDB\t\t%.3f sec\t\t%d' % (m_time, m_size))

        # print disk usage info
        m_disk_size = get_mongo_db().command("collstats", v_name + '_1')['size'] / 1024.0 / 1024.0
        cur = connection.cursor()
        cur.execute(
            """
            SELECT *, pg_size_pretty(total_bytes) AS total
                    , pg_size_pretty(index_bytes) AS INDEX
                    , pg_size_pretty(toast_bytes) AS toast
                    , pg_size_pretty(table_bytes) AS TABLE
                  FROM (
                  SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (
                      SELECT c.oid,nspname AS table_schema, relname AS TABLE_NAME
                              , c.reltuples AS row_estimate
                              , pg_total_relation_size(c.oid) AS total_bytes
                              , pg_indexes_size(c.oid) AS index_bytes
                              , pg_total_relation_size(reltoastrelid) AS toast_bytes
                          FROM pg_class c
                          LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                          WHERE relkind = 'r'
                  ) a
                ) a
                WHERE table_name = '%s';
            """ % pd1.variables.get().data_table_name
        )
        p_disk_size = cur.fetchone()[4] / 1024.0 / 1024.0

        print('')
        print('Disk usage')
        print('===========')
        print('\tDatabase\tSize (MB)\t\t#Rows')
        print ('\tPostgres\t%.2f MB\t\t%d' % (p_disk_size, p_size))
        print ('\tMongoDB\t\t%.2f MB\t\t%d' % (m_disk_size, m_size))

        # prepare queries
        queries = self.prepare_queries(pg_datasets=[pd1, pd2], mongo_datasets=[md1, md2])

        # execute queries
        for q in queries:
            if skip_joins and q['type'] == 'join':
                continue

            print('')
            title = 'Query: %s' % q['title']
            print(title)
            print(''.join(['=' for _ in title]))
            print('\tDatabase\tDuration\t\t#Results')

            try:
                t1 = time.time()
                cur = connection.cursor()
                cur.execute(q['postgres'])
                cnt = len([x for x in cur.fetchall()])
                t2 = time.time()

                print ('\tPostgres\t%.3f sec\t\t%d' % ((t2 - t1), cnt))
            except:
                traceback.print_exc()
                print ('\tPostgres failed')

            if skip_mongo_joins and q['type'] == 'join':
                continue
            try:
                t1 = time.time()
                f = get_mongo_db().get_collection(q['mongo']['collection'])
                if 'find' in q['mongo']:
                    f = f.find(q['mongo']['find'])
                if 'aggregates' in q['mongo']:
                    f = f.aggregate(q['mongo']['aggregates'])
                if 'limit' in q['mongo']:
                    f = f.limit(q['mongo']['limit'])
                cnt = [x for x in f].__len__()
                t2 = time.time()

                print ('\tMongoDB\t\t%.3f sec\t\t%d' % ((t2 - t1), cnt))
            except:
                traceback.print_exc()
                print ('\tMongoDB failed')

        # drop everything
        pd1.delete()
        if pd2:
            pd2.delete()

        for md in [md1, md2]:
            if md is None:
                continue

            db = get_mongo_db()
            variable = db.variables.find_one({'dataset_id': md})
            db.get_collection(variable['name']).drop()
            db.dimensions.delete_many({'variable_id': variable['_id']})
            db.variables.delete_many({'dataset_id': md})
            db.datasets.delete_many({'_id': md})



