import sys
import requests
import json
from conf import db, get_job_arguments_and_info, get_spark_query


job_id = int(sys.argv[1])
server_url = sys.argv[2]


try:
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import VectorAssembler

    import importlib
    import math

    # collect the job's arguments
    args, info = get_job_arguments_and_info(job_id)
    print('-------------------------------------------')

    # get the SPARK query and the number of selected data per node
    query, total_data = get_spark_query(args, info)
    print("query:")
    print(query)

    # create a new SPARK session
    spark = SparkSession \
        .builder \
        .appName("Python Spark - Read from Postgres DB") \
        .getOrCreate()

    # Get data and load them into a dataframe
    raw_df = spark.read.format('jdbc').options(
        url=db['jdbc'],
        database='bdo_platform',
        dbtable=query,
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
    # Create the analysis object dynamically
    anal1 = getattr(importlib.import_module(info['package']), info['class'])
    anal1_obj = anal1()
    # Depending on the arguments format required by the analysis do the following
    # if info['arg_format'] == 'Feature-Label':
    #     # Gather all the features into the "features" column
    #     feat_cols = [args[feat] for feat in args.keys() if 'feat' in feat]
    #     assembler = VectorAssembler(inputCols=feat_cols, outputCol="features")
    #     analysis_df = assembler.transform(raw_df)
    #     # Set the "label" column
    #     anal1_obj.setLabelCol(args['label'])
    # elif info['arg_format'] == 'Features':
    #     # Gather all the features into the "features" column
    #     feat_cols = [args[feat] for feat in args.keys() if 'feat' in feat]
    #     assembler = VectorAssembler(inputCols=feat_cols, outputCol="features")
    #     analysis_df = assembler.transform(raw_df)
    # elif info['arg_format'] == 'Input-Output':
    #     # Set the input and output columns
    #     analysis_df = raw_df
    #     anal1_obj.setInputCol(args['feat'])
    #     anal1_obj.setOutputCol(args['feat'] + "transformed")
    # else:
    #     # TODO: add the other formats
    #     pass

    # Set the features column if neeeded
    if info['needs_feat_assembling'] == "True":
        # Gather all the features into the "features" column
        feat_cols = [args[feat] for feat in args.keys() if 'feat' in feat]
        assembler = VectorAssembler(inputCols=feat_cols, outputCol="features")
        analysis_df = assembler.transform(raw_df)
    else:
        analysis_df = raw_df
    # Set the other type of columns if needed
    for arg in info['arguments']:
        if arg['type'] == 'COLUMN' and 'feat' not in arg['name']:
            setter = getattr(anal1_obj, 'set' + str(arg['name'][0]).capitalize() + str(arg['name'][1:]))
            setter(args[arg['name']])

    # ********************************************* #
    # Add the parameters
    print("Adding the parameters")
    for param in info['parameters']:
        setter = getattr(anal1_obj, 'set'+str(param['name'][0]).capitalize()+str(param['name'][1:]))
        if param['type'] == "INT":
            value = int(args[param['name']])
        elif param['type'] == "FLOAT":
            value = float(args[param['name']])
        elif param['type'] == "BOOLEAN":
            value = bool(args[param['name']])
        elif param['type'] == "STRING":
            value = str(args[param['name']])
        elif param['type'] == "FLOAT-LIST":
            value = [float(x) for x in str(args[param['name']]).split(" ")]
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
    if info['type'] == 'Estimator':
        # Fit the model
        anal1_model = anal1_obj.fit(analysis_df)

        # Get the model and/or training results
        result = dict()
        for output in info['output']:
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

    elif info['type'] == 'Estimator-Transformer':
        # Fit the model
        analysis_df = anal1_obj.fit(analysis_df).transform(analysis_df)
        result = dict()
        result['result'] = 'successfully transformed'
        analysis_df.show()

    elif info['type'] == 'Transformer':
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

