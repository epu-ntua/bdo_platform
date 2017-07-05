# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import decimal
import datetime
import copy
import time
from collections import OrderedDict

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *

from aggregator.models import *


class ResultEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, float):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


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

        result = '(%s) %s (%s)' % \
               (Query.process_filters(filters['a']),
                Query.operator_to_str(filters['op']),
                Query.process_filters(filters['b']))

        return result

    def process(self, dimension_values='', variable='', only_headers=False, commit=True, execute=False, raw_query=False):
        if dimension_values:
            dimension_values = dimension_values.split(',')
        else:
            dimension_values = []

        # select
        selects = OrderedDict()
        headers = []
        header_sql_types = []

        aliases = []
        for _from in self.document['from']:
            v_obj = Variable.objects.get(pk=_from['type'])

            for s in _from['select']:
                sql_type = None
                if s['type'] != 'VALUE':
                    dimension = Dimension.objects.get(pk=s['type'])
                    column_name = dimension.data_column_name
                    column_unit = dimension.unit
                    column_axis = dimension.axis
                    column_step = dimension.step
                    sql_type = dimension.sql_type

                else:
                    column_name = 'value'
                    column_unit = v_obj.unit
                    column_axis = None
                    column_step = None
                    sql_type = 'double precision'

                selects[s['name']] = {'column': column_name, 'table': v_obj.data_table_name}

                if 'joined' not in s:
                    header_sql_types.append(sql_type)
                    headers.append({
                        'title': s['title'],
                        'name': s['name'],
                        'unit': column_unit,
                        'step': column_step,
                        'quote': '' if sql_type.startswith('numeric') or sql_type.startswith('double') else "'",
                        'isVariable': s['type'] == 'VALUE',
                        'axis': column_axis,
                    })

                    # add fields to select clause
                    aliases.append('%s.%s AS %s' % (v_obj.data_table_name, selects[s['name']]['column'], s['name']))

        # select
        select_clause = 'SELECT ' + ','.join(aliases) + '\n'

        # from
        from_clause = 'FROM ' + selects[selects.keys()[0]]['table'] + '\n'

        # join
        join_clause = ''
        for _from in self.document['from'][1:]:
            joins = []
            for s in _from['select']:
                if 'joined' in s:
                    if s['name'].endswith('location_latitude'):
                        js = [
                            (s['name'], s['joined'] + '_latitude'),
                            (s['name'].replace('_latitude', '_longitude'), s['joined'] + '_longitude'),
                        ]
                    elif s['name'].endswith('location_longitude'):
                        js = []
                    else:
                        js = [(s['name'], s['joined'])]

                    for j in js:
                        joins.append('%s=%s' %
                                     (selects[j[0]]['column'],
                                      selects[j[1]]['column']))

            join_clause += 'JOIN %s ON %s\n' % (selects[_from['select'][0]['name']]['table'], ' AND '.join(joins))

        # where
        filters = self.document.get('filters', '')
        if not filters:
            where_clause = ''
        else:
            where_clause = Query.process_filters(filters)

        if where_clause:
            where_clause = 'WHERE ' + where_clause + ' \n'

        # offset & limit
        offset_clause = ''
        offset = 0
        limit_clause = ''
        limit = None
        if 'offset' in self.document and self.document['offset']:
            offset = int(self.document['offset'])
            offset_clause = 'OFFSET %d\n' % offset

        if 'limit' in self.document and self.document['limit']:
            limit = int(self.document['limit'])
            limit_clause = 'LIMIT %d\n' % limit

        # organize into subquery
        subquery = 'SELECT * FROM (' + select_clause + from_clause + join_clause + ') AS SQ1\n'
        subquery_cnt = 'SELECT COUNT(*) FROM (' + select_clause + from_clause + join_clause + ') AS SQ1\n'

        # generate query
        q = subquery + \
            where_clause + \
            offset_clause + \
            limit_clause

        print q

        cursor = connection.cursor()
        if not only_headers:
            # execute query & return results
            t1 = time.time()

            # apply granularity
            try:
                granularity = int(self.document.get('granularity', 0))
            except ValueError:
                granularity = 0

            if granularity > 1:
                q = """
                    SELECT * FROM (
                        SELECT row_number() OVER () AS row_id, * FROM (%s) AS GQ
                    ) AS GQ_C
                    WHERE (row_id %% %d = 0)
                """ % (q, granularity)

            results = []
            if execute:
                cursor.execute(q)

                # we have to convert numeric results to float
                # by default they're returned as strings to prevent loss of precision

                for row in cursor.fetchall():
                    res_row = []
                    for idx, h_type in enumerate(header_sql_types):
                        pos = idx if not granularity > 1 else idx + 1
                        if (h_type == 'numeric' or h_type.startswith('numeric(')) and type(row[pos]) in [str, unicode]:
                            res_row.append(float(row[pos]))
                        else:
                            res_row.append(row[pos])

                    results.append(res_row)

            # count pages
            if limit is not None:
                pages = {
                    'current': (offset / limit) + 1,
                    'total': 1
                }
            else:
                pages = {
                    'current': 1,
                    'total': 1
                }

            if len(results) == limit:
                q_pages = subquery_cnt + \
                          where_clause

                cursor.execute(q_pages)
                self.count = cursor.fetchone()[0]
                pages['total'] = (self.count - 1) / limit + 1

        # include dimension values if requested
        for d_name in dimension_values:
            hdx, header = [hi for hi in enumerate(headers) if hi[1]['name'] == d_name][0]
            header['values'] = Dimension.objects.get(pk=selects[d_name]['column'].split('_')[-1]).values

        # include variable ranges if requested
        if variable:
            vdx, v = [vi for vi in enumerate(headers) if vi[1]['name'] == variable][0]
            v['distribution'] = Variable.objects.get(pk=selects[variable]['table'].split('_')[-1]).distribution

        if not only_headers:
            # monitor query duration
            q_time = (time.time() - t1) * 1000

        if not only_headers:
            response = {
                'results': results,
                'headers': {
                    'runtime_msec': q_time,
                    'pages': pages,
                }
            }
        else:
            response = {'headers': {}}
        response['headers']['columns'] = headers

        if raw_query:
            response['raw_query'] = q

        # store headers
        self.headers = ResultEncoder().encode(headers)
        if self.pk and commit:
            self.save()

        return response

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
        res = self.process(dimension_values='', variable='', only_headers=False, commit=False,
                           execute=False, raw_query=True)

        # restore initial doc
        self.document = doc

        return res['raw_query']
