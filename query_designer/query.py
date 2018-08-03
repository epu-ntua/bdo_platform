# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from query_designer.models import *
from django.http import JsonResponse

from aggregator.models import *
from query_designer.query_processors.utils import ResultEncoder

from django.http import HttpResponseForbidden


def execute_query(request, pk=None):
    user = request.user
    if user.is_authenticated:
        doc_str = request.POST.get('query', '')

        # get or fake query object
        if not pk:
            q = Query(document=json.loads(doc_str))
            dimension_values = request.POST.get('dimension_values', '')
            variable = request.POST.get('variable', '')
            only_headers = request.POST.get('only_headers', '').lower() == 'true'
            response, encoder = q.execute(request, dimension_values=dimension_values, variable=variable,
                                          only_headers=only_headers,
                                          with_encoder=True)
            return JsonResponse(response, encoder=encoder)

        else:
            q = Query.objects.get(pk=pk)
            try:
                q.document = json.loads(doc_str)
            except ValueError:
                pass

            # print q.document
            # print q.raw_query
            # get POST params
            dimension_values = request.POST.get('dimension_values', '')
            variable = request.POST.get('variable', '')
            only_headers = request.POST.get('only_headers', '').lower() == 'true'


            response, encoder = q.execute(request,dimension_values=dimension_values, variable=variable, only_headers=only_headers,
                                          with_encoder=True)
            # send results
            return JsonResponse(response, encoder=encoder)
    else:
        return HttpResponseForbidden()
