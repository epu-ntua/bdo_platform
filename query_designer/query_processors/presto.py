import re
from collections import OrderedDict

import prestodb

from query_designer.models import Query

import time
from threading import Thread

import sys
from django.db import connections, ProgrammingError
from django.conf import settings

from aggregator.models import Variable, Dimension
from .utils import GRANULARITY_MIN_PAGES, ResultEncoder


def process(self, dimension_values='', variable='', only_headers=False, commit=True, execute=False, raw_query=False, from_visualizer=False):
    dimension_values = preprocess_dimension_values(dimension_values)
    selects = OrderedDict()
    headers = []
    header_sql_types = []
    columns = []
    groups = []
    prejoin_groups = []

    c_name, v_obj, data_table_names, groups = preprocess_document(columns, groups, prejoin_groups,
                                                          header_sql_types, headers, selects, self)
    # import pdb
    # pdb.set_trace()
    prejoin_name = None
    if len(self.document['from']) > 1:
        prejoin_name = extract_prejoin_name(self.document['from'])

    if is_query_with_aggregate(self.document['from']) and prejoin_name is not None:
        limit, query, subquery_cnt = build_prejoin_query(prejoin_name, columns,
                                                                 prejoin_groups, self)
    else:
        limit, query, subquery_cnt = build_query(c_name, columns, groups, selects, self)

    # if for map visualisation, do not perform round on select, but choose min
    print 'trying to remove round'
    if from_visualizer:
        query = remove_round_from_select(query)
    print 'removed round'
    cursor = choose_db_cursor(v_obj)

    if not only_headers:
        # execute query & return results
        t1 = time.time()


        pages = {
            'current': 1,
            'total': 1
        }

        def _count():
            pass
            # cursor.execute(subquery_cnt)
            # self.count = cursor.fetchone()[0]

        self.count = None
        count_failed = False
        # t = Thread(target=_count, args=[])
        # t.start()
        # t.join(timeout=5)

        # if self.count is None:
        #     count_failed = True
        #     self.count = 10000000
        #
        # if limit is not None:
        #     pages['total'] = (self.count - 1) / limit + 1

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
            try:
                all_rows = cursor.fetchall()
            except Exception, e:
                if e.message.find('exceeded') >= 0:
                    print 'MAX MEMORY EXCEEDED'
                    raise Exception('max_memory_exceeded')
                else:
                    print e.message
                    print 'other error'
                    raise Exception('error')
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
                # 'pages': pages,
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
                human_column_name = Dimension.objects.get(pk=s['type']).title
                print human_column_name
                dimension = Dimension.objects.get(pk=s['type'])
                column_name = dimension.data_column_name
                column_unit = dimension.unit
                column_axis = dimension.axis
                column_step = dimension.step
                sql_type = dimension.sql_type
            else:
                human_column_name = Variable.objects.get(pk=_from['type']).title
                print human_column_name
                if v_obj.dataset.stored_at == 'UBITECH_PRESTO':
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
                c_name_with_agg = '%s(%s)' % (s.get('aggregate'), c_name)
                if str(s.get('aggregate')).startswith('date_trunc'):
                    human_column_name_with_agg = '%s(%s)' % (str(s.get('aggregate')).split('date_trunc_')[1], human_column_name)
                elif str(s.get('aggregate')).startswith('round0'):
                    human_column_name_with_agg = '%s\n(%s)' % (human_column_name, 'resolution 1 deg')
                elif str(s.get('aggregate')).startswith('round1'):
                    human_column_name_with_agg = '%s\n(%s)' % (human_column_name, 'resolution 0.1 deg')
                elif str(s.get('aggregate')).startswith('round2'):
                    human_column_name_with_agg = '%s\n(%s)' % (human_column_name, 'resolution 0.01 deg')
                else:
                    human_column_name_with_agg = '%s(%s)' % (str(s.get('aggregate')), human_column_name)
            else:
                c_name_with_agg = c_name
                human_column_name_with_agg = human_column_name

            if not s.get('exclude', False):
                header_sql_types.append(sql_type)
                headers.append({
                    'title': human_column_name_with_agg.lower().title(),
                    'name': s['name'],
                    'unit': column_unit,
                    'step': column_step,
                    'quote': '' if sql_type.startswith('numeric') or sql_type.startswith('double') else "'",
                    'isVariable': s['type'] == 'VALUE',
                    'axis': column_axis,
                })

                # add fields to select clause
                columns.append((c_name_with_agg, '%s' % s['name'], '%s' % s['title'], s.get('aggregate')))

            # add fields to grouping
            if s.get('groupBy', False):
                if str(s.get('aggregate', '')).startswith('round') or str(s.get('aggregate', '')).startswith('date'):
                    groups.append(c_name_with_agg)
                    prejoin_groups.append('%s(%s)' % (s.get('aggregate'), selects[s['name']]['column']))
                else:
                    groups.append(c_name)
                    prejoin_groups.append('%s' % (selects[s['name']]['column']))
        data_table_names.append(v_obj.data_table_name)
        groups = list(set(groups))
    return c_name_with_agg, v_obj, data_table_names, groups


