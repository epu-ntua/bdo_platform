import ast
import json

import collections, re
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import Context, Template

from bs4 import BeautifulSoup
from django.conf import settings

from query_designer.models import Query, TempQuery
from visualizer.models import Visualization
from service_builder.models import Service, ServiceTemplate
from visualizer.utils import create_zep__query_paragraph, run_zep_paragraph, run_zep_note, clone_zep_note, delete_zep_paragraph, \
    create_zep_getDict_paragraph, get_zep_getDict_paragraph_response, create_zep_arguments_paragraph


def create_new_service(request):
    user = request.user
    if request.user.is_authenticated():
        saved_queries = Query.objects.filter(user=user).exclude(document__from=[])
    else:
        saved_queries = []
    available_viz = Visualization.objects.filter(hidden=False)
    available_templates = ServiceTemplate.objects.all()
    if settings.TEST_SERVICES:
        service = Service.objects.get(pk=89)
    else:
        service = Service(user=user, private=False, notebook_id='2D9E8JBBX', published=False)
        service.save()

    # service = Service.objects.get(pk=3)
    return render(request, 'service_builder/create_new_service.html', {
        'saved_queries': saved_queries,
        'available_viz': available_viz,
        'available_templates': available_templates,
        'notebook_id': service.notebook_id,
        'service_id': service.id,})


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
    query_name = str(request.POST.get('query_name'))
    exposed_args = convert_unicode_json(json.loads(str(request.POST.get('exposed_args'))))

    print "query name: " + query_name

    doc = Query.objects.get(pk=query_id).document
    for arg in exposed_args:
        filters = convert_unicode_json(doc['filters'])
        doc['filters'] = update_filter(filters, arg)

    raw_query = Query(document=doc).raw_query
    query_paragraph_id = create_zep__query_paragraph(notebook_id, 'query paragraph', raw_query, index=0, df_name="df_" + query_name)
    run_zep_paragraph(notebook_id, query_paragraph_id)

    result = {query_name: {"dataframe": "df_" + query_name, "paragraph": query_paragraph_id}}
    return HttpResponse(json.dumps(result), content_type="application/json")


def publish_new_service(request):
    if request.method == 'POST':
        selected_queries = convert_unicode_json(json.loads(str(request.POST.get('selected_queries'))))
        # print selected_queries
        arguments = convert_unicode_json(json.loads(str(request.POST.get('exposed_args'))))
        # print arguments
        notebook_id = str(request.POST.get('notebook_id'))
        # print notebook_id
        output_html = str(request.POST.get('output_html'))
        # print output_html
        output_css = str(request.POST.get('output_css'))
        # print output_css
        output_js = str(request.POST.get('output_js'))
        # print output_js

        service = Service()
        service.user = request.user
        service.title = 'A Test Service'

        service.notebook_id = ''
        service.queries = selected_queries

        for arg in arguments['filter-arguments']:
            if arg['type'] == "SPATIAL_COV":
                arg['default_lat_min'] = arg['default'].split('<<')[1].split(',')[0]
                arg['default_lon_min'] = arg['default'].split('<<')[1].split(',')[1].split('>')[0]
                arg['default_lat_max'] = arg['default'].split('>,<')[1].split(',')[0]
                arg['default_lon_max'] = arg['default'].split('>,<')[1].split(',')[1].split('>')[0]
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

    # output_html = service.output_html.replace('src', 'src-a')
    output_html = service.output_html
    output_css = service.output_css
    output_js = service.output_js

    return render(request, 'service_builder/load_service.html', {
        'output_html': output_html,
        'output_css': output_css,
        'output_js': output_js,
        'arguments': json.dumps(arguments),
        'service_id': pk,
        'published': service.published})


def load_service_args_form_fields(request):
    service_id = int(request.GET.get('service_id', '0'))
    arguments = str(request.GET.get('arguments', ''))
    if service_id != 0:
        service = Service.objects.get(pk=service_id)
        html = render_to_string('service_builder/config-service-form-fields.html', {'arguments': service.arguments['filter-arguments']+service.arguments['algorithm-arguments']})
    else:
        arguments = convert_unicode_json(json.loads(arguments))
        html = render_to_string('service_builder/config-service-form-fields.html', {'arguments': arguments})
    return HttpResponse(html)


