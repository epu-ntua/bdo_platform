# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bson import ObjectId
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from mongo_client import get_mongo_db, MongoResponse


from query_designer.postgres_api import *
from query_designer.postgres_query import *

# from query_designer.mongo_api import *
# from query_designer.mongo_query import *


def index(request):
    return render(request, 'query_designer/index.html', {
        'sidebar_active': 'queries',
    })


def load_query(request, pk):
    q = Query.objects.get(pk=pk)

    return JsonResponse({
        'pk': q.pk,
        'title': q.title,
        'design': q.design,
    })


@csrf_exempt
def save_query(request, pk=None):
    # create or update
    if not pk:
        current_user = request.user
        if current_user.is_authenticated():
            q = Query(user=current_user)
        else:
            q = Query(user=User.objects.get(username='BigDataOcean'))
    else:
        q = Query.objects.get(pk=pk)

    # document
    if 'document' in request.POST:
        try:
            doc = json.loads(request.POST.get('document', ''))
        except ValueError:
            return JsonResponse({'error': 'Invalid query document'}, status=400)

        q.document = doc

    # design
    if 'design' in request.POST:
        try:
            design = json.loads(request.POST.get('design', ''))
        except ValueError:
            return JsonResponse({'error': 'Invalid design'}, status=400)

        q.design = design
    else:
        q.design = None

    # title
    if 'title' in request.POST:
        q.title = request.POST.get('title', 'Untitled query')

    # save
    q.save()

    # return OK response
    return JsonResponse({
        'pk': q.pk,
        'title': q.title,
    })


def get_query_variables(request, pk):
    # get the query
    q = Query.objects.get(pk=pk)
    # find the query's SELECT variables formatted as: 'variable's column name': 'variable's name'
    variables = dict()
    for var in q.document['from']:
        value_name = ''
        for col_name in var['select']:
            if col_name['type'] == 'VALUE':
                value_name = col_name['name']
        variables[value_name] = var['name']

    # return the found variables
    return HttpResponse(json.dumps(variables), content_type="application/json")
