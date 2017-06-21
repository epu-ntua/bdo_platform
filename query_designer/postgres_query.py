import json
import decimal
import datetime
import time
from collections import OrderedDict

from django.http import JsonResponse

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


def process_filters(filters):
    # end value
    if type(filters) in [str, unicode, int, float]:
        return filters

    return '(%s) %s (%s)' % \
           (process_filters(filters['a']), operator_to_str(filters['op']), process_filters(filters['b']))


def execute_query(request):
    # get POST params
    query_document = json.loads(request.POST.get('query'), '')
    dimension_values = request.POST.get('dimension_values', '')
    variable = request.POST.get('variable', '')
    only_headers = request.POST.get('only_headers', '').lower() == 'true'
    if dimension_values:
        dimension_values = dimension_values.split(',')
    else:
        dimension_values = []

    # select
    selects = OrderedDict()
    headers = []
    header_sql_types = []

    v_obj = Variable.objects.get(pk=query_document['from'][0]['type'])
    for s in query_document['from'][0]['select']:
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

        header_sql_types.append(sql_type)
        selects[s['name']] = {'column': column_name, 'table': v_obj.data_table_name}
        headers.append({
            'title': s['title'],
            'name': s['name'],
            'unit': column_unit,
            'step': column_step,
            'quote': '' if sql_type.startswith('numeric') or sql_type.startswith('double') else "'",
            'isVariable': s['type'] == 'VALUE',
            'axis': column_axis,
        })
    select_clause = 'SELECT ' + ','.join('%s AS %s' % (selects[name]['column'], name) for name in selects.keys()) + '\n'

    # from
    from_clause = 'FROM ' + selects[selects.keys()[0]]['table'] + '\n'

    # where
    filters = query_document.get('filters', '')
    if not filters:
        where_clause = ''
    else:
        where_clause = process_filters(filters)

    if where_clause:
        where_clause = 'WHERE ' + where_clause + ' \n'

    # offset & limit
    offset_clause = ''
    offset = 0
    limit_clause = ''
    limit = None
    if 'offset' in query_document and query_document['offset']:
        offset = int(query_document['offset'])
        offset_clause = 'OFFSET %d\n' % offset

    if 'limit' in query_document and query_document['limit']:
        limit = int(query_document['limit'])
        limit_clause = 'LIMIT %d\n' % limit

    # organize into subquery
    subquery = 'SELECT * FROM (' + select_clause + from_clause + ') AS SQ1\n'
    subquery_cnt = 'SELECT COUNT(*) FROM (' + select_clause + from_clause + ') AS SQ1\n'

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
        cursor.execute(q)

        # we have to convert numeric results to float
        # by default they're returned as strings to prevent loss of precision
        results = []
        for row in cursor.fetchall():
            res_row = []
            for idx, h_type in enumerate(header_sql_types):
                if (h_type == 'numeric' or h_type.startswith('numeric(')) and type(row[idx]) in [str, unicode]:
                    res_row.append(float(row[idx]))
                else:
                    res_row.append(row[idx])

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
            pages['total'] = (cursor.fetchone()[0] - 1) / 1000 + 1

    # include dimension values if requested
    for d_name in dimension_values:
        hdx, header = [hi for hi in enumerate(headers) if hi[1]['name'] == d_name][0]
        header['values'] = Dimension.objects.get(pk=selects[d_name]['column'].split('_')[-1]).values
        """
        q_col_values = 'SELECT DISTINCT(%s) FROM %s ORDER BY %s' % \
            (selects[d_name]['column'], selects[d_name]['table'], selects[d_name]['column'])

        print q_col_values
        td = time.time()
        cursor.execute(q_col_values)
        print '%s --> %d' % (d_name, int((time.time() - td) * 1000))
        header['values'] = []
        h_type = header_sql_types[hdx]
        for row in cursor.fetchall():
            v = row[0]
            if (h_type == 'numeric' or h_type.startswith('numeric(')) and type(v) in [str, unicode]:
                header['values'].append(float(v))
            else:
                header['values'].append(v)
        """

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

    return JsonResponse(response, encoder=ResultEncoder)
