import json
import decimal
import datetime
import time
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


def execute_query(request):
    query_document = json.loads(request.POST.get('query'), '')
    dimension_values = request.POST.get('dimension_values', '')
    if dimension_values:
        dimension_values = dimension_values.split(',')
    else:
        dimension_values = []

    # select
    selects = {}
    headers = []
    header_sql_types = []

    variable = Variable.objects.get(pk=query_document['from'][0]['type'])
    for s in query_document['from'][0]['select']:
        if s['type'] != 'VALUE':
            dimension = Dimension.objects.get(pk=s['type'])
            column_name = dimension.data_column_name
            column_unit = dimension.unit
            column_axis = dimension.axis
            header_sql_types.append(dimension.sql_type)
        else:
            column_name = 'value'
            column_unit = 'VALUE'
            column_axis = None
            header_sql_types.append('double precision')

        selects[s['name']] = {'column': column_name, 'table': variable.data_table_name}
        headers.append({
            'title': s['title'],
            'name': s['name'],
            'unit': column_unit,
            'axis': column_axis,
        })
    select_clause = 'SELECT ' + ','.join('%s AS %s' % (selects[name]['column'], name) for name in selects.keys()) + '\n'

    # from
    from_clause = 'FROM ' + selects[selects.keys()[0]]['table'] + '\n'

    # where
    where_clause = ' AND '.join(['(%s)' % f for f in query_document['filters']]) \
        .replace(' && ', ' AND ') \
        .replace(' || ', ' OR ') \
        .replace('!', ' NOT ')

    if where_clause:
        where_clause = 'WHERE ' + where_clause + '\n'

    # offset & limit
    offset = int(query_document['offset']) if 'offset' in query_document and query_document['offset'] else 0
    offset_clause = 'OFFSET %d\n' % offset
    limit = int(query_document['limit']) if 'limit' in query_document and query_document['limit'] else 100
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

    # execute query & return results
    t1 = time.time()
    cursor = connection.cursor()
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
    pages = {
        'current': (offset / limit) + 1,
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
        q_col_values = 'SELECT DISTINCT(%s) FROM %s ORDER BY %s' % \
            (selects[d_name]['column'], selects[d_name]['table'], selects[d_name]['column'])

        cursor.execute(q_col_values)
        header['values'] = []
        h_type = header_sql_types[hdx]
        for row in cursor.fetchall():
            v = row[0]
            if (h_type == 'numeric' or h_type.startswith('numeric(')) and type(v) in [str, unicode]:
                header['values'].append(float(v))
            else:
                header['values'].append(v)

    # monitor query duration
    q_time = (time.time() - t1) * 1000

    return JsonResponse({
        'results': results,
        'headers': {
            'runtime_msec': q_time,
            'columns': headers,
            'pages': pages,
        }
    }, encoder=ResultEncoder)
