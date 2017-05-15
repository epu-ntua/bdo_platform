import json

from django.http import JsonResponse

from aggregator.models import *


def execute_query(request):
    query_document = json.loads(request.POST.get('query'), '')

    # select
    selects = []
    for s in query_document['select']:
        if s['type']['id'] != 'VALUE':
            column_name = Dimension.objects.get(pk=s['type']['id']).data_column_name
        else:
            column_name = 'value'

        selects.append('%s AS %s' % (column_name, s['name']))

    select_clause = 'SELECT ' + ','.join(selects) + '\n'

    # from
    _from = Variable.objects.get(pk=query_document['from'][0]['type']['id']).data_table_name
    from_clause = 'FROM ' + _from + '\n'

    # where
    where_clause = ''

    # offset & limit
    offset_clause = 'OFFSET %d\n' % \
                    (int(query_document['offset']) if 'offset' in query_document and query_document['offset'] else 0)
    limit_clause = 'LIMIT %d\n' % \
                   (int(query_document['limit']) if 'limit' in query_document and query_document['limit'] else 100)

    # generate query
    query = select_clause + \
            from_clause + \
            where_clause + \
            offset_clause + \
            limit_clause

    # execute query & return results
    cursor = connection.cursor()
    cursor.execute(query)
    return JsonResponse({
        'results': cursor.fetchall()
    })
