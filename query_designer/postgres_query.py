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

    # select
    selects = []
    headers = []
    header_sql_types = []
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

        selects.append('%s AS %s' % (column_name, s['name']))
        headers.append({
            'title': s['title'],
            'name': s['name'],
            'unit': column_unit,
            'axis': column_axis,
        })
    select_clause = 'SELECT ' + ','.join(selects) + '\n'

    # from
    _from = Variable.objects.get(pk=query_document['from'][0]['type']).data_table_name
    from_clause = 'FROM ' + _from + '\n'

    # where
    where_clause = ''

    # offset & limit
    offset = int(query_document['offset']) if 'offset' in query_document and query_document['offset'] else 0
    offset_clause = 'OFFSET %d\n' % offset
    limit = int(query_document['limit']) if 'limit' in query_document and query_document['limit'] else 100
    limit_clause = 'LIMIT %d\n' % limit

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
        q_pages = 'SELECT count(*) ' + \
            from_clause + \
            where_clause

        cursor.execute(q_pages)
        pages['total'] = (cursor.fetchone()[0] - 1) / 1000 + 1

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
