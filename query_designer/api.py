# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aggregator.models import *
from django.http import JsonResponse
from models import *
from django.shortcuts import render

from mongo_client import get_mongo_db, MongoResponse


def datasets(request):
    results = [{
        '_id': 'ALL',
        'title': 'All datasets',
        'default': True,
    }]

    for d in Dataset.objects.all():
        results.append(d.to_json())

    return JsonResponse(results, safe=False)


def queries(request):
    results = []

    for q in Query.objects.filter(user=request.user):
        results.append({'id': q.id, 'name': q.title, 'created': str(q.created)})

    return JsonResponse(results, safe=False)



def dataset_variables(request, dataset_id):
    page = int(request.GET.get('p', '1'))

    qs = Variable.objects.all()
    if dataset_id != 'ALL':
        qs = qs.filter(dataset_id=dataset_id)

    return JsonResponse([v.to_json() for v in qs], safe=False)


def dataset_variable_properties(request, dataset_id, variable_id):
    property_info = [d.to_json() for d in Dimension.objects.filter(variable_id=variable_id)]
    response = [Variable.objects.get(pk=variable_id).to_json()] + property_info

    return JsonResponse(response, safe=False)


def count_variable_values(request, dataset_id, variable_id):
    variable = Variable.objects.get(pk=variable_id)

    return JsonResponse({
        'count': variable.dataset.number_of_rows,
    })
