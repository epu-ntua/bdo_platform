# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
import time

import pymongo
from django.http import JsonResponse
from django.shortcuts import render
from mongo_client import get_mongo_db, MongoResponse

import json
from bson import ObjectId


def execute_query(request):
    query_document = json.loads(request.POST.get('query'), '')
    dimension_values = request.POST.get('dimension_values', '')
    variable = request.POST.get('variable', '')
    only_headers = request.POST.get('only_headers', '').lower() == 'true'
    if dimension_values:
        dimension_values = dimension_values.split(',')
    else:
        dimension_values = []

    db = get_mongo_db()

    # use from to filter dataset
    filters = {}

    # fetch variables and their dimensions
    v = db.variables.find_one({
        '_id': ObjectId(query_document['from'][0]['type']),
    })

    documents = db.get_collection(v['name']).find(filters)

    # offset & limit
    offset = None
    limit = None
    if 'offset' in query_document:
        offset = int(query_document['offset'])

    if 'limit' in query_document:
        limit = int(query_document['limit'])

    if offset:
        documents = documents.skip(offset)

    if limit:
        documents = documents.limit(limit)

    if not only_headers:
        t1 = time.time()

        # count pages
        if limit is not None:
            pages = {
                'current': (offset / limit) + 1,
                'total': 1
            }
        else:
            pages = {
                'current': 1,
                'total': 1
            }

        results = [d for d in documents]
        for r in results:
            del r['_id']

        if len(results) == limit:
            pages['total'] = int(db.get_collection(v['name']).count() / (limit + 0.0)) + 1

    # get headers
    headers = []
    h_docs = []
    for s in query_document['from'][0]['select']:
        if s['type'] != 'VALUE':
            h_doc = db.dimensions.find_one({'_id': ObjectId(s['type'])})
        else:
            h_doc = {
                'name': 'value',
                'unit': 'VALUE',
                'axis': None
            }

        h_docs.append(h_doc)
        headers.append({
            'title': s['title'],
            'name': s['name'],
            'unit': h_doc['unit'],
            'quote': '',
            'axis': h_doc['axis'],
        })

    # include dimension values if requested
    for d_name in dimension_values:
        hdx, header = [hi for hi in enumerate(headers) if hi[1]['name'] == d_name][0]
        header['values'] = db.get_collection(v['name']).distinct(h_docs[hdx]['name'])

    # include variable ranges if requested
    if variable:
        vdx, v_header = [vi for vi in enumerate(headers) if vi[1]['name'] == variable][0]
        v_header['range'] = {
            'min': db.get_collection(v['name']).find().sort([("value", pymongo.ASCENDING)]).limit(1)[0]['value'],
            'max': db.get_collection(v['name']).find().sort([("value", pymongo.DESCENDING)]).limit(1)[0]['value'],
        }

    if not only_headers:
        # monitor query duration
        q_time = (time.time() - t1) * 1000

    if not only_headers:
        response = {
            'results': results,
            'headers': {
                'runtime_msec': q_time,
                'pages': pages,
            }
        }
    else:
        response = {'headers': {}}
    response['headers']['columns'] = headers

    return MongoResponse(response, safe=False)