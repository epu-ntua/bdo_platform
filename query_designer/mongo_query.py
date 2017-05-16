# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
from django.http import JsonResponse
from django.shortcuts import render
from mongo_client import get_mongo_db, MongoResponse

import json
from bson import ObjectId


def execute_query(request):

    def matches(query_document, d):
        return d['value'] is not None


    db = get_mongo_db()
    query_document = json.loads(request.POST.get('query'), '')

    # use from to filter dataset
    filters = {
        'variable_id': ObjectId(query_document['from'][0]['type']['id']),
    }

    # fetch variables and their dimensions
    variable = db.variables.find_one({
        '_id': ObjectId(query_document['from'][0]['type']['id']),
    })
    dimensions = db.variables.aggregate([
        {"$match": {'_id': ObjectId(query_document['from'][0]['type']['id'])}},
        {"$unwind": "$dimension_ids"},
        {"$lookup": {
            "from": "dimensions",
            "localField": "dimension_ids",
            "foreignField": "_id",
            "as": "dimensions"
        }},
        {"$unwind": "$dimensions"},
        {"$group": {
            "_id": "$_id",
            "dimension_ids": {"$push": "$dimension_ids"},
            "dimensions": {"$push": "$dimensions"}
        }}
    ]).next()['dimensions']

    documents = db.data.find(filters)

    result = []
    match_idx = -1

    # read offset & limit
    try:
        offset = int(query_document['offset'])
    except (ValueError, KeyError, TypeError):
        offset = 0
    try:
        limit = int(query_document['limit'])
    except (ValueError, KeyError, TypeError):
        limit = 100

    finish = False
    for document in documents:
        if finish:
            break

        data = document['values']
        dim_values = []
        for dimension in dimensions:
            vv = []
            v = float(dimension['min'])
            idx = 0
            while v <= float(dimension['max']):
                vv.append((idx, v))
                if dimension['step'] is None:
                    break
                idx += 1
                v += float(dimension['step'])
            dim_values.append(vv)

        for comb in itertools.product(*dim_values):
            document = {}
            dt = data
            for idx, dimension in enumerate(comb):
                document[dimensions[idx]['name']] = comb[idx][1]
                dt = dt[comb[idx][0]]

            document['value'] = dt

            if matches(query_document, document):
                match_idx += 1

                if match_idx >= offset:
                    result.append(document)

                if match_idx >= limit:
                    finish = True
                    break

        # calculate how many matches there are based on the filters
    return MongoResponse(result, safe=False)