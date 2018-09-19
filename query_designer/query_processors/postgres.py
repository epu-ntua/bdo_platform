from collections import OrderedDict
import psycopg2

import time
from threading import Thread

from django.db import connections, ProgrammingError

from aggregator.models import Variable, Dimension
from .utils import GRANULARITY_MIN_PAGES, ResultEncoder


def process(self, dimension_values='', variable='', only_headers=False, commit=True, execute=False, raw_query=False):
    if dimension_values:
        dimension_values = dimension_values.split(',')
    else:
        dimension_values = []

    # select
    selects = OrderedDict()
    headers = []
    header_sql_types = []

    columns = []
    groups = []
    for _from in self.document['from']:
        v_obj = Variable.objects.get(pk=_from['type'])

        for s in _from['select']:
            if s['type'] != 'VALUE':
                dimension = Dimension.objects.get(pk=s['type'])
                column_name = dimension.data_column_name
                column_unit = dimension.unit
                column_axis = dimension.axis
                column_step = dimension.step
                sql_type = dimension.sql_type

            else:
                if v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
                    column_name = v_obj.name
                else:
                    column_name = 'value'
                column_unit = v_obj.unit
                column_axis = None
                column_step = None
                sql_type = 'double precision'

            selects[s['name']] = {'column': column_name, 'table': v_obj.data_table_name}
            _from['name'] = v_obj.data_table_name

            # if 'joined' not in s:
            c_name = '%s.%s' % (_from['name'], selects[s['name']]['column'])
            if s.get('aggregate', '') != '':
                c_name = '%s(%s)' % (s.get('aggregate'), c_name)

            if not s.get('exclude', False):
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
                columns.append((c_name, '%s' % s['name']))

            # add fields to grouping
            if s.get('groupBy', False):
                groups.append(c_name)

    # select
    select_clause = 'SELECT ' + ','.join(['%s AS %s' % (c[0], c[1]) for c in columns]) + '\n'

    # from
    from_clause = 'FROM %s \n' % \
                  (selects[selects.keys()[0]]['table'])

    # join
    join_clause = ''
    all_joins_for_check = []
    for _from in self.document['from'][1:]:
        joins = []
        joins_for_check = []
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
                    joins_for_check.append( ( ( _from['type'], selects[j[0]]['column'] ), ( self.document['from'][0]['type'], selects[j[1]]['column'] ) ) )
                    if s.get('aggregate', '') != '':
                        c_name = '%s(%s)' % (s.get('aggregate'), c_name)
                        joins.append('%s(%s.%s)=%s(%s.%s)' %
                                     (s.get('aggregate'),
                                      _from['name'],
                                      selects[j[0]]['column'],
                                      s.get('aggregate'),
                                      self.document['from'][0]['name'],
                                      selects[j[1]]['column']))
                    else:
                        joins.append('%s.%s=%s.%s' %
                                     (_from['name'],
                                      selects[j[0]]['column'],
                                      self.document['from'][0]['name'],
                                      selects[j[1]]['column']))

        print "LOOK FOR JOIN"
        print selects
        print _from['name']
        if selects[_from['select'][0]['name']]['table'] != selects[self.document['from'][0]['select'][0]['name']]['table']:
            print "WE HAVE JOIN"
            join_clause += 'JOIN %s ON %s\n' % \
                           (selects[_from['select'][0]['name']]['table'],
                            ' AND '.join(joins))
        all_joins_for_check.append(joins_for_check)

    if not is_same_range_joins(all_joins_for_check):
        raise ValueError("Datasets have columns in common but actually nothing to join (ranges with nothing in common)")


    # where
    filters = self.document.get('filters', '')
    if not filters:
        where_clause = ''
    else:
        where_clause = self.process_filters(filters)

    if where_clause:
        where_clause = 'WHERE ' + where_clause + ' \n'

    # grouping
    group_clause = ''
    if groups:
        group_clause = 'GROUP BY %s\n' % ','.join(groups)

    # ordering
    order_by_clause = ''
    orderings = self.document.get('orderings', [])
    if orderings:
        order_by_clause = 'ORDER BY %s\n' % ','.join([(o['name'] + ' ' + o['type']) for o in orderings])

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
    subquery = 'SELECT * FROM (' + select_clause + from_clause + join_clause + where_clause + group_clause + order_by_clause + ') AS SQ1\n'
    subquery_cnt = 'SELECT COUNT(*) FROM (' + select_clause + from_clause + join_clause + where_clause + group_clause + ') AS SQ1\n'

    # generate query
    # q = subquery + \
    #     order_by_clause + \
    #     offset_clause + \
    #     limit_clause
    q = subquery + \
        offset_clause + \
        limit_clause
    subquery_cnt = 'SELECT COUNT(*) FROM (' + q + ') AS SQ1\n'

    import re
    print 'Initial Query:'
    print subquery
    if len(re.findall(r'round\d', subquery)) > 0:
        print 'Trying to fix round'
        # round_num = str(subquery.split('round')[1][0])
        round_num = str(re.findall(r'round\d', subquery)[0])[-1]
        print round_num
        # names = re.findall(r"round" + round_num + "\((.*?)\)", subquery)
        # print
        names = re.findall(r"round"+round_num+"\((.*?)\)", subquery)
        for name in names:
            subquery = re.sub(r"round"+round_num+"\((" + name + ")\)", "round(" + name + "::NUMERIC, " + round_num + ")::DOUBLE PRECISION", subquery)
        # print subquery

        names = re.findall(r"round" + round_num +"\((.*?)\)", subquery_cnt)
        for name in names:
            subquery_cnt = re.sub(r"round"+round_num+"\((" + name + ")\)", "round(" + name + "::NUMERIC, " + round_num + ")::DOUBLE PRECISION", subquery_cnt)
        # print subquery_cnt

        names = re.findall(r"round" + round_num +"\((.*?)\)", q)
        for name in names:
            q = re.sub(r"round"+round_num+"\((" + name + ")\)", "round(" + name + "::NUMERIC, " + round_num + ")::DOUBLE PRECISION", q)
        # print q


    if len(re.findall(r'date_trunc_(.*?)', subquery)) > 0:
        print 'Trying to fix date_trunc'
        time_trunc = str(subquery.split('date_trunc_')[1].split('(')[0])
        # print
        names = re.findall(r"date_trunc_" + time_trunc + "\((.*?)\)", subquery)
        for name in names:
            subquery = re.sub(r"date_trunc_"+time_trunc+"\((" + name + ")\)", "date_trunc('" + time_trunc + "', " + name + ")", subquery)
        # print subquery

        names = re.findall(r"date_trunc_" + time_trunc + "\((.*?)\)", subquery_cnt)
        for name in names:
            subquery_cnt = re.sub(r"date_trunc_"+time_trunc+"\((" + name + ")\)", "date_trunc('" + time_trunc + "', " + name + ")", subquery_cnt)
        # print subquery_cnt

        names = re.findall(r"date_trunc_" + time_trunc + "\((.*?)\)", q)
        for name in names:
            q = re.sub(r"date_trunc_"+time_trunc+"\((" + name + ")\)", "date_trunc('" + time_trunc + "', " + name + ")", q)
        # print q



    # cursor = connection.cursor()
    if v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
        cursor = connections['UBITECH_POSTGRES'].cursor()
    else:
        cursor = connections['default'].cursor()

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

        def _count():
            cursor.execute(subquery_cnt)
            self.count = cursor.fetchone()[0]

        self.count = None
        count_failed = False
        t = Thread(target=_count, args=[])
        t.start()
        t.join(timeout=5)

        if self.count is None:
            count_failed = True
            self.count = 10000000

        if limit is not None:
            pages['total'] = (self.count - 1) / limit + 1

        # apply granularity
        if self.count >= GRANULARITY_MIN_PAGES and (not count_failed):
            try:
                granularity = int(self.document.get('granularity', 0))
            except ValueError:
                granularity = 0

            if granularity > 1:
                q = """
                    SELECT %s FROM (
                        SELECT row_number() OVER () AS row_id, * FROM (%s) AS GQ
                    ) AS GQ_C
                    WHERE (row_id %% %d = 0)
                """ % (','.join([c[1] for c in columns]), q, granularity)
        print "Executed query:"
        print q
        results = []
        if execute:
            cursor.execute(q)
            all_rows = cursor.fetchall()
            print "First rows"
            print all_rows[:3]
            print header_sql_types
            # all_rows = Query.threaded_fetchall(connection, q, self.count)

            # we have to convert numeric results to float
            # by default they're returned as strings to prevent loss of precision
            # for row in all_rows:
            #     res_row = []
            #     for idx, h_type in enumerate(header_sql_types):
            #         if (h_type == 'numeric' or h_type.startswith('numeric(')) and type(row[idx]) in [str, unicode]:
            #         # if h_type == 'numeric' or h_type == 'double precision':
            #             res_row.append(float(row[idx]))
            #         else:
            #             res_row.append(row[idx])
            #
            #     results.append(res_row)
            results = all_rows
    # include dimension values if requested
    for d_name in dimension_values:
        hdx, header = [hi for hi in enumerate(headers) if hi[1]['name'] == d_name][0]
        d = Dimension.objects.get(pk=selects[d_name]['column'].split('_')[-1])
        if not d.non_filterable:
            header['values'] = d.values

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
    self.headers = ResultEncoder(mode='postgres').encode(headers)
    if self.pk and commit:
        self.save()

    return response


