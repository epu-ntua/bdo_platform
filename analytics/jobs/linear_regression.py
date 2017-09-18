import sys
import requests
import json

job_id = int(sys.argv[1])
server_url = sys.argv[2]

try:
    from pyspark.sql import SparkSession
    from pyspark.ml.regression import LinearRegression
    from pyspark.mllib.regression import LabeledPoint
    from pyspark.ml.linalg import Vectors

    import psycopg2
    import math

    spark = SparkSession \
        .builder \
        .appName("Python Spark - Read from Postgres DB") \
        .getOrCreate()

    # connect to BDO platform db to get job details
    conn = psycopg2.connect("dbname='bdo_platform' user='postgres' host='localhost' password='1234'")
    cur = conn.cursor()
    cur.execute("""SELECT * from analytics_jobinstance WHERE id = %d""" % job_id)
    row = cur.fetchone()
    args = row[5]
    print(args)
    print('-------------------------------------------')
    # define query
    query = '(SELECT spark_part_id, %s, %s FROM (SELECT row_number() OVER () AS spark_part_id, ' \
            '* FROM (%s) AS SPARKQ2) AS SPARKQ1) AS SPARKQ0' \
            % (args['x'], args['y'], args['query'])

    # query = '(SELECT spark_part_id, %s, %s FROM (SELECT row_number() OVER () AS spark_part_id, ' \
    #         '* FROM (%s) AS SPARKQ2) AS SPARKQ1) AS SPARKQ0' \
    #         % ('i0_value', 'i1_value', args['query'])

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
    dataframe2 = spark.read.format('jdbc').options(
        url="jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=1234",
        database='bdo_platform',
        dbtable=query,
        partitionColumn="spark_part_id",
        lowerBound="1",
        upperBound=str(cnt),
        numPartitions=str(int(math.ceil(cnt / 20000.0)))
    ).load()
    print('dataframe loaded')
    dataframe2.cache()  # Cache data for faster reuse
    dataframe2 = dataframe2.dropna()  # drop rows with missing values

    dataframe2.show()

    dataframe2.printSchema()

    dataframe2.select(args['x']).show()

    # dataframe2.drop("time_1")
    # dataframe2.drop("lon_3")

    # ********************************************* #

    points_dataframe2 = dataframe2.select(args['x'], args['y']).rdd.map(lambda r: (r[0], Vectors.dense([r[1]]))).toDF(
        ['label', 'features'])
    points_dataframe2.show()

    # def parsePoint(line):
    #    values = [float(x) for x in line.split(',')]
    #    return (values[1], Vectors.dense([values[0]]))

    # points_dataframe2 = dataframe2.rdd.map(parsePoint).toDF(['label','features'])

    lr = LinearRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)

    # Fit the model
    lrModel = lr.fit(points_dataframe2)

    # Summarize the model over the training set and print out some metrics
    trainingSummary = lrModel.summary

    result = {}
    result['coefficients'] = list(lrModel.coefficients)
    result['intercept'] = lrModel.intercept
    result['RMSE'] = trainingSummary.rootMeanSquaredError
    result['r2'] = trainingSummary.r2

    print(result)

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

