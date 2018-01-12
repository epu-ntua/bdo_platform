# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import decimal
import datetime
import copy
import time
from collections import OrderedDict
from threading import Thread

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *

from aggregator.models import *


class Query(Model):
    user = ForeignKey(User, related_name='queries')
    title = TextField(default='Untitled query')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    document = JSONField()
    design = JSONField(blank=True, null=True, default=None)
    count = IntegerField(blank=True, null=True, default=None)
    headers = JSONField(blank=True, null=True, default=None)

    def __unicode__(self):
        return '<#%d "%s"%s>' % (self.pk, self.title, ' (%d results)' % self.count if self.count is not None else '')

    @staticmethod
    def operator_to_str(op):
        return {
            # comparison
            'eq': '=',
            'neq': '!=',
            'gt': '>',
            'gte': '>=',
            'lt': '<',
            'lte': '<=',
            'mod': '%',

            # boolean
            '&&': 'AND',
            'and': 'AND',
            '||': 'OR',
            'or': 'OR',
            '!': 'NOT',
            'not': 'NOT',
        }[op.lower()]

    @staticmethod
    def process_filters(filters):
        # end value
        if type(filters) in [str, unicode, int, float]:
            return filters

        # Special case: parsing location filters
        # inside_rect|outside_rect <<lat_south,lng_west>,<lat_north,lng_east>>

        if filters['op'] in ['inside_rect', 'outside_rect', ]:
            rect_start = filters['b'].split('<')[2].split('>,')[0].split(',')
            rect_end = filters['b'].split('>,<')[1].split('>')[0].split(',')

            lat = filters['a'] + '_latitude'
            lng = filters['a'] + '_longitude'
            result = '%s >= %s AND %s <= %s' % (lat, rect_start[0], lat, rect_end[0])
            result += ' AND %s >= %s AND %s <= %s' % (lng, rect_start[1], lng, rect_end[1])

            if filters['op'] == 'outside_rect':
                result = 'NOT(%s)' % result

            return result

        result = '(%s) %s (%s)' % \
               (Query.process_filters(filters['a']),
                Query.operator_to_str(filters['op']),
                Query.process_filters(filters['b']))

        return result

    @staticmethod
    def threaded_fetchall(conn, query, count):

        def fetch_data_page(results, offset=0, limit=100):
            cur = conn.cursor()
            cur.execute(query + ' OFFSET %d LIMIT %d' % (offset, limit))
            results.extend(cur.fetchall())

        # try threaded fetch
        unlimited_results_page_size = 50000
        workers = 5
        current_offset = 0
        all_rows = []

        while current_offset <= count:
            print current_offset
            threads = []
            for w in range(0, workers):
                if current_offset + w * unlimited_results_page_size > count:
                    break

                thread = Thread(target=fetch_data_page,
                                args=(all_rows,
                                      current_offset + w * unlimited_results_page_size,
                                      unlimited_results_page_size))
                thread.start()
                threads.append(thread)

            # wait for all to finish
            for k, thread in enumerate(threads):
                print 'waiting %d' % (k+1)
                thread.join()

            current_offset += unlimited_results_page_size * workers

        return all_rows

    def process(self, dimension_values='', variable='', only_headers=False, commit=True, execute=False, raw_query=False):
        if 'POSTGRES' in Variable.objects.get(pk=self.document['from'][0]['type']).dataset.stored_at:
            from query_designer.query_processors.postgres import process as q_process
        else:
            from query_designer.query_processors.solr import process as q_process

        q_process(dimension_values=dimension_values, variable=variable,
                  only_headers=only_headers, commit=commit,
                  execute=execute, raw_query=raw_query)

    def execute(self, dimension_values='', variable='', only_headers=False, commit=True):
        return self.process(dimension_values, variable, only_headers, commit, execute=True)

    @property
    def raw_query(self):
        # remove several keys from query
        doc = copy.deepcopy(self.document)
        for key in ['limit', 'offset', 'granularity']:
            if key in self.document:
                del self.document[key]

        # get raw query
        res = self.process(dimension_values='', variable='', only_headers=True, commit=False,
                           execute=False, raw_query=True)

        # restore initial doc
        self.document = doc

        return res['raw_query']