def is_same_range_joins(join_list):
    join_chain_list = create_join_chain_list_from_joins(join_list)
    min_max_list = calculate_range_for_every_join_chain(join_chain_list)
    return is_valid_range_all_chains(min_max_list)


def create_join_chain_list_from_joins(join_list):
    all_joins_list, chained_dimensions, join_chain_list, list_accessed_counter = init_variables(join_list)
    for join in all_joins_list:
        if not (chained_dimensions.__contains__(join[0]) and chained_dimensions.__contains__(join[1])):
            chain_list = update_chain_join_list(join)
            update_chained_dimensions(chained_dimensions, join)
            add_joins_to_chain_if_exist(all_joins_list, chain_list, chained_dimensions, list_accessed_counter)
            join_chain_list.append(chain_list)
            list_accessed_counter += 1
    return join_chain_list


def calculate_range_for_every_join_chain(join_chain_list):
    min_max_dim_chain_list = []
    for join_chain in join_chain_list:
        min_max_dim_list = []

        for dim in join_chain:
            min_dim, max_dim = get_min_max_dimension(dim)
            min_max_dim_list.append((min_dim, max_dim))

        min_max_dim_chain_list.append(min_max_dim_list)
    # print(min_max_dim_chain_list)
    return min_max_dim_chain_list


