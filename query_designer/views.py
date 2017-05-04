# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bson import ObjectId
from django.shortcuts import render

from mongo_client import get_mongo_db, MongoResponse


def index(request):
    return render(request, 'query_designer/index.html', {

    })


def datasets(request):

    # All datasets by default
    datasets = [{
        '_id': 'ALL',
        'title': 'All datasets',
        'default': True,
    }]

    # load all datasets from db
    datasets += [dataset for dataset in get_mongo_db().datasets.find()]

    return MongoResponse(datasets, safe=False)


def dataset_variables(request, dataset_id):
    page = int(request.GET.get('p', '1'))

    variables = get_mongo_db().variables

    _filter = {}
    if dataset_id != 'ALL':
        _filter['dataset_id'] = ObjectId(dataset_id)

    variables = variables.find(_filter)

    return MongoResponse([v for v in variables], safe=False)
