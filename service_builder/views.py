import ast
import json

import collections
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from query_designer.models import Query, TempQuery
from visualizer.models import Visualization
from service_builder.models import Service
from visualizer.utils import create_zep__query_paragraph, run_zep_paragraph, run_zep_note, clone_zep_note, delete_zep_paragraph


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
        print arg
        print arg.__class__
        if "a" in doc_filters.keys():
            if (str(doc_filters["a"]).strip() == arg['filter_a'].strip()) and (str(doc_filters['op']).strip() == arg['filter_op'].strip()):
                found = False
                try:
                    doc_filters["b"] = int(arg['filter_b'])
                    found = True
                except ValueError:
                    pass  # it was not an int.
                if not found:
                    try:
                        doc_filters["b"] = float(arg['filter_b'])
                        found = True
                    except ValueError:
                        pass  # it was not an int.
                if not found:
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


def load_service(request, pk):
    service = Service.objects.get(pk=pk)
    title = service.title

    notebook_id = service.notebook_id
    queries = service.queries
    arguments = service.arguments

    output_html = service.output_html.replace('src', 'src-a')
    output_css = service.output_css
    output_js = service.output_js

    return render(request, 'service_builder/load_service.html', {
        'output_html': output_html,
        'output_css': output_css,
        'output_js': output_js,
        'arguments': json.dumps(arguments)})


def load_service_args_form_fields(request):
    service_id = int(request.GET.get('service_id'))
    service = Service.objects.get(pk=service_id)

    html = render_to_string('service_builder/config-service-form-fields.html', {'arguments': service.arguments['filter-arguments']})
    return HttpResponse(html)


def submit_service_args(request, service_id):
    service = Service.objects.get(pk=int(service_id))

    # 1.GATHER THE SERVICE ARGUMENTS
    service_args = convert_unicode_json(service.arguments)
    service_filter_args = service_args["filter-arguments"]
    print service_filter_args
    for filter_arg in service_filter_args:
        filter_arg['filter_b'] = request.GET.get(filter_arg['name'], filter_arg['default'])
    print service_filter_args

    # 2.CUSTOMIZE THE QUERIES BASED ON THE GATHERED USER ARGUMENTS (AND CREATE TEMPQUERIES)
    # query_mapping is a dict that maps the original queries of the template service to the tempQueries created after the user customisation
    queries = service.queries
    for name, q in queries.iteritems():
        query_id = int(q['query_id'])
        query = Query.objects.get(pk=query_id)
        doc = query.document
        for arg in service_filter_args:
            arg_query_id = int(queries[arg['query']]['query_id'])
            if arg_query_id == query_id:
                filters = convert_unicode_json(doc['filters'])
                doc['filters'] = update_filter(filters, arg)
        q_temp = TempQuery(original=query, document=doc, user_id=query.user_id)
        q_temp.save()
        q['temp_q'] = q_temp.id
    print queries

    # 3.BRING THE CUSTOMISED QUERIES TO THE SERVICE CODE
    original_notebook_id = service.notebook_id
    new_notebook_id = clone_zep_note(original_notebook_id, "")
    # new_notebook_id = original_notebook_id
    # customise the respective queries in the code
    for name, info in queries.iteritems():
        for original_paragraph_id in info['paragraphs']:
            delete_zep_paragraph(notebook_id=new_notebook_id, paragraph_id=original_paragraph_id)
            raw_query = TempQuery.objects.get(pk=int(info['temp_q'])).raw_query
            paragraph_id = create_zep__query_paragraph(new_notebook_id, '', raw_query, index=0, df_name="df_"+name)


    # 4.RUN THE SERVICE CODE (one by one paragraph, or all together. CHOOSE..)
    run_zep_note(new_notebook_id)

    # 5. BRING THE CUSTOMISED QUERIES TO THE SERVICE OUTPUT
    output_html = service.output_html
    for name, info in queries.iteritems():
        q = info['query_id']
        temp_q = info['temp_q']
        output_html = output_html.replace('query='+str(q), 'query='+str(temp_q))
    output_css = service.output_css
    output_js = service.output_js

    return render(request, 'service_builder/load_service.html', {
        'output_html': output_html,
        'output_css': output_css,
        'output_js': output_js,
        'arguments': json.dumps(service_args)})

    # first! run code (loading..) and then close modal and render html
    result = dict()
    return HttpResponse(json.dumps(result), content_type="application/json")
