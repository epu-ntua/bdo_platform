# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from query_designer.models import *
from django.http import JsonResponse

from aggregator.models import *
from query_designer.query_processors.utils import ResultEncoder


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
    response, encoder = q.execute(dimension_values=dimension_values, variable=variable, only_headers=only_headers)

    # send results
    return JsonResponse(response, encoder=encoder)

