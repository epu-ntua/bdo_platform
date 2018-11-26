import prestodb
from django.db import connections

from django.conf import settings


def create_join_view_for_datasets(dataset1, dataset2):
    query = build_create_view_query(dataset1, dataset2)
    execute_create_view_query(query)
    add_relation_between_datasets(dataset1, dataset2)


def build_create_view_query(dataset1, dataset2):
    dataset1_columns = get_columns_for_table(dataset1)
    dataset2_columns = get_columns_for_table(dataset2)
    common_columns = find_common_columns(dataset1_columns, dataset2_columns)
    dataset1_private_cols = get_list_minus_sublist(dataset1_columns, common_columns)
    dataset2_private_cols = get_list_minus_sublist(dataset2_columns, common_columns)
    dataset1_vars = [c[0] for c in dataset1_private_cols if is_variable(c[0])]
    dataset2_vars = [c[0] for c in dataset2_private_cols if is_variable(c[0])]

    query = """CREATE OR REPLACE VIEW %s_%s AS""" % (dataset1, dataset2)
    query += build_select_clause(common_columns, dataset1, dataset1_vars, dataset2, dataset2_vars)
    query += """\nFROM %s \n JOIN %s \n""" % (dataset1, dataset2)
    query += build_join_on_clause(common_columns, dataset1, dataset2)
    query += build_group_by_clause(common_columns, dataset1)
    print query
    return query


def execute_create_view_query(query):
    cursor = get_presto_cursor()
    cursor.execute(query)


def add_relation_between_datasets(dataset1, dataset2):
    view_name = dataset1 + "_" + dataset2
    dataset1_id = extract_dataset_id(dataset1)
    dataset2_id = extract_dataset_id(dataset2)
    query = build_add_relation_query(dataset1_id, dataset2_id, view_name)
    cursor = connections['default'].cursor()
    cursor.execute(query)


def get_columns_for_table(table_name):
    cursor = get_presto_cursor()
    query = """
        SELECT column_name 
        FROM information_schema.columns
        WHERE table_name   = '%s'
            """ % table_name
    # print(query)
    cursor.execute(query)
    res = cursor.fetchall()
    return res


def get_presto_cursor():
    presto_credentials = settings.DATABASES['UBITECH_PRESTO']
    conn = prestodb.dbapi.connect(
        host=presto_credentials['HOST'],
        port=presto_credentials['PORT'],
        user=presto_credentials['USER'],
        catalog=presto_credentials['CATALOG'],
        schema=presto_credentials['SCHEMA'],
    )
    cursor = conn.cursor()
    return cursor


def find_common_columns(d1_columns, d2_columns):
    result = []
    for c1 in d1_columns:
        if c1 in d2_columns:
            result.append(c1)
    return result

def get_list_minus_sublist(list, sublist_to_be_removed):
    return [list_elem for list_elem in list if list_elem not in sublist_to_be_removed]



def is_variable(column):
    cursor = connections['default'].cursor()
    query = """select distinct 1 
          from aggregator_variable 
          where name = '%s'
    """ % column
    cursor.execute(query)
    res = cursor.fetchone()
    return res is not None


def build_select_clause(common_columns, dataset1, dataset1_variables, dataset2, dataset2_variables):
    query = "\nSELECT "
    for c in dataset1_variables:
        query += "AVG(%s.%s) AS %s, \n" % (dataset1, c[0], c[0])
    for c in common_columns:
        if c[0] == 'time':
            query += "date_trunc('hour', %s.%s) AS %s, \n" % (dataset1, c[0], c[0])
        elif c[0] in ['latitude', 'longitude']:
            query += "round(%s.%s, 1) AS %s, \n" % (dataset1, c[0], c[0])
        else:
            query += "%s.%s AS %s, \n" % (dataset1, c[0], c[0])
    idx = 0
    last_idx = len(dataset2_variables)
    for c in dataset2_variables:
        idx += 1
        query += "AVG(%s.%s) AS %s" % (dataset2, c[0], c[0])
        if idx != last_idx:
            query += ", \n"
    return query


def build_join_on_clause(common_columns, dataset1, dataset2):
    idx = 0
    length = len(common_columns)
    query = """ ON \n """
    for c in common_columns:
        idx += 1
        if c[0] == 'time':
            query += "date_trunc('hour', %s.%s) = date_trunc('hour', %s.%s) " % (dataset1, c[0], dataset2, c[0])
        elif c[0] in ['latitude', 'longitude']:
            query += "round(%s.%s, 1) = round(%s.%s, 1) " % (dataset1, c[0], dataset2, c[0])
        else:
            query += "%s.%s = %s.%s \n" % (dataset1, c[0], dataset2, c[0])
        if idx != length:
            query += " AND \n"
    return query


def build_group_by_clause(common_columns, dataset1):
    query = """\n GROUP BY \n"""
    length = len(common_columns)
    idx = 0
    for c in common_columns:
        idx += 1
        if c[0] == 'time':
            query += "date_trunc('hour', %s.%s) " % (dataset1, c[0])
        elif c[0] in ['latitude', 'longitude']:
            query += "round(%s.%s, 1) " % (dataset1, c[0])
        if idx != length:
            query += ", \n"
    return query


def extract_dataset_id(dataset1):
    query = """SELECT id \n
            FROM aggregator_dataset \n
            WHERE table_name = '%s' AND stored_at = 'UBITECH_PRESTO' """ % dataset1
    cursor = connections['default'].cursor()
    # print query
    cursor.execute(query)
    res = cursor.fetchone()
    return res[0]


def build_add_relation_query(dataset1_id, dataset2_id, view_name):
    query = """insert into aggregator_joinofdatasets 
              (view_name, dataset_first_id, dataset_second_id) 
              SELECT '%s', %s, %s
              WHERE NOT EXISTS
              	(SELECT view_name,dataset_first_id,dataset_second_id 
                FROM aggregator_joinofdatasets 
              WHERE view_name='%s' AND dataset_first_id= %s AND  dataset_second_id = %s)
              """ % (view_name, dataset1_id, dataset2_id, view_name, dataset1_id, dataset2_id)
    return query
