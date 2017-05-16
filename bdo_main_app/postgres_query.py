import json

import time
from django.http import JsonResponse

from aggregator.models import *


def execute_query(request):
    query_document = json.loads(request.POST.get('query'), '')

    # select
    selects = []
    headers = []
    header_sql_types = []
    for s in query_document['from'][0]['select']:
        if s['type'] != 'VALUE':
            dimension = Dimension.objects.get(pk=s['type'])
            column_name = dimension.data_column_name
            column_unit = dimension.unit
            header_sql_types.append(dimension.sql_type)
        else:
            column_name = 'value'
            column_unit = 'VALUE'
            header_sql_types.append('double precision')

        selects.append('%s AS %s' % (column_name, s['name']))
        headers.append({
            'title': s['title'],
            'name': s['name'],
            'unit': column_unit,
        })
    select_clause = 'SELECT ' + ','.join(selects) + '\n'

    # from
    _from = Variable.objects.get(pk=query_document['from'][0]['type']).data_table_name
    from_clause = 'FROM ' + _from + '\n'

    # where
    where_clause = ''

    # offset & limit
    offset_clause = 'OFFSET %d\n' % \
                    (int(query_document['offset']) if 'offset' in query_document and query_document['offset'] else 0)
    limit_clause = 'LIMIT %d\n' % \
                   (int(query_document['limit']) if 'limit' in query_document and query_document['limit'] else 100)

    # generate query
    q = select_clause + \
            from_clause + \
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
            if h_type == 'numeric' or h_type.startswith('numeric('):
                res_row.append(float(row[idx]))
            else:
                res_row.append(row[idx])

        results.append(res_row)

    # monitor query duration
    q_time = (time.time() - t1) * 1000

    return JsonResponse({
        'results': results,
        'headers': {
            'runtime_msec': q_time,
            'total_results': None,
            'columns': headers,
        }
    })
