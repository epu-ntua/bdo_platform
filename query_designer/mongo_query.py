# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
from django.http import JsonResponse
from django.shortcuts import render
from mongo_client import get_mongo_db, MongoResponse

import json
from bson import ObjectId


def execute_query(request):

    db = get_mongo_db()
    query_document = json.loads(request.POST.get('query'), '')

    # use from to filter dataset
    filters = {}

    # fetch variables and their dimensions
    variable = db.variables.find_one({
        '_id': ObjectId(query_document['from'][0]['type']),
    })

    documents = db.get_collection(variable['name']).find(filters)

    result = []

    # offset & limit
    offset = None
    limit = None
    if 'offset' in query_document and query_document['offset']:
        offset = int(query_document['offset'])

    if 'limit' in query_document and query_document['limit']:
        limit = int(query_document['limit'])

    if offset:
        documents = documents.skip(offset)

    if limit:
        documents = documents.limit(limit)

    return MongoResponse(result, safe=False)