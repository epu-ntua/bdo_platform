import json

import collections
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from query_designer.models import Query
from visualizer.models import Visualization
from service_builder.models import Service
from visualizer.utils import create_zep__query_paragraph, run_zep_paragraph


def create_new_service(request):
    user = request.user
    if request.user.is_authenticated():
        saved_queries = Query.objects.filter(user=user).exclude(document__from=[])
    else:
        saved_queries = []
    available_viz = Visualization.objects.filter(hidden=False)
    return render(request, 'service_builder/create_new_service.html', {
        'saved_queries': saved_queries,
        'available_viz': available_viz,
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
    return HttpResponse(json.dumps(result), content_type="application/json")


def publish_new_service(request):
    if request.method == 'POST':
        selected_queries = convert_unicode_json(json.loads(str(request.POST.get('selected_queries'))))
        print selected_queries
        arguments = convert_unicode_json(json.loads(str(request.POST.get('exposed_args'))))
        print arguments
        notebook_id = str(request.POST.get('notebook_id'))
        print notebook_id
        output_html = str(request.POST.get('output_html'))
        print output_html
        output_css = str(request.POST.get('output_css'))
        print output_css
        output_js = str(request.POST.get('output_js'))
        print output_js

        service = Service()
        service.user = request.user
        service.title = 'A Test Service'

        service.notebook_id = ''
        service.queries = selected_queries
        service.arguments = arguments

        service.output_html = output_html
        service.output_css = output_css
        service.output_js = output_js

        service.save()


    result = {}
    return HttpResponse(json.dumps(result), content_type="application/json")