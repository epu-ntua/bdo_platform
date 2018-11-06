import re
from collections import OrderedDict
from query_designer import models
from query_designer.models import Query

import time
from threading import Thread

import sys
from django.db import connections, ProgrammingError

from aggregator.models import Variable, Dimension
from .utils import GRANULARITY_MIN_PAGES, ResultEncoder


def process(self, dimension_values='', variable='', only_headers=False, commit=True, execute=False, raw_query=False):
    dimension_values = preprocess_dimension_values(dimension_values)
    selects = OrderedDict()
    headers = []
    header_sql_types = []
    columns = []
    groups = []
    prejoin_groups = []

    c_name, v_obj, data_table_names= preprocess_document(columns, groups, prejoin_groups,
                                                        header_sql_types, headers, selects, self)
    prejoin_name = None
    if len(self.document['from']) > 1:
        prejoin_name = extract_prejoin_name(self.document['from'])

    if is_query_for_average(self.document['from']) and prejoin_name is not None:
        limit, offset, query, subquery_cnt = build_prejoin_query(prejoin_name, data_table_names, columns, prejoin_groups, self)
    else:
        limit, offset, query, subquery_cnt = build_query(c_name, columns, groups, selects, self)

    cursor = choose_db_cursor(v_obj)

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
                query = """
                    SELECT %s FROM (
                        SELECT row_number() OVER () AS row_id, * FROM (%s) AS GQ
                    ) AS GQ_C
                    WHERE (row_id %% %d = 0)
                """ % (','.join([c[1] for c in columns]), query, granularity)
        print "Executed query:"
        print query
        results = []
        if execute:
            cursor.execute(query)
            all_rows = cursor.fetchall()
            print "First rows"
            print all_rows[:3]
            print header_sql_types

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
        response['raw_query'] = query

    # store headers
    self.headers = ResultEncoder(mode='postgres').encode(headers)
    if self.pk and commit:
        self.save()

    return response


def preprocess_dimension_values(dimension_values):
    if dimension_values:
        dimension_values = dimension_values.split(',')
    else:
        dimension_values = []
    return dimension_values


def preprocess_document(columns, groups, prejoin_groups, header_sql_types, headers, selects, self):
    data_table_names = []
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
                columns.append( (c_name, '%s' % s['name'], '%s' % s['title'], s.get('aggregate')) )

            # add fields to grouping
            if s.get('groupBy', False):
                groups.append(c_name)
                prejoin_groups.append('%s(%s)' % (s.get('aggregate'), selects[s['name']]['column']))
        data_table_names.append(v_obj.data_table_name)
    return c_name, v_obj, data_table_names


def is_query_for_average(from_list):
    for _from in from_list:
        for s in _from['select']:
            if 'type' in s and s['type'] == 'VALUE' and s['aggregate'] != 'AVG':
                return False
    return True


def extract_prejoin_name(from_list):
    variable_id1, variable_id2 = extract_variable_ids_from_doc(from_list)
    dataset_id1 = extract_dataset_id_from_varible_ids(variable_id1)
    dataset_id2 = extract_dataset_id_from_varible_ids(variable_id2)
    return extract_prejoin_name_for_datasets(dataset_id1, dataset_id2)


def build_prejoin_query(prejoin_name, data_table_names, columns, prejoin_groups, self):
    select_clause = build_prejoin_select_clause(columns)
    from_clause = 'FROM ' + prejoin_name + '\n'
    where_clause = build_prejoin_where_clause(self, prejoin_name)
    group_clause = build_group_by_clause(prejoin_groups)
    order_by_clause = build_order_by_clause(self)
    offset, offset_clause = build_offset_clause(self)
    limit, limit_clause = build_limit_clause(self)

    subquery = 'SELECT * FROM (' + select_clause + from_clause + where_clause + group_clause + order_by_clause + ') AS SQ1\n'
    q = subquery + offset_clause + limit_clause
    subquery_cnt = 'SELECT COUNT(*) FROM (' + q + ') AS SQ1\n'
    print 'Initial Query:'
    print subquery
    q, subquery, subquery_cnt = fix_round(q, subquery, subquery_cnt)
    q = fix_date_trunc(q, subquery, subquery_cnt)
    return limit, offset, q, subquery_cnt


def build_query(c_name, columns, groups, selects, self):
    select_clause = build_select_clause(columns)
    from_clause = build_from_clause(selects)
    all_joins_for_check, join_clause = build_join_clause(c_name, selects, self)
    if not is_same_range_joins(all_joins_for_check):
        raise ValueError("Datasets have columns in common but actually nothing to join (ranges with nothing in common)")
    where_clause = build_where_clause(self)
    group_clause = build_group_by_clause(groups)
    order_by_clause = build_order_by_clause(self)
    offset, offset_clause = build_offset_clause(self)
    limit, limit_clause = build_limit_clause(self)
    # organize into subquery
    subquery = 'SELECT * FROM (' + select_clause + from_clause + join_clause + where_clause + group_clause + order_by_clause + ') AS SQ1\n'
    q = subquery + offset_clause + limit_clause
    subquery_cnt = 'SELECT COUNT(*) FROM (' + q + ') AS SQ1\n'
    print 'Initial Query:'
    print subquery
    q, subquery, subquery_cnt = fix_round(q, subquery, subquery_cnt)
    q = fix_date_trunc(q, subquery, subquery_cnt)
    return limit, offset, q, subquery_cnt


