# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aggregator.models import *
from django.http import JsonResponse
from django.shortcuts import render

from mongo_client import get_mongo_db, MongoResponse


def datasets(request):

    return JsonResponse([d.to_json() for d in Dataset.objects.all()], safe=False)


def dataset_variables(request, dataset_id):
    page = int(request.GET.get('p', '1'))

    return JsonResponse([v.to_json() for v in Variable.objects.filter(dataset_id=dataset_id)], safe=False)


def dataset_variable_properties(request, dataset_id, variable_id):

    return JsonResponse([d.to_json() for d in Dimension.objects.filter(variable__dataset_id=dataset_id, variable_id=variable_id)],
                        safe=False)


def count_variable_values(request, dataset_id, variable_id):
    variable = Variable.objects.get(dataset_id=dataset_id, pk=variable_id)

    return JsonResponse({
        'count': variable.count_values(cursor=connection.cursor()),
    })
