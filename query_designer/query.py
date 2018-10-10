# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from query_designer.models import *
from django.http import JsonResponse

from aggregator.models import *
from query_designer.query_processors.utils import ResultEncoder
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from access_controller.policy_enforcement_point import PEP


def execute_query(request, pk=None):
    user = request.user
    if user.is_authenticated:
        doc_str = request.POST.get('query', '')

        # get or fake query object
        if not pk:
            q = AbstractQuery(document=json.loads(doc_str))
        else:
            q = AbstractQuery.objects.get(pk=pk)
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

        # check for the access
        try:
            dataset_list = []
            doc = q.document
            print q.document
            for el in doc['from']:
                dataset = Variable.objects.get(id=int(el['type'])).dataset
                if dataset.id not in dataset_list:
                    dataset_list.append(dataset.id)
            print dataset_list
            for dataset_id in dataset_list:
                access_decision = PEP.access_to_dataset_for_query(request, dataset_id)
                if access_decision is False:
                    raise PermissionDenied
        except:
            return HttpResponseForbidden()

        try:
            # execute
            result = q.execute(dimension_values=dimension_values,
                               variable=variable,
                               only_headers=only_headers,
                               with_encoder=True)
        except ValueError as ve:
            return JsonResponse({"error_message": str(ve.message)})
        response, encoder = result
        # import pdb
        # pdb.set_trace()
        # send results
        return JsonResponse(response, encoder=encoder)
    else:
        return HttpResponseForbidden()


