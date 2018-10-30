import sys
import requests
import json
from django.db import connections

#from bdo_platform import settings
from service_building_conf import db, get_job_arguments_and_info, get_spark_query


job_id = int(sys.argv[1])
server_url = sys.argv[2]


try:
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import VectorAssembler

    import importlib
    import math

    # collect the job's arguments
    args, query, info = get_job_arguments_and_info(job_id)
    print('-------------------------------------------')

    # get the SPARK query and the number of selected data per node
    spark_query, total_data = get_spark_query(args, info, query)
    print("spark query:")
    print(spark_query)

    # create a new SPARK session
    spark = SparkSession \
        .builder \
        .appName("Python Spark - Read from Postgres DB") \
        .getOrCreate()
    conn_dict = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bigdataocean',
        'USER': 'bdo',
        'PASSWORD': 'df195715HBdhahfP',
        'HOST': '212.101.173.21',
        'PORT': '5432',
    }
    # Get data and load them into a dataframe
    raw_df = spark.read.format('jdbc').options(
        url=str('jdbc:postgresql://'+conn_dict["HOST"]+':'+conn_dict["PORT"]+'/'+conn_dict["NAME"]+'?user='+conn_dict["USER"]+'&password='+conn_dict["PASSWORD"]),
        database=conn_dict["NAME"],
        dbtable=spark_query,
        partitionColumn="spark_part_id",
        lowerBound="1",
        upperBound=str(total_data),
        numPartitions=str(int(math.ceil(total_data / 20000.0)))
    ).load()
    print('dataframe loaded')

    raw_df.cache()  # Cache data for faster reuse
    raw_df = raw_df.dropna()  # drop rows with missing values

    raw_df.show()
    raw_df.printSchema()

    # ********************************************* #

    analysis_df = raw_df

    for i, a in zip(info, args):
        # Create the analysis object dynamically
        anal1 = getattr(importlib.import_module(i['package']), i['class'])
        anal1_obj = anal1()

        # Set the features column if neeeded
        if i['needs_feat_assembling'] == "True":
            # Gather all the features into the "features" column
            feat_cols = [a[feat] for feat in a.keys() if 'feat' in feat]
            assembler = VectorAssembler(inputCols=feat_cols, outputCol="features")
            analysis_df = assembler.transform(analysis_df)

        # Set the other type of columns if needed
        for arg in i['arguments']:
            if arg['type'] == 'COLUMN' and 'feat' not in arg['name']:
                setter = getattr(anal1_obj, 'set' + str(arg['name'][0]).capitalize() + str(arg['name'][1:]))
                setter(a[arg['name']])

        # ********************************************* #
        # Add the parameters
        print("Adding the parameters")
        for param in i['parameters']:
            setter = getattr(anal1_obj, 'set'+str(param['name'][0]).capitalize()+str(param['name'][1:]))
            if param['type'] == "INT":
                value = int(a[param['name']])
            elif param['type'] == "FLOAT":
                value = float(a[param['name']])
            elif param['type'] == "BOOLEAN":
                value = bool(a[param['name']])
            elif param['type'] == "STRING":
                value = str(a[param['name']])
            elif param['type'] == "FLOAT-LIST":
                value = [float(x) for x in str(a[param['name']]).split(" ")]
                if 'required_start' in param:
                    value = [-float("inf")] + value
                if 'required_end' in param:
                    value = value + [float("inf")]
            setter(value)
            # Print the set parameters for validation
            getter = getattr(anal1_obj, 'get' + str(param['name'][0]).capitalize() + str(param['name'][1:]))
            print(getter())
        # ********************************************* #

        # Select the model's actions depending on its type (Estimator, Transformer, Estimator-Transformer, other?)
        if i['type'] == 'Estimator':
            # Fit the model
            anal1_model = anal1_obj.fit(analysis_df)

            # Get the model and/or training results
            result = dict()
            for output in i['output']:
                value = getattr(anal1_model, output['name'])
                if output['type'] == 'method':
                    value = value()
                # if 'DenseVector' in str(value.__class__):
                if output['tolist'] == "1":
                    value = [v for v in value]
                elif output['tolist'] == "2":
                    value = [list(v) for v in value]
                result[output['title']] = value

            print(result)

        elif i['type'] == 'Estimator-Transformer':
            # Fit the model
            analysis_df = anal1_obj.fit(analysis_df).transform(analysis_df)
            result = dict()
            result['result'] = 'successfully transformed'
            analysis_df.show()

        elif i['type'] == 'Transformer':
            # Fit the model
            analysis_df = anal1_obj.transform(analysis_df)
            result = dict()
            result['result'] = 'successfully transformed'
            analysis_df.show()

    # Finally, return the resutls
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

