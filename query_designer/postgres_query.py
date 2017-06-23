# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import decimal
import datetime
import time
from collections import OrderedDict

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from query_designer.models import Query
from django.http import JsonResponse

from aggregator.models import *


class ResultEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, float):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


def execute_query(request, pk=None):
    # get document
    doc_str = request.POST.get('query', '')

    # get or fake query object
    if not pk:
        q = Query(document=json.loads(doc_str))
    else:
        q = Query.objects.get(pk=pk)
        try:
            q.document = json.loads(doc_str)
        except ValueError:
            pass

    # get POST params
    dimension_values = request.POST.get('dimension_values', '')
    variable = request.POST.get('variable', '')
    only_headers = request.POST.get('only_headers', '').lower() == 'true'

    # execute
    response = q.execute(dimension_values=dimension_values, variable=variable, only_headers=only_headers)

    # send results
    return JsonResponse(response, encoder=ResultEncoder)