def is_query_with_aggregate(from_list):
    for _from in from_list:
        for s in _from['select']:
            if 'type' in s and s['type'] == 'VALUE' and s['aggregate'] == '':
                return False
    return True


def remove_round_from_select(q):
    select_clause = q.split('(SELECT')[1].split('FROM')[0].replace('round(', 'MIN(').replace(', 0', '').replace(', 1', '').replace(', 2', '')
    return q.split('(SELECT')[0] + '(SELECT' + select_clause + 'FROM' + q.split('(SELECT')[1].split('FROM')[1]


def extract_prejoin_name(from_list):
    dataset_list = []
    for f in from_list:
        dataset_list.append(Variable.objects.get(pk=int(f['type'])).dataset.id)
    dataset_list = list(set(dataset_list))
    if len(dataset_list) > 1:
        return extract_prejoin_name_for_datasets(dataset_list[0], dataset_list[1])
    else:
        return None


def build_prejoin_query(prejoin_name, columns, prejoin_groups, self):
    select_clause = build_prejoin_select_clause(columns)
    from_clause = 'FROM ' + prejoin_name + '\n'
    where_clause = build_prejoin_where_clause(self, prejoin_name)
    group_clause = build_group_by_clause(prejoin_groups)
    order_by_clause = build_order_by_clause(self)
    limit, limit_clause = build_limit_clause(self)

    subquery = 'SELECT * FROM (' + select_clause + from_clause + where_clause + group_clause + order_by_clause + ') AS SQ1\n'
    q = subquery + limit_clause
    subquery_cnt = 'SELECT COUNT(*) FROM (' + q + ') AS SQ1\n'
    print 'Initial Query:'
    print subquery
    q, subquery, subquery_cnt = fix_round(q, subquery, subquery_cnt)
    q = fix_date_trunc(q, subquery, subquery_cnt)
    return limit, q, subquery_cnt


def build_query(c_name, columns, groups, selects, self):
    select_clause = build_select_clause(columns)
    from_clause = build_from_clause(selects)
    all_joins_for_check, join_clause, needs_join_reorder = build_join_clause(c_name, selects, self)
    if not is_same_range_joins(all_joins_for_check):
        raise ValueError("Datasets have columns in common but actually nothing to join (ranges with nothing in common)")
    where_clause = build_where_clause(self)
    group_clause = build_group_by_clause(groups)
    order_by_clause = build_order_by_clause(self)
    limit, limit_clause = build_limit_clause(self)

    if needs_join_reorder:
        table1 = from_clause.split('FROM ')[1].strip()
        table2 = join_clause.split('JOIN ')[1].split('ON')[0].strip()
        from_clause = from_clause.replace(table1, table2)
        join_clause = join_clause.split('ON')[0].replace(table2, table1) + ' ON ' + join_clause.split('ON')[1]

    # organize into subquery
    subquery = 'SELECT * FROM (' + select_clause + from_clause + join_clause + where_clause + group_clause + order_by_clause + ') AS SQ1\n'
    q = subquery + limit_clause
    subquery_cnt = 'SELECT COUNT(*) FROM (' + q + ') AS SQ1\n'
    print 'Initial Query:'
    print subquery
    q, subquery, subquery_cnt = fix_round(q, subquery, subquery_cnt)
    q = fix_date_trunc(q, subquery, subquery_cnt)
    return limit, q, subquery_cnt