def is_valid_range_all_chains(min_max_chain_list):
    for chain in min_max_chain_list:
        if not is_valid_range_for_chain(chain):
            return False
    return True


def init_variables(join_list):
    join_chain_list = []
    chained_dimensions = []
    all_joins_list = extract_all_joins_from_join_list(join_list)
    list_accessed_counter = 0
    return all_joins_list, chained_dimensions, join_chain_list, list_accessed_counter


def update_chain_join_list(join):
    chain_list = [join[0], join[1]]
    return chain_list


def update_chained_dimensions(chained_dimensions, join):
    chained_dimensions.append(join[0])
    chained_dimensions.append(join[1])


def add_joins_to_chain_if_exist(all_joins_list, chain_list, chained_dimensions, list_accessed_counter):
    list_size = len(all_joins_list)
    for join2 in all_joins_list[list_accessed_counter:list_size]:
        add_join_if_valid(chain_list, chained_dimensions, join2)


def get_min_max_dimension(dim):
    cursor = connections['default'].cursor()
    min_max_dim_query = build_min_max_dimension_query(dim)
    try:
        cursor.execute(min_max_dim_query)
    except ProgrammingError as e:
        print "query execution failed due to: ", e
        return None
    res = cursor.fetchone()
    return res[0], res[1]


def build_min_max_dimension_query(dim):
    min_max_dim_query = """
                SELECT
                    min,
                    max
                FROM aggregator_dimension d 
                INNER JOIN aggregator_variable v 
                ON d.variable_id = v.id  
                WHERE d.title = '%s' AND variable_id = %s
            """ % (dim[1], dim[0])
    return min_max_dim_query


def is_valid_range_for_chain(chain):
    first_dim = next(iter(chain), None)
    max_of_mins = first_dim[0]
    min_of_maxes = first_dim[1]
    for dim in chain:
        if dim[0] > max_of_mins:
            max_of_mins = dim[0]
        if dim[1] < min_of_maxes:
            min_of_maxes = dim[1]
    if min_of_maxes < max_of_mins:
        return False
    return True


def add_join_if_valid(chain_list, chained_dimensions, join2):
    if join2[0] in chain_list and join2[1] not in chain_list:
        chain_list.append(join2[1])
        chained_dimensions.append(join2[1])
    elif join2[1] in chain_list and join2[0] not in chain_list:
        chain_list.append(join2[0])
        chained_dimensions.append(join2[0])


def extract_all_joins_from_join_list(join_list):
    all_joins_list = []
    for lists in join_list:
        all_joins_list += lists
    return all_joins_list
