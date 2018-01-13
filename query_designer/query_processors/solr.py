from collections import OrderedDict

import time
from threading import Thread

import requests
from django.db import connection

from aggregator.models import Variable, Dimension
from .utils import GRANULARITY_MIN_PAGES, ResultEncoder


def query_string_from_params(params):
    return '?%s' % ('&'.join(['%s=%s' % (key, params[key]) for key in params.keys()]))


def process(self, dimension_values='', variable='', only_headers=False, commit=True, execute=False, raw_query=False):
    if dimension_values:
        dimension_values = dimension_values.split(',')
    else:
        dimension_values = []

    # all params
    request_params = {}

    # select
    selects = OrderedDict()
    headers = []
    header_sql_types = []

    columns = []
    groups = []
    v_names = []
    for _from in self.document['from']:
        v_obj = Variable.objects.get(pk=_from['type'])

        for s in _from['select']:
            obj = None
            if s['type'] != 'VALUE':
                dimension = Dimension.objects.get(pk=s['type'])
                obj = dimension
                column_name = dimension.name
                column_unit = dimension.unit
                column_axis = dimension.axis
                column_step = dimension.step
                sql_type = dimension.sql_type

            else:
                obj = v_obj
                column_name = v_obj.name
                v_names.append(column_name)
                column_unit = v_obj.unit
                column_axis = None
                column_step = None
                sql_type = 'double precision'

            selects[s['name']] = {'field': column_name, 'obj': obj}

            if 'joined' not in s:
                c_name = column_name
                if s.get('aggregate', '') != '':
                    c_name = '%s(%s)' % (s.get('aggregate'), column_name)

                if not s.get('exclude', False):
                    header_sql_types.append(sql_type)
                    headers.append({
                        'title': s['title'],
                        'name': s['name'],
                        'unit': column_unit,
                        'step': column_step,
                        'quote': '' if sql_type.startswith('numeric') or sql_type.startswith('double') else '"',
                        'isVariable': s['type'] == 'VALUE',
                        'axis': column_axis,
                    })

                    # add fields to select clause
                    columns.append((c_name, s['name']))

                # add fields to grouping
                if s.get('groupBy', False):
                    groups.append(c_name)

    # select
    select_clause = ','.join(['%s:%s' % (c[1], c[0]) for c in columns])
    request_params['fl'] = select_clause

    # where
    filters = self.document.get('filters', '')
    for v_name in v_names:
        filters = {
            'a': {'a': v_name, 'op': 'gt', 'b': '0'},
            'op': 'AND',
            'b': filters.copy() if filters else {'a': '*', 'op': 'EQ', 'b': '*'}
        }

    where_clause = self.process_filters(filters, mode='solr')
    for column_name, field_name in columns:
        where_clause = where_clause.replace(field_name, column_name)

    request_params['q'] = where_clause

    # grouping
    if groups:
        request_params['group'] = 'true'
        for group_field in groups:
            request_params['group.field'] = group_field

    # ordering
    orderings = self.document.get('orderings', [])
    if orderings:
        order_by_clause = ','.join([('%s %s' % (o['name'], o['type'])) for o in orderings])
        request_params['sort'] = order_by_clause

    # offset & limit
    offset = 0
    limit = None
    if 'offset' in self.document and self.document['offset']:
        offset = int(self.document['offset'])
        request_params['start'] = offset

    if 'limit' in self.document and self.document['limit']:
        limit = int(self.document['limit'])
        request_params['rows'] = offset

    print(query_string_from_params(request_params))

    if not only_headers:
        # execute query & return results
        t1 = time.time()

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

        if not execute:
            # only count
            request_params['rows'] = 0

        resp = requests.get('http://212.101.173.50:8983/solr/bdo/select%s' %
                            query_string_from_params(request_params)).json()
        self.count = resp['response']['numFound']

        if limit is not None:
            pages['total'] = (self.count - 1) / limit + 1

        results = []
        if execute:
            all_rows = resp['response']['docs']

            # we have to convert numeric results to float
            # by default they're returned as strings to prevent loss of precision
            for row in all_rows:
                res_row = []
                for _, field_alias in columns:
                    res_row.append(row[field_alias])

                results.append(res_row)

    # include dimension values if requested
    for d_name in dimension_values:
        hdx, header = [hi for hi in enumerate(headers) if hi[1]['name'] == d_name][0]
        d = selects[d_name]['obj']
        if not d.non_filterable:
            header['values'] = d.values

    # include variable ranges if requested
    if variable:
        vdx, v = [vi for vi in enumerate(headers) if vi[1]['name'] == variable][0]
        v['distribution'] = selects[variable]['obj'].distribution

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
        response['raw_query'] = query_string_from_params(request_params)

    # store headers
    self.headers = ResultEncoder(mode='solr').encode(headers)
    if self.pk and commit:
        self.save()

    return response