def choose_db_cursor(v_obj):
    if v_obj.dataset.stored_at == 'UBITECH_PRESTO':
        presto_credentials = settings.DATABASES['UBITECH_PRESTO']
        conn = prestodb.dbapi.connect(
            host=presto_credentials['HOST'],
            port=presto_credentials['PORT'],
            user=presto_credentials['USER'],
            catalog=presto_credentials['CATALOG'],
            schema=presto_credentials['SCHEMA'],
        )
        cursor = conn.cursor()
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


def translate_percentiles_if_needed(select_clause):
    if not 'PERCENTILE_CONT' in select_clause:
        return select_clause
    else:
        return translate_percentiles(select_clause)


def translate_percentiles(select_clause):
    select_table = select_clause.split('(')
    func = select_table[0]
    params = select_table[1]
    percentage = int(func.split('_')[2])
    percentage_float = percentage / 100.0
    func = 'APPROX_PERCENTILE'
    params_table = params.split(')')
    return func + '(' + params_table[0] + ', ' + str(percentage_float) + ')'


def build_select_clause(columns):
    select_clause = 'SELECT ' + ','.join(['%s AS %s' %
                                          (translate_percentiles_if_needed(c[0]), c[1]) for c in columns]) + '\n'
    return select_clause


def build_prejoin_select_clause(columns):
    import re
    select_clause = 'SELECT ' + ','.join(['%s AS %s' % (re.sub("[(].*[.]", "(", c[0]), c[1]) for c in columns]) + '\n'
    return select_clause


def build_from_clause(selects):
    from_clause = 'FROM %s \n' % \
                  (selects[selects.keys()[0]]['table'])
    return from_clause


def build_join_clause(c_name, selects, self):
    join_clause = ''
    all_joins_for_check = []
    tables_in_query = set()
    tables_in_query.add(selects[self.document['from'][0]['select'][0]['name']]['table'])
    join_from_index = -1
    needs_join_reorder = False
    for idx, _from in enumerate(self.document['from'][1:], 1):
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
        print tables_in_query
        if selects[_from['select'][0]['name']]['table'] not in tables_in_query:
            tables_in_query.add(selects[_from['select'][0]['name']]['table'])
            print "WE HAVE JOIN"
            join_from_index = idx
            join_clause += 'JOIN %s ON %s\n' % \
                           (selects[_from['select'][0]['name']]['table'],
                            ' AND '.join(joins))
            if join_clause.replace(" ", "").replace("\n", "").replace(",", "").endswith("ON"):
                raise ValueError("No common columns for all the datasets. They cannot be combined.")

        all_joins_for_check.append(joins_for_check)

    if join_clause != '':
        print 'join_clause is not empty'
        dataset1 = Variable.objects.get(pk=int(self.document['from'][0]['type'])).dataset
        dataset2 = Variable.objects.get(pk=int(self.document['from'][join_from_index]['type'])).dataset
        print long(dataset1.number_of_rows) , long(dataset2.number_of_rows)
        if long(dataset2.number_of_rows) > long(dataset1.number_of_rows):
            print 'needs reorder'
            needs_join_reorder = True

    print "Joins to check"
    print all_joins_for_check
    if not is_same_range_joins(all_joins_for_check):
        print "Datasets have columns in common but actually nothing to join (ranges with nothing in common)"
        raise ValueError("Datasets do not match both in space and time. They cannot be combined.")
    print "Query Continues"

    # where
    return all_joins_for_check, join_clause, needs_join_reorder


