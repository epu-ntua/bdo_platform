import json

import collections
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from query_designer.models import Query
from visualizer.utils import create_zep__query_paragraph, run_zep_paragraph


def create_new_service(request):
    user = request.user
    if request.user.is_authenticated():
        saved_queries = Query.objects.filter(user=user).exclude(document__from=[])
    else:
        saved_queries = []
    return render(request, 'service_builder/create_new_service.html', {
        'saved_queries': saved_queries,
        'notebook_id': '2D9E8JBBX'})


def convert_unicode_json(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_unicode_json, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_unicode_json, data))
    else:
        return data


def update_filter(doc_filters, arg):
    if type(doc_filters) == dict:
        print doc_filters
        print 'dict'
        if "a" in doc_filters.keys():
            if (doc_filters["a"].strip() == arg['filter_a'].strip()) and (doc_filters['op'].strip() == arg['filter_op'].strip()):
                if type(doc_filters["b"]) == int:
                    doc_filters["b"] = int(arg['filter_b'])
                elif type(doc_filters["b"]) == float:
                    doc_filters["b"] = float(arg['filter_b'])
                elif (type(doc_filters["b"]) == str) or (type(doc_filters["b"]) == unicode) or (type(doc_filters["b"]) == basestring):
                    doc_filters["b"] = "'"+str(arg['filter_b'])+"'"
            else:
                print str(doc_filters)
                doc_filters["a"] = update_filter(doc_filters["a"], arg)
                doc_filters["b"] = update_filter(doc_filters["b"], arg)
    return doc_filters



def load_query(request):
    notebook_id = str(request.POST.get('notebook_id'))
    query_id = int(request.POST.get('query_id'))
    exposed_args = convert_unicode_json(json.loads(str(request.POST.get('exposed_args'))))

    doc = Query.objects.get(pk=query_id).document
    for arg in exposed_args:
        filters = convert_unicode_json(doc['filters'])
        doc['filters'] = update_filter(filters, arg)



    raw_query = Query(document=doc).raw_query
    query_paragraph_id = create_zep__query_paragraph(notebook_id, 'query paragraph', raw_query)
    run_zep_paragraph(notebook_id, query_paragraph_id)

    result = {}
    # return the found variables
    return HttpResponse(json.dumps(result), content_type="application/json")