def update_service_output(request):
    service_id = int(request.POST.get('service_id', '0'))
    service = Service.objects.get(pk=int(service_id))
    output_html = str(request.POST.get('output_html'))
    output_css = str(request.POST.get('output_css'))
    output_js = str(request.POST.get('output_js'))
    service.output_html = output_html
    service.output_css = output_css
    service.output_js = output_js
    service.save()
    result = {}
    return HttpResponse(json.dumps(result), content_type="application/json")


def update_service_queries(request):
    service_id = int(request.POST.get('service_id', '0'))
    service = Service.objects.get(pk=int(service_id))
    selected_queries = convert_unicode_json(json.loads(str(request.POST.get('selected_queries'))))
    service.queries = selected_queries
    service.save()
    result = {}
    return HttpResponse(json.dumps(result), content_type="application/json")


def update_service_arguments(request):
    service_id = int(request.POST.get('service_id', '0'))
    service = Service.objects.get(pk=int(service_id))
    arguments = convert_unicode_json(json.loads(str(request.POST.get('exposed_args'))))
    print arguments
    for arg in arguments['filter-arguments']:
        if arg['type'] == "SPATIAL_COV":
            arg['default_lat_min'] = arg['default'].split('<<')[1].split(',')[0]
            arg['default_lon_min'] = arg['default'].split('<<')[1].split(',')[1].split('>')[0]
            arg['default_lat_max'] = arg['default'].split('>,<')[1].split(',')[0]
            arg['default_lon_max'] = arg['default'].split('>,<')[1].split(',')[1].split('>')[0]
    args_to_note = dict()
    for arg in arguments['algorithm-arguments']:
        args_to_note[arg['name']] = arg['default']
    new_arguments_paragraph = create_zep_arguments_paragraph(notebook_id=service.notebook_id, title='', args_json_string=json.dumps(args_to_note))
    run_zep_paragraph(notebook_id=service.notebook_id, paragraph_id=new_arguments_paragraph)
    if service.arguments_paragraph_id is not None:
        delete_zep_paragraph(service.notebook_id, service.arguments_paragraph_id)
    service.arguments_paragraph_id = new_arguments_paragraph
    service.arguments = arguments
    service.save()
    result = {}
    return HttpResponse(json.dumps(result), content_type="application/json")


