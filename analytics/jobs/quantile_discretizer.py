import sys
import requests
import json

db = {
    'psycopg': "dbname='bdo_platform' user='postgres' host='localhost' password='1234'",
    'jdbc': "jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=1234",
}

job_id = int(sys.argv[1])
server_url = sys.argv[2]

try:
    from pyspark.sql import SparkSession
    from pyspark.ml.linalg import Vectors
    from pyspark.ml.feature import QuantileDiscretizer

    import psycopg2
    import math

    spark = SparkSession \
        .builder \
        .appName("Python Spark - Read from Postgres DB") \
        .getOrCreate()

    # Here is the application ID, it can be used to get number of stages, jobs, etc.
    appID = spark.sparkContext.applicationId

    # connect to BDO platform db to get job details
    conn = psycopg2.connect(db['psycopg'])
    cur = conn.cursor()
    cur.execute("""SELECT * from analytics_jobinstance WHERE id = %d""" % job_id)
    row = cur.fetchone()
    args = row[5]
    print(args)
    print('-------------------------------------------')
    # define query
    query = '(SELECT spark_part_id, %s FROM (SELECT row_number() OVER () AS spark_part_id, ' \
            '* FROM (%s LIMIT 100) AS SPARKQ2) AS SPARKQ1) AS SPARKQ0' \
            % (args['feat_1'], args['query'])

    # =========> JOHN REMOVE THE LIMIT 100

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

    print("query:")
    print(query)
    # get data
    raw_df = spark.read.format('jdbc').options(
        url=db['jdbc'],
        database='bdo_platform',
        dbtable=query,
        partitionColumn="spark_part_id",
        lowerBound="1",
        upperBound=str(cnt),
        numPartitions=str(int(math.ceil(cnt / 20000.0)))
    ).load()
    print('dataframe loaded')
    raw_df.cache()  # Cache data for faster reuse
    raw_df = raw_df.dropna()  # drop rows with missing values

    raw_df.show()

    raw_df.printSchema()

    raw_df.select(args['feat_1']).show()

    # ********************************************* #

    discretizer = QuantileDiscretizer(numBuckets=3, inputCol=args['feat_1'], outputCol=args['feat_1']+"_discretized_3")

    discretized_df = discretizer.fit(raw_df).transform(raw_df)
    discretized_df.show()

    result = dict()
    result['result'] = args['feat_1'] + ' succeessfully splited into 3 quantiles'

    requests.post('%s/analytics/jobs/%d/update/' % (server_url, job_id), data={
        'success': 'true',
        'results': json.dumps(result),
    })
except Exception as e:
    print('error')
    print(e)
    requests.post('%s/analytics/jobs/%d/update/' % (server_url, job_id), data={
        'success': 'false',
        'error': str(e),
    })