def build_where_clause(self):
    filters = self.document.get('filters', '')
    if not filters:
        where_clause = ''
    else:
        where_clause = self.process_filters(filters, 'presto', use_table_names=True)

    extra_filters = ''
    for f in self.document['from']:
        table_name = Variable.objects.get(pk=int(f['type'])).dataset.table_name
        col_name = Variable.objects.get(pk=int(f['type'])).name
        if extra_filters == '':
            extra_filters += table_name + '.' + col_name + ' is not NULL'
        else:
            extra_filters += ' OR ' + table_name + '.' + col_name + ' is not NULL'

    if where_clause:
        where_clause = 'WHERE ' + where_clause + ' AND (' + extra_filters + ') \n'
    else:
        where_clause = 'WHERE ' + extra_filters + ' \n'
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
                    if v_obj.dataset.stored_at == 'UBITECH_PRESTO':
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
        where_clause = self.process_filters(filters, mode='presto', use_table_names = False)

    extra_filters = ''
    for f in self.document['from']:
        table_name = Variable.objects.get(pk=int(f['type'])).dataset.table_name
        col_name = Variable.objects.get(pk=int(f['type'])).name
        if extra_filters == '':
            extra_filters += col_name + ' is not NULL'
        else:
            extra_filters += ' OR ' + col_name + ' is not NULL'

    if where_clause:
        where_clause = 'WHERE ' + where_clause + ' AND (' + extra_filters + ') \n'
    else:
        where_clause = 'WHERE ' + extra_filters + ' \n'

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
    print 'looking for COUNTdistinctdate_trunc'

    if str(q).find('COUNTdistinctdate_trunc') > -1:
        q = q.split('COUNTdistinctdate_trunc')[0] + 'COUNT(DISTINCT date_trunc' + q.split('COUNTdistinctdate_trunc')[1].split(')', 1)[0] + '))' + q.split('COUNTdistinctdate_trunc')[1].split(')', 1)[1]
    print 'done COUNTdistinctdate_trunc'
    return q


def fix_round(q, subquery, subquery_cnt):
    if len(re.findall(r'round\d', subquery)) > 0:
        print 'Trying to fix round'
        # round_num = str(subquery.split('round')[1][0])
        for occurance in set(re.findall(r'round\d', subquery)):
            round_num = str(occurance)[-1]
            print round_num
            # names = re.findall(r"round" + round_num + "\((.*?)\)", subquery)
            # print
            names = re.findall(r"round" + round_num + "\((.*?)\)", subquery)
            for name in names:
                subquery = re.sub(r"round" + round_num + "\((" + name + ")\)",
                                  "round(" + name + ", " + round_num + ")", subquery)
            # print subquery

            names = re.findall(r"round" + round_num + "\((.*?)\)", subquery_cnt)
            for name in names:
                subquery_cnt = re.sub(r"round" + round_num + "\((" + name + ")\)",
                                      "round(" + name + ", " + round_num + ")", subquery_cnt)
            # print subquery_cnt

            names = re.findall(r"round" + round_num + "\((.*?)\)", q)
            for name in names:
                q = re.sub(r"round" + round_num + "\((" + name + ")\)",
                           "round(" + name + ", " + round_num + ")", q)
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
    print 'join_chain_list'
    print join_chain_list
    min_max_list = calculate_range_for_every_join_chain(join_chain_list)
    print 'min_max_list'
    print min_max_list
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
    # cursor = connections['default'].cursor()
    # min_max_dim_query = build_min_max_dimension_query(dim)
    # try:
    #     cursor.execute(min_max_dim_query)
    # except ProgrammingError as e:
    #     print "query execution failed due to: ", e
    #     return None
    # res = cursor.fetchone()
    res = None
    try:
        min = Variable.objects.get(pk=int(dim[0])).dimensions.get(name=dim[1]).min
        max = Variable.objects.get(pk=int(dim[0])).dimensions.get(name=dim[1]).max
        if min is not None and max is not None:
            res = (min, max)
    except:
        pass
    if res is not None:
        return res[0], res[1]
    else:
        return (-1 * sys.maxint), sys.maxint


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

    chain_size = len(chain)
    cnt = 0
    while (min_of_maxes is None or max_of_mins is None) and cnt < chain_size:
        first_dim = next(iter(chain), None)
        max_of_mins = first_dim[0]
        min_of_maxes = first_dim[1]
        cnt += 1

    return max_of_mins, min_of_maxes