def submit_service_args(request, service_id):
    service = Service.objects.get(pk=int(service_id))

    # 1.GATHER THE SERVICE ARGUMENTS
    service_args = convert_unicode_json(service.arguments)
    service_filter_args = service_args["filter-arguments"]
    print 'original args:'
    print service_filter_args
    for filter_arg in service_filter_args:
        filter_arg['filter_b'] = request.GET.get(filter_arg['name'], filter_arg['default'])
    print 'user args:'
    print service_filter_args

    service_algorithm_args = service_args["algorithm-arguments"]
    print 'original algorithm args:'
    print service_algorithm_args
    args_to_note = dict()
    for algorithm_arg in service_algorithm_args:
        args_to_note[algorithm_arg['name']] = request.GET.get(algorithm_arg['name'], algorithm_arg['default'])
    print 'user algorithm args:'
    print args_to_note

    # 2.CUSTOMIZE THE QUERIES BASED ON THE GATHERED USER ARGUMENTS (AND CREATE TEMPQUERIES)
    # query_mapping is a dict that maps the original queries of the template service to the tempQueries created after the user customisation
    query_mapping = dict()
    queries = convert_unicode_json(service.queries)
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
        query_mapping[query_id] = q_temp.id
    print queries

    # 3.BRING THE CUSTOMISED QUERIES TO THE SERVICE CODE
    original_notebook_id = service.notebook_id
    if settings.TEST_SERVICES:
        new_notebook_id = original_notebook_id
        excluded_paragraphs = []
        new_created_paragraphs = []
    else:
        new_notebook_id = clone_zep_note(original_notebook_id, "")

    # customise the respective queries in the code
    for name, info in queries.iteritems():
        for original_paragraph_id in info['paragraphs']:
            raw_query = TempQuery.objects.get(pk=int(info['temp_q'])).raw_query
            new_query_paragraph_id = create_zep__query_paragraph(new_notebook_id, '', raw_query, index=0, df_name="df_"+name)
            if settings.TEST_SERVICES:
                excluded_paragraphs.append(original_paragraph_id)
                new_created_paragraphs.append(new_query_paragraph_id)
            else:
                print 'deleting paragraph: {0}'.format(original_paragraph_id)
                delete_zep_paragraph(notebook_id=str(new_notebook_id), paragraph_id=str(original_paragraph_id))


    new_arguments_paragraph = create_zep_arguments_paragraph(notebook_id=new_notebook_id, title='',
                                                             args_json_string=json.dumps(args_to_note))
    if service.arguments_paragraph_id is not None:
        delete_zep_paragraph(new_notebook_id, service.arguments_paragraph_id)

    if settings.TEST_SERVICES:
        service.arguments_paragraph_id = new_arguments_paragraph
        service.save()


    # 4.RUN THE SERVICE CODE (one by one paragraph, or all together. CHOOSE..)
    run_zep_note(notebook_id=new_notebook_id, exclude=excluded_paragraphs)
    if settings.TEST_SERVICES:
        for p in new_created_paragraphs:
            print 'deleting paragraph: {0}'.format(p)
            delete_zep_paragraph(notebook_id=str(new_notebook_id), paragraph_id=str(p))

    # 5. GET THE SERVICE RESULTS
    result_paragraph_id = create_zep_getDict_paragraph(notebook_id=new_notebook_id, title='', dict_name='result')
    run_zep_paragraph(notebook_id=new_notebook_id, paragraph_id=result_paragraph_id)
    result = get_zep_getDict_paragraph_response(notebook_id=new_notebook_id, paragraph_id=result_paragraph_id)
    delete_zep_paragraph(notebook_id=new_notebook_id, paragraph_id=result_paragraph_id)

    # 5. BRING THE CUSTOMISED QUERIES TO THE SERVICE OUTPUT
    # print 'Change queries:'
    # output_html = service.output_html
    # for name, info in queries.iteritems():
    #     print name, info
    #     q = info['query_id']
    #     temp_q = info['temp_q']
    #     print output_html
    #     output_html = output_html.replace('query='+str(q), 'query='+str(temp_q))
    #     print output_html
    # output_css = service.output_css
    # output_js = service.output_js
    # print output_html
    # return render(request, 'service_builder/load_service.html', {
    #     'output_html': output_html,
    #     'output_css': output_css,
    #     'output_js': output_js,
    #     'arguments': json.dumps(service_args),
    #     'service_id': service_id})

    # result = dict()
    # result['query_mapping'] = query_mapping
    # return HttpResponse(json.dumps(result), content_type="application/json")

    # template = Template("Hello {{ name }}! ")

    # result = dict()
    # result['result1'] = "John"

    output_html = service.output_html
    output_css = service.output_css
    output_js = service.output_js

    if settings.TEST_SERVICES:
        import os
        with open(os.path.join(settings.BASE_DIR, 'service_builder\\templates\\service_builder\\service_template_1.html')) as f:
            output_html = f.read()

    for name, info in queries.iteritems():
        query = info['query_id']
        new_query = info['temp_q']
        # print output_html
        output_html = re.sub(r"query="+str(query)+"&", "query="+str(new_query)+"&", output_html)
        output_html = re.sub(r"query="+str(query)+"\"", "query="+str(new_query)+"\"", output_html)

    soup = BeautifulSoup(str(output_html), 'html.parser')
    service_result_container = soup.find(id="service_result_container")
    innerHTML = ''
    for c in service_result_container.contents:
        innerHTML += str(c)

    context = Context({"result": result})
    template = Template(innerHTML)

    return HttpResponse(template.render(context))


def load_template(request):
    template_id = int(request.GET.get('template_id', '0'))
    template = ServiceTemplate.objects.get(pk=template_id)

    result = dict()

    result['html'] = template.html
    result['css'] = template.css
    result['js'] = template.js

    return HttpResponse(json.dumps(result), content_type="application/json")


def load_results_to_template(request):
    # from django.template import engines
    # from django.template.loader import render_to_string
    # from django.template import Context, Template
    #
    # django_engine = engines['django']
    # # template = django_engine.from_string("Hello {{ name }}!")
    # template = Template("{% extends 'base.html' %} {% block content %} Hello {{ name }}! {% endblock %}")
    # context = Context({"name": "John"})
    # # rendered = render_to_string(template, {'name': 'bar'})
    # # return render(template, {'name': 'bar'})
    #
    # return HttpResponse(template.render(context))
    # # return render(request, template.render(context))

    from django.template import Context, Template
    template = Template("Hello {{ name }}! ")
    context = Context({"name": "John"})
    return HttpResponse(template.render(context))