def choose_db_cursor(v_obj):
    if v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
        cursor = connections['UBITECH_POSTGRES'].cursor()
    else:
        cursor = connections['default'].cursor()
    return cursor


def extract_prejoin_name_for_datasets(dataset_id1, dataset_id2):
    query = """SELECT view_name 
              FROM aggregator_joinofdatasets 
              WHERE (dataset_first_id =%s AND dataset_second_id = %s) OR 
                  (dataset_first_id = %s AND dataset_second_id = %s) """ \
            % (dataset_id1, dataset_id2, dataset_id2, dataset_id1)
    cursor = connections['default'].cursor()
    try:
        cursor.execute(query)
    except ProgrammingError as e:
        print "query execution failed due to: ", e
        return None
    res = cursor.fetchone()
    if res is not None:
        return res[0]
    return None


def build_select_clause(columns):
    select_clause = 'SELECT ' + ','.join(['%s AS %s' % (c[0], c[1]) for c in columns]) + '\n'
    return select_clause


def build_prejoin_select_clause(columns):
    select_clause = 'SELECT ' + ','.join(['%s(%s) AS %s' % (c[3], c[2], c[1]) for c in columns]) + '\n'
    return select_clause


def build_from_clause(selects):
    from_clause = 'FROM %s \n' % \
                  (selects[selects.keys()[0]]['table'])
    return from_clause


def build_join_clause(c_name, selects, self):
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
                    joins_for_check.append(((_from['type'], selects[j[0]]['column']),
                                            (self.document['from'][0]['type'], selects[j[1]]['column'])))
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
        if selects[_from['select'][0]['name']]['table'] != \
                selects[self.document['from'][0]['select'][0]['name']]['table']:
            print "WE HAVE JOIN"
            join_clause += 'JOIN %s ON %s\n' % \
                           (selects[_from['select'][0]['name']]['table'],
                            ' AND '.join(joins))
            if join_clause.replace(" ","").replace("\n","").replace(",", "").endswith("ON"):
                raise ValueError("No common columns for all the datasets. They cannot be combined.")

        all_joins_for_check.append(joins_for_check)
    print "Joins to check"
    print all_joins_for_check
    if not is_same_range_joins(all_joins_for_check):
        print "Datasets have columns in common but actually nothing to join (ranges with nothing in common)"
        raise ValueError("Datasets do not match both in space and time. They cannot be combined.")
    print "Query Continues"

    # where
    return all_joins_for_check, join_clause


def build_where_clause(self):
    filters = self.document.get('filters', '')
    if not filters:
        where_clause = ''
    else:
        where_clause = self.process_filters(filters)

    if where_clause:
        where_clause = 'WHERE ' + where_clause + ' \n'
    return where_clause


def process_prejoin_filters(filters_json, self, view_name):
    if type(filters_json) in [int, float]:
        try:
            filters = process_prejoin_leaf_filters(filters_json, self, view_name)
        except:
            return filters_json
        return filters
    if type(filters_json) in [str, unicode]:
        try:
            filters = process_prejoin_leaf_filters(filters_json, self, view_name)
        except:
            return filters_json
        return "%s" % filters
    _a = process_prejoin_filters(filters_json['a'], self, view_name)
    _b = process_prejoin_filters(filters_json['b'], self, view_name)
    result = '%s %s %s' % \
             (('(%s)' % _a) if type(_a) not in [str, unicode, int, float] else _a,
              Query.operator_to_str(filters_json['op']),
              ('(%s)' % _b) if type(_b) not in [str, unicode, int, float] else _b)
    return result


def process_prejoin_leaf_filters(filters, self, view_name):
    col_name = ''
    from_order = int(filters[filters.find('i') + 1:filters.find('_')])
    if from_order >= 0:
        for x in self.document['from'][from_order]['select']:
            if x['name'] == filters:
                if x['type'] != 'VALUE':
                    col_name = Dimension.objects.get(pk=x['type']).data_column_name
                else:
                    v_obj = Variable.objects.get(pk=int(self.document['from'][from_order]['type']))
                    if v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
                        col_name = v_obj.name
                    else:
                        col_name = 'value'
        filters = view_name + '.' + col_name
    return filters


def build_prejoin_where_clause(self, view_name):
    filters = self.document.get('filters', '')
    if not filters:
        where_clause = ''
    else:
        where_clause = process_prejoin_filters(filters, self, view_name)

    if where_clause:
        where_clause = 'WHERE ' + where_clause + ' \n'
    return where_clause


