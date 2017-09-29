import psycopg2

db = {
    'psycopg': "dbname='bdo_platform' user='postgres' host='localhost' password='bdo!'",
    'jdbc': "jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=1234",
}


def get_job_arguments_and_info(job_id):
    # connect to BDO platform db to get job details
    conn = psycopg2.connect(db['psycopg'])
    cur = conn.cursor()
    cur.execute("""SELECT * FROM analytics_jobinstance WHERE id = %d""" % job_id)
    row = cur.fetchone()
    args = row[5]
    print(args)

    cur.execute("""SELECT info FROM analytics_jobinstance AS j INNER JOIN bdo_main_app_service as s 
                   ON j.base_analysis_id = s.id WHERE j.id = %d""" % job_id)
    row = cur.fetchone()
    info = row[0]
    print(info)

    # close custom connection
    conn.close()

    return args, info


def get_spark_query(args, info):
    conn = psycopg2.connect(db['psycopg'])
    cur = conn.cursor()

    query = ''
    # if info['arg_format'] == 'Feature-Label':
    #     # define query
    #     query = '(SELECT spark_part_id, %s, %s FROM (SELECT row_number() OVER () AS spark_part_id, ' \
    #             '* FROM (%s LIMIT 100) AS SPARKQ2) AS SPARKQ1) AS SPARKQ0' \
    #             % (args['feat'], args['label'], args['query'])
    #
    #     # TODO: JOHN REMOVE THE LIMIT 100
    # elif info['arg_format'] == 'Features':
    #     # define query
    #     query = '(SELECT spark_part_id, %s, %s FROM (SELECT row_number() OVER () AS spark_part_id, ' \
    #             '* FROM (%s LIMIT 100) AS SPARKQ2) AS SPARKQ1) AS SPARKQ0' \
    #             % (args['feat_1'], args['feat_2'], args['query'])
    # elif info['arg_format'] == 'Input-Output':
    #     # define query
    #     query = '(SELECT spark_part_id, %s FROM (SELECT row_number() OVER () AS spark_part_id, ' \
    #             '* FROM (%s LIMIT 100) AS SPARKQ2) AS SPARKQ1) AS SPARKQ0' \
    #             % (args['feat'], args['query'])
    # else:
    #     # TODO: add other arm_formats
    #     pass

    # define query
    query = '(SELECT spark_part_id'

    # TODO: If the same column appears in two features we may need to bring it only once
    for arg in info['arguments']:
        if arg['type'] == 'COLUMN':
            query += ', ' + args[arg['name']]

    query += ' FROM (SELECT row_number() OVER () AS spark_part_id, ' \
             '* FROM (%s LIMIT 100) AS SPARKQ2) AS SPARKQ1) AS SPARKQ0' \
             % (args['query'])

    # first count to partition
    print('executing query')
    cur.execute('SELECT COUNT(*) FROM (%s) AS SPARKQ2' % args['query'])
    print('query succeeded')
    row = cur.fetchone()
    cnt = row[0]
    print('fetched data')
    print(cnt)

    # close custom connection
    conn.close()

    return query, cnt
