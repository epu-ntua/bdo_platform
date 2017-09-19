import sys
import requests
import json

db = {
    'psycopg': "dbname='bdo_platform' user='postgres' host='localhost' password='bdo!'",
    'jdbc': "jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=1234",
}

job_id = int(sys.argv[1])
server_url = sys.argv[2]

try:
    from pyspark.sql import SparkSession
    from pyspark.ml.linalg import Vectors
    from pyspark.ml.feature import VectorAssembler
    from pyspark.ml.clustering import KMeans

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
    query = '(SELECT spark_part_id, %s, %s FROM (SELECT row_number() OVER () AS spark_part_id, ' \
            '* FROM (%s LIMIT 100) AS SPARKQ2) AS SPARKQ1) AS SPARKQ0' \
            % (args['feat_1'], args['feat_2'], args['query'])

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

    # dataframe2.drop("time_1")
    # dataframe2.drop("lon_3")

    # ********************************************* #

    # points_dataframe2 = dataframe2.select(args['feat_1'], args['feat_2']).rdd.map(lambda r: ('null', Vectors.dense([r[0], r[1]]))).toDF(
    #     ['label', 'features'])
    assembler = VectorAssembler(inputCols=[args['feat_1'], args['feat_2']],
                                outputCol="features")

    analysis_df = assembler.transform(raw_df)

    analysis_df.show()
    analysis_df.printSchema()

    # Trains a k-means model.
    kmeans = KMeans().setK(2).setSeed(1).setMaxIter(2)
    model = kmeans.fit(analysis_df)

    # Evaluate clustering by computing Within Set Sum of Squared Errors.
    wssse = model.computeCost(analysis_df)
    print("Within Set Sum of Squared Errors = " + str(wssse))

    # Shows the result.
    centers = [list(center) for center in model.clusterCenters()]
    print("Cluster Centers: ")
    for center in centers:
        print(center)


    result = dict()
    result['centers'] = list(centers)

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
