import psycopg2
from django.db import connections
from sets import Set

db_local = {
    'psycopg': "dbname='bdo_platform' user='postgres' host='localhost' password='bdo!'",
    'jdbc': "jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=bdo!",
}

db_zep = {
    'psycopg': "dbname='bigdataocean' user='bdo' host='212.101.173.21' password='df195715HBdhahfP'",
    'jdbc': "jdbc:postgresql://212.101.173.21:5432/bigdataocean?user=bdo&password=df195715HBdhahfP",
}


def get_job_arguments_and_info(job_id):
    # connect to BDO platform db to get job details
    try:
        conn = psycopg2.connect("dbname='bdo_platform' user='postgres' host='localhost' password='bdo!'")
    except:
        print "I am unable to connect to the database"
<<<<<<< Updated upstream
    # conn = connections['default']
=======
>>>>>>> Stashed changes
    cur = conn.cursor()
    cur.execute("""SELECT analysis_flow, arguments FROM analytics_jobinstance WHERE id = %d""" % job_id)
    row = cur.fetchone()

    analysis_flow = row[0]
    print analysis_flow
    args_dict = row[1]
    print args_dict
    args = list()
    for i in range(1, len(analysis_flow)+1):
        args.append(args_dict[str(i)])

    print('args')
    print(args)

    query = args_dict['query']

    info = list()
    for i in range(1, len(analysis_flow)+1):
        service_id = int(analysis_flow[str(i)])
        cur.execute("""SELECT info FROM bdo_main_app_service WHERE id = %d""" % service_id)
        row = cur.fetchone()
        info.append(row[0])

    print('info')
    print(info)

    # close custom connection
    conn.close()

    return args, query, info


def get_spark_query(args, info, query):
    # conn = psycopg2.connect(db['psycopg'])
    try:
        conn = psycopg2.connect("dbname='bigdataocean' user='bdo' host='212.101.173.21' password='df195715HBdhahfP'")
    except:
        print "I am unable to connect to the database"
<<<<<<< Updated upstream
    # conn = connections['default']
=======
>>>>>>> Stashed changes
    cur = conn.cursor()

    col_args = Set()
    for i, a in zip(info, args):
        for arg in i['arguments']:
            if arg['type'] == 'COLUMN' and '(derived)' not in a[arg['name']]:
                col_args.add(a[arg['name']])
    print('columns to query')
    print(col_args)

    spark_query = ''

    # define query
    spark_query = '(SELECT spark_part_id'

    for col in col_args:
        spark_query += ', ' + col

    spark_query += ' FROM (SELECT row_number() OVER () AS spark_part_id, ' \
                   '* FROM (%s LIMIT 100) AS SPARKQ2) AS SPARKQ1) AS SPARKQ0' \
                   % query

    # first count to partition
    print('executing query')
    cur.execute('SELECT COUNT(*) FROM (%s) AS SPARKQ2' % query)
    print('query succeeded')
    row = cur.fetchone()
    cnt = row[0]
    print('fetched data')
    print(cnt)

    # close custom connection
    conn.close()

    return spark_query, cnt