def build_group_by_clause(groups):
    group_clause = ''
    if groups:
        group_clause = 'GROUP BY %s\n' % ','.join(groups)
    return group_clause


def build_order_by_clause(self):
    order_by_clause = ''
    orderings = self.document.get('orderings', [])
    if orderings:
        order_by_clause = 'ORDER BY %s\n' % ','.join([(o['name'] + ' ' + o['type']) for o in orderings])
    return order_by_clause


def build_limit_clause(self):
    limit_clause = ''
    limit = None
    if 'limit' in self.document and self.document['limit']:
        limit = int(self.document['limit'])
        limit_clause = 'LIMIT %d\n' % limit
    return limit, limit_clause


def build_offset_clause(self):
    offset_clause = ''
    offset = 0
    if 'offset' in self.document and self.document['offset']:
        offset = int(self.document['offset'])
        offset_clause = 'OFFSET %d\n' % offset
    return offset, offset_clause


def fix_date_trunc(q, subquery, subquery_cnt):
    if len(re.findall(r'date_trunc_(.*?)', subquery)) > 0:
        print 'Trying to fix date_trunc'
        time_trunc = str(subquery.split('date_trunc_')[1].split('(')[0])
        # print
        names = re.findall(r"date_trunc_" + time_trunc + "\((.*?)\)", subquery)
        for name in names:
            subquery = re.sub(r"date_trunc_" + time_trunc + "\((" + name + ")\)",
                              "date_trunc('" + time_trunc + "', " + name + ")", subquery)
        # print subquery

        names = re.findall(r"date_trunc_" + time_trunc + "\((.*?)\)", subquery_cnt)
        for name in names:
            subquery_cnt = re.sub(r"date_trunc_" + time_trunc + "\((" + name + ")\)",
                                  "date_trunc('" + time_trunc + "', " + name + ")", subquery_cnt)
        # print subquery_cnt

        names = re.findall(r"date_trunc_" + time_trunc + "\((.*?)\)", q)
        for name in names:
            q = re.sub(r"date_trunc_" + time_trunc + "\((" + name + ")\)",
                       "date_trunc('" + time_trunc + "', " + name + ")", q)
        # print q
    return q


def fix_round(q, subquery, subquery_cnt):
    if len(re.findall(r'round\d', subquery)) > 0:
        print 'Trying to fix round'
        # round_num = str(subquery.split('round')[1][0])
        round_num = str(re.findall(r'round\d', subquery)[0])[-1]
        print round_num
        # names = re.findall(r"round" + round_num + "\((.*?)\)", subquery)
        # print
        names = re.findall(r"round" + round_num + "\((.*?)\)", subquery)
        for name in names:
            subquery = re.sub(r"round" + round_num + "\((" + name + ")\)",
                              "round(" + name + "::NUMERIC, " + round_num + ")::DOUBLE PRECISION", subquery)
        # print subquery

        names = re.findall(r"round" + round_num + "\((.*?)\)", subquery_cnt)
        for name in names:
            subquery_cnt = re.sub(r"round" + round_num + "\((" + name + ")\)",
                                  "round(" + name + "::NUMERIC, " + round_num + ")::DOUBLE PRECISION", subquery_cnt)
        # print subquery_cnt

        names = re.findall(r"round" + round_num + "\((.*?)\)", q)
        for name in names:
            q = re.sub(r"round" + round_num + "\((" + name + ")\)",
                       "round(" + name + "::NUMERIC, " + round_num + ")::DOUBLE PRECISION", q)
        # print q
    return q, subquery, subquery_cnt


def extract_variable_ids_from_doc(from_list):
    variable_list = []
    for _from in from_list:
        variable_list.append(_from['type'])

    return variable_list[0], variable_list[1]


def extract_dataset_id_from_varible_ids(variable_id):
    query = """SELECT dataset_id 
              FROM aggregator_variable 
              WHERE id =%s """ % variable_id
    cursor = connections['default'].cursor()
    try:
        cursor.execute(query)
    except ProgrammingError as e:
        print "query execution failed due to: ", e
        return None
    res = cursor.fetchone()
    return res[0]


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
    if res is not None:
        return res[0], res[1]
    else:
        return (-1*sys.maxint), sys.maxint


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
    max_of_mins, min_of_maxes = initialize_minofmaxes_and_maxofmins(chain)
    if min_of_maxes is None or max_of_mins is None:
        return True

    for dim in chain:
        if dim[0] is not None and dim[0] > max_of_mins:
            max_of_mins = dim[0]
        if dim[1] is not None and dim[1] < min_of_maxes:
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


def initialize_minofmaxes_and_maxofmins(chain):
    first_dim = next(iter(chain), None)
    max_of_mins = first_dim[0]
    min_of_maxes = first_dim[1]

    while min_of_maxes is None or max_of_mins is None:
        first_dim = next(iter(chain), None)
        max_of_mins = first_dim[0]
        min_of_maxes = first_dim[1]

    return max_of_mins, min_of_maxes
