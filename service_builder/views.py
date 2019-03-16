import ast
import json

import collections, re
from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import Context, Template

from bs4 import BeautifulSoup
from django.conf import settings

from background_task import background
from django.utils.datastructures import MultiValueDictKeyError

from query_designer.models import Query, TempQuery
from service_builder.forms import ServiceForm
from visualizer.models import Visualization
from service_builder.models import Service, ServiceTemplate, ServiceInstance
from visualizer.utils import create_zep__query_paragraph, run_zep_paragraph, run_zep_note, clone_zep_note, delete_zep_paragraph, \
    create_zep_getDict_paragraph, get_zep_getDict_paragraph_response, create_zep_arguments_paragraph, get_result_dict_from_livy, close_livy_session, \
    delete_zep_notebook


def create_new_service(request):
    user = request.user
    if request.user.is_authenticated():
        saved_queries = Query.objects.filter(user=user).exclude(document__from=[])
    else:
        saved_queries = []
    available_viz = Visualization.objects.filter(hidden=False).order_by('order')
    available_templates = ServiceTemplate.objects.all()
    if settings.TEST_SERVICES:
        service = Service.objects.get(pk=89)
        # new_notebook_id = clone_zep_note("2DF6DH32T", "BigDataOceanService")
        # run_zep_paragraph(new_notebook_id, paragraph_id='20180514-011802_1275384604')
        # service = Service(user=user, private=True, notebook_id=new_notebook_id, published=False, arguments_paragraph_id='20180518-114325_90076876')
        # service.save()
    else:
        new_notebook_id = clone_zep_note(settings.SERVICE_BUILDER_BASE_NOTE, "BigDataOceanService")
        # run_zep_paragraph(new_notebook_id, paragraph_id='20180514-011802_1275384604')
        service = Service(user=user, private=True, notebook_id=new_notebook_id, published=False, arguments_paragraph_id=settings.BASE_NOTE_ARG_PARAGRAPH)
        service.save()

    form = ServiceForm()
    # service = Service.objects.get(pk=3)
    return render(request, 'service_builder/create_new_service.html', {
        'saved_queries': saved_queries,
        'available_viz': available_viz,
        'available_templates': available_templates,
        'notebook_id': service.notebook_id,
        'zeppelin_url': settings.ZEPPELIN_URL,
        'service_id': service.id,
        'service_form': form})


def run_initial_zep_paragraph(request):
    service_id = request.POST.get('service_id')
    service = Service.objects.get(pk=service_id)
    run_zep_paragraph(service.notebook_id, paragraph_id=settings.BASE_NOTE_LOADER_PARAGRAPH, livy_session_id=0, mode='zeppelin')
    run_zep_paragraph(service.notebook_id, paragraph_id=settings.BASE_NOTE_ARG_PARAGRAPH, livy_session_id=0, mode='zeppelin')
    return HttpResponse("OK")


def convert_unicode_json(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_unicode_json, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_unicode_json, data))
    else:
        return data


@background(schedule=600)
def clean_up_new_note(notebook_id):
    delete_zep_notebook(notebook_id)


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
    query_paragraph_id = create_zep__query_paragraph(notebook_id, 'query paragraph', raw_query, index=2, df_name="df_" + query_name)
    run_zep_paragraph(notebook_id, query_paragraph_id, livy_session_id=0, mode='zeppelin')


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
        title = str(request.POST.get('title'))
        description = str(request.POST.get('description'))
        price = str(request.POST.get('price'))
        private = str(request.POST.get('private'))

        service_id = int(request.POST.get('service_id'))


        service = Service.objects.get(pk=service_id)
        service.user = request.user

        service.notebook_id = notebook_id

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

        service.title = title
        service.description = description
        service.price = price
        if private == "True":
            service.private = True
        else:
            service.private = False
        service.published = True

        service.save()

    result = {}
    return HttpResponse(json.dumps(result), content_type="application/json")


def load_service(request, pk):
    service = Service.objects.get(pk=pk)
    title = service.title

    notebook_id = service.notebook_id
    queries = service.queries
    arguments = service.arguments

    output_html = service.output_html
    output_css = service.output_css
    output_js = service.output_js

    # if settings.TEST_SERVICES:
    #     from bdo_platform.settings import BASE_DIR
    #     import os
    #     path = os.path.join(BASE_DIR + '\\service_builder\\templates\\service_builder\\', 'service_template_1.html')
    #     with open(path, 'r') as f:
    #         output_html = f.read()
    #     path = os.path.join(BASE_DIR + '\\service_builder\\static\\service_builder\\css\\', 'service_template_1.css')
    #     with open(path, 'r') as f:
    #         output_css = f.read()
    #     path = os.path.join(BASE_DIR + '\\service_builder\\static\\service_builder\\js\\', 'service_template_1.js')
    #     with open(path, 'r') as f:
    #         output_js = f.read()

    output_html = output_html.replace('iframe src', 'iframe src-a')

    return render(request, 'service_builder/load_service.html', {
        'service_title': service.title,
        'output_html': output_html,
        'output_css': output_css,
        'output_js': output_js,
        'arguments': json.dumps(arguments),
        'service_id': pk,
        'published': service.published})


def load_service_preview(request, pk):
    service = Service.objects.get(pk=pk)
    title = service.title


    notebook_id = service.notebook_id
    queries = service.queries
    arguments = service.arguments

    output_html = service.output_html
    output_css = service.output_css
    output_js = service.output_js

    return render(request, 'service_builder/load_service.html', {
        'service_title': service.title,
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
    run_zep_paragraph(notebook_id=service.notebook_id, paragraph_id=new_arguments_paragraph, livy_session_id=0, mode='zeppelin')
    if service.arguments_paragraph_id is not None:
        delete_zep_paragraph(service.notebook_id, service.arguments_paragraph_id)
    service.arguments_paragraph_id = new_arguments_paragraph
    service.arguments = arguments
    service.save()
    result = {}
    return HttpResponse(json.dumps(result), content_type="application/json")


def submit_service_args(request, service_id):
    service = Service.objects.get(pk=int(service_id))
    if service.title == 'Oil Spill Simulation Service':
        output_html = service.output_html
        soup = BeautifulSoup(str(output_html), 'html.parser')
        service_result_container = soup.find(id="service_result_container")
        innerHTML = ''
        for c in service_result_container.contents:
            innerHTML += str(c)

        context = Context({"result": ''})
        template = Template(innerHTML)
        return HttpResponse(template.render(context))
    livy = service.through_livy
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now())
    service_exec.save()

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

    service_exec.arguments = {'filter-arguments': service_filter_args, 'algorithm-arguments': service_algorithm_args}
    service_exec.save()

    # 2.CUSTOMIZE THE QUERIES BASED ON THE GATHERED USER ARGUMENTS (AND CREATE TEMPQUERIES)
    # query_mapping is a dict that maps the original queries of the template service to the tempQueries created after the user customisation
    query_mapping = dict()
    queries = convert_unicode_json(service.queries)
    if queries is not None:
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
        excluded_paragraphs = []
        new_notebook_id = clone_zep_note(original_notebook_id, "")
        clean_up_new_note(new_notebook_id)

    service_exec.notebook_id = new_notebook_id
    service_exec.save()

    print 'Notebook ID: {0}'.format(new_notebook_id)

    # customise the respective queries in the code
    if queries is not None:
        for name, info in queries.iteritems():
            for original_paragraph_id in info['paragraphs']:
                raw_query = TempQuery.objects.get(pk=int(info['temp_q'])).raw_query
                new_query_paragraph_id = create_zep__query_paragraph(new_notebook_id, '', raw_query, index=2, df_name="df_"+name)
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

    output_html = service.output_html
    output_html = output_html.replace(original_notebook_id, new_notebook_id)
    soup = BeautifulSoup(output_html, 'html.parser')
    visualizations = []
    for f in soup.findAll('iframe'):
        visualizations.append(f.get("src"))

    import urlparse
    dataframe_viz = []
    for url in visualizations:
        parsed = urlparse.urlparse(url)
        if 'notebook_id' in urlparse.parse_qs(parsed.query).keys():
            if 'df' in urlparse.parse_qs(parsed.query).keys():
                df = urlparse.parse_qs(parsed.query)['df'][0]
            elif 'df1' in urlparse.parse_qs(parsed.query).keys():
                df = urlparse.parse_qs(parsed.query)['df1'][0]
            elif 'df2' in urlparse.parse_qs(parsed.query).keys():
                df = urlparse.parse_qs(parsed.query)['df2'][0]

            dataframe_viz.append({'notebook_id': urlparse.parse_qs(parsed.query)['notebook_id'][0],
                                  'df': df,
                                  'url': url,
                                  'done': False})

    service_exec.dataframe_visualizations = dataframe_viz
    service_exec.save()

    # 4.RUN THE SERVICE CODE (one by one paragraph, or all together. CHOOSE..)
    try:
        if livy:
            livy_session = run_zep_note(notebook_id=new_notebook_id, exclude=excluded_paragraphs, mode='livy')
            service_exec.livy_session = livy_session
            service_exec.save()
        else:
            run_zep_note(notebook_id=new_notebook_id, exclude=excluded_paragraphs, mode='zeppelin')
        # data = create_livy_toJSON_paragraph()
        # with open('df_json_{0}___{1}.json'.format(new_notebook_id, df_name), 'w') as outfile:
        #     json.dump(data, outfile)

        if settings.TEST_SERVICES:
            for p in new_created_paragraphs:
                print 'deleting paragraph: {0}'.format(p)
                delete_zep_paragraph(notebook_id=str(new_notebook_id), paragraph_id=str(p))

        # 5. GET THE SERVICE RESULTS
        if livy:
            result = get_result_dict_from_livy(livy_session, 'result')
        else:
            result_paragraph_id = create_zep_getDict_paragraph(notebook_id=new_notebook_id, title='', dict_name='result')
            run_zep_paragraph(notebook_id=new_notebook_id, paragraph_id=result_paragraph_id, livy_session_id=0, mode='zeppelin')
            result = get_zep_getDict_paragraph_response(notebook_id=new_notebook_id, paragraph_id=result_paragraph_id)
            delete_zep_paragraph(notebook_id=new_notebook_id, paragraph_id=result_paragraph_id)


        print 'result: ' + str(result)
        # result = json.loads(str(result))

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

        # if settings.TEST_SERVICES:
        #     import os
        #     with open(os.path.join(settings.BASE_DIR, 'service_builder\\templates\\service_builder\\service_template_1.html')) as f:
        #         output_html = f.read()

        if queries is not None:
            for name, info in queries.iteritems():
                query = info['query_id']
                new_query = info['temp_q']
                # print output_html
                output_html = re.sub(r"query="+str(query)+"&", "query="+str(new_query)+"&", output_html)
                output_html = re.sub(r"query="+str(query)+"\"", "query="+str(new_query)+"\"", output_html)

        output_html = output_html.replace(original_notebook_id, new_notebook_id)
        soup = BeautifulSoup(str(output_html), 'html.parser')
        service_result_container = soup.find(id="service_result_container")
        innerHTML = ''
        for c in service_result_container.contents:
            innerHTML += str(c)

        context = Context({"result": result})

        template = Template(innerHTML)
        return HttpResponse(template.render(context))
    except Exception as e:
        print '%s (%s)' % (e.message, type(e))
        if livy:
            close_livy_session(service_exec.livy_session)

        return HttpResponse(status=500)




def load_template(request):
    template_id = int(request.GET.get('template_id', '0'))
    template = ServiceTemplate.objects.get(pk=template_id)

    result = dict()

    result['html'] = template.html
    result['css'] = template.css
    result['js'] = template.js

    return HttpResponse(json.dumps(result), content_type="application/json")


def updateServiceInstanceVisualizations(execution_id, url):
    service_exec = ServiceInstance.objects.get(pk=execution_id)
    for key in service_exec.dataframe_visualizations.keys():
        viz = service_exec.dataframe_visualizations[key]
        if viz['url'] == url and not viz['done']:
            viz['done'] = True
            break
    all_done = True
    for key in service_exec.dataframe_visualizations.keys():
        viz = service_exec.dataframe_visualizations[key]
        if not viz['done']:
            all_done = False
            break
    if all_done:
        close_livy_session(service_exec.livy_session)
        delete_zep_notebook(service_exec.notebook_id)


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


#----------HCMR Dummy Service -------------------------------------------------------------------#
from django.contrib.auth.decorators import login_required
import ftplib,time,io

#Create the input file for the oil spill simulator and put it on the HCMR ftp size
#GET Parameters
#LATLON REQUIRED	(e.g."37.3778 25.9595")		: Position of the oil slick: latitude (positive for North, negative for South) and longitude (positive for East, negative for West) in degrees (decimal number)
#DEPTH	DEFAULT=0	(e.g."0 0")		: Depth of the oil spill: in m (it is 0 in the case of a surface slick)
#DATETIME REQUIRED	(e.g."2017 12 27 1000")	: Date and Time start
#DURATION DEFAULT=0 (e.g."48")			: Duration of the spill release in hours
#VOLUME	REQUIRED	 (e.g."2500")	: Total amount (volume) of spilled oil in m3
#SIMULATIONNAME	GENERATEDBYSYSTEM 	(e.g. userid + BDOB171227_1000_F)		: user selected name of the simulation
#DENSITYOILTYPE	DEFAULT=920.0 (e.g. "920")	: Density of oil (kg/m3) or API number or Type of oil
#SIM_TYPE	GENERATEDBYSYSTEM ("FORWARD")		:Type of the requested simulation (FORWARD or BACKWARD)
#SIM_LENGTH DEFAULT=48 	(e.g. "48")		: Length of the requested simulation in hours
#STEP DEFAULT=2		(e.g. "2")		: requested time interval between 2 outputs in hours (decimal number)
#GRD_SIZE	GENERATEDBYSYSTEM (e.g. "150")		: Grid size for concentration output reconstruction (m)
#OCEAN_MODEL DEFAULT=001 (Dropdownlist: 1) POSEIDON High resolution Aegean Model - value "001",2) POSEIDON Mediterranean Model - value "002") 		: Ocean forcing requested (three-digit number, see table 1)
#WIND_MODEL DEFAULT=101	 (Dropdownlist 1 option only: 1) POSEIDON ETA weather forecasting system - value "101")		: Atmospheric forcing requested (three-digit number, see table 2)
#WAVE_MODEL DEFAULT=201	(Dropdownlist: 1) POSEIDON WAM Cycle 4 for the Mediterranean - value "201",2) POSEIDON WAM Cycle 4 for the Aegean - value "202") 			: Wave forcing requested (three-digit number, see table 3)

#Example http://localhost:8000/requests/api/createInputFileForHCMRSpillSimulator/?LATLON=37.3778%2025.9595&DATETIME=2017%2012%2027%201000&VOLUME=2500
# @login_required
def APIcreateInputFileForHCMRSpillSimulator(request):
    if request.method == 'GET':
        print(request.GET)
        if 'LATLON0' in request.GET and 'DATETIME0' in request.GET and 'VOLUME0' in request.GET:
            #Initialisation with defaults or GET parameters
            N_SPILL = "1"
            SPILL_NUM = 1
            LATLON = request.GET['LATLON0']
            if 'DEPTH0' in request.GET:
                DEPTH = request.GET['DEPTH0']
            else:
                DEPTH = "0"
            DATETIME = request.GET['DATETIME0']
            if 'DURATION0' in request.GET:
                DURATION = request.GET['DURATION0']
            else:
                DURATION = "0"
            VOLUME = request.GET['VOLUME0']
            SIMULATIONNAME = "USER" + str(request.user.id) + "BDO"
            SPILL_NUM, point_info_list = find_additional_point_info(SPILL_NUM, request)

            if 'DENSITYOILTYPE' in request.GET:
                DENSITYOILTYPE = request.GET['DENSITYOILTYPE']
            else:
                DENSITYOILTYPE = "920.0"
            SIM_TYPE = "FORWARD"
            if 'SIM_LENGTH' in request.GET:
                SIM_LENGTH = request.GET['SIM_LENGTH']
            else:
                SIM_LENGTH = "48"
            if 'STEP' in request.GET:
                STEP = request.GET['STEP']
            else:
                STEP = "2"
            GRD_SIZE = "150"
            if 'OCEAN_MODEL' in request.GET:
                OCEAN_MODEL = request.GET['OCEAN_MODEL']
            else:
                OCEAN_MODEL = "001"
            if 'WIND_MODEL' in request.GET:
                WIND_MODEL = request.GET['WIND_MODEL']
            else:
                WIND_MODEL = "101"
            if 'WAVE_MODEL' in request.GET:
                WAVE_MODEL = request.GET['WAVE_MODEL']
            else:
                WAVE_MODEL = "201"

            #Create the file input in string format
            OilSpillInputString = build_oil_spill_input_string(DATETIME, DENSITYOILTYPE, DEPTH, DURATION, GRD_SIZE,
                                                               LATLON, N_SPILL, OCEAN_MODEL, SIMULATIONNAME, SIM_LENGTH,
                                                               SIM_TYPE, str(SPILL_NUM), STEP, VOLUME, WAVE_MODEL,
                                                               WIND_MODEL, point_info_list)
            print 'InputString:{0}'.format(OilSpillInputString)
            FTPSERVER, FTPUSERNAME, FTPPASS = 'tethys.hcmr.gr', 'bdo', '!p1l0t2#'

            #Save Oil Spill Simulation input string to a text file in ftp
            ftp = ftplib.FTP(FTPSERVER)
            ftp.login(FTPUSERNAME, FTPPASS)
            print 'Logged In'
            ftp.cwd('/in/')
            print 'Changed wd'
            #Convert e.g. "2017 12 27 1000" to "171227_1000"
            LATLONNAME = LATLON.replace(".","_").replace(" ","__")
            FILEDATETIME = DATETIME[2:4] + DATETIME[5:7] + DATETIME[8:10]+ "_" + DATETIME[11:15]
            #filename format xxxxyymmdd_hhmmZZ.inp
            #where
            #xxxx is name of the simulation chosen by the user;
            #yymmdd is the date of the spill;
            #hhmm the time of the spill;
            #ZZ is _F for a forecast and _H for a hindcast.
            filename = LATLONNAME +  SIMULATIONNAME + FILEDATETIME + '_F.inp'
            binaryofInput = io.BytesIO(OilSpillInputString.encode())
            ftp.storbinary('STOR ' + filename, binaryofInput)
            print 'File Stored'
            ftp.quit()
            # return HttpResponse("***"+filename+"***")
            return HttpResponse(json.dumps({"filename": str(filename)}), content_type="application/json")
        else:
            return HttpResponse('LATLON, DATETIME, and VOLUME are required', status=400)


def find_additional_point_info(SPILL_NUM, request):
    point_info_list = []
    for i in range(1, 5):
        point_info = {}
        try:
            point_info['LATLON'] = latloni = request.GET['LATLON' + str(i)]
        except MultiValueDictKeyError:
            break
        SPILL_NUM += 1
        if latloni == '':
            break
        if ('DEPTH' + str(i)) in request.GET:
            point_info['DEPTH'] = request.GET['DEPTH' + str(i)]
        else:
            point_info['DEPTH'] = "0"
        point_info['DATETIME'] = request.GET['DATETIME' + str(i)]
        if 'DURATION' + str(i) in request.GET:
            point_info['DURATION'] = request.GET['DURATION' + str(i)]
        else:
            point_info['DURATION'] = "0"
        point_info['VOLUME'] = request.GET['VOLUME' + str(i)]
        point_info['SIMULATIONNAME'] = "USER" + str(request.user.id) + "BDO"
        point_info_list.append(point_info)
    return SPILL_NUM, point_info_list


def build_polygon_string(LATLON, LATLON2):
    lat1, lon1 = LATLON.split(' ')
    lat2, lon2 = LATLON2.split(' ')
    result = LATLON + '\n' + lat1 +' '+ lon2+'\n'+LATLON2+'\n'+ lat2+ ' '+ lon1+ '\n'

    return result

def build_oil_spill_input_string(DATETIME, DENSITYOILTYPE, DEPTH, DURATION, GRD_SIZE, LATLON, N_SPILL, OCEAN_MODEL,
                                 SIMULATIONNAME, SIM_LENGTH, SIM_TYPE, SPILL_NUM, STEP, VOLUME, WAVE_MODEL, WIND_MODEL,
                                 point_list):
    latlon1 = str(LATLON)
    inp_string = SPILL_NUM + "\n" + \
                          '1' + "\n" + \
                          latlon1 + "\n" + \
                          DEPTH + "\n" + \
                          DATETIME + "\n" + \
                          DURATION + "\n" + \
                          VOLUME + "\n"
    idx = 1
    if point_list != '':
        for p in point_list:
            idx += 1
            inp_string += str(idx) + "\n" + \
                              str(p['LATLON']) + "\n" + \
                              str(p['DEPTH']) + "\n" + \
                              str(p['DATETIME']) + "\n" + \
                              str(p['DURATION'])+ "\n" + \
                              str(p['VOLUME']) + "\n"

    inp_string += SIMULATIONNAME + "\n" + \
                          DENSITYOILTYPE + "\n" + \
                          SIM_TYPE + "\n" + \
                          SIM_LENGTH + "\n" + \
                          STEP + "\n" + \
                          GRD_SIZE + "\n" + \
                          OCEAN_MODEL + "\n" + \
                          WIND_MODEL + "\n" + \
                          WAVE_MODEL + "\n"
    return inp_string


#Check if an output for the same user and date exists
#example http://localhost:8000/requests/api/checkIfOutputExistsforHCMRSpillSimulator/?LATLON=37.3778%2025.9595&DATETIME=2017%2012%2027%201000&VOLUME=2500
# @login_required
def APIcheckIfOutputExistsforHCMRSpillSimulator(request):
    if request.method == 'GET':
        if 'LATLON0' in request.GET and 'DATETIME0' in request.GET:
            LATLON = request.GET['LATLON0']
            DATETIME = request.GET['DATETIME0']

            FTPSERVER, FTPUSERNAME, FTPPASS = 'tethys.hcmr.gr','bdo', '!p1l0t2#'

            # Check the out directory
            ftp = ftplib.FTP(FTPSERVER)
            ftp.login(FTPUSERNAME, FTPPASS)
            ftp.cwd('/out/')
            # Convert "2017 12 27 1000" to "171227_1000"
            LATLONNAME = LATLON.replace(".", "_").replace(" ", "__")
            SIMULATIONNAME = "USER" + str(request.user.id) + "BDO"
            FILEDATETIME = DATETIME[2:4] + DATETIME[5:7] + DATETIME[8:10] + "_" + DATETIME[11:15]
            filenameToSearchFor = LATLONNAME + SIMULATIONNAME + FILEDATETIME + '_F.out'
            if filenameToSearchFor in ftp.nlst():
                #change temp file
                inputfile = open("service_builder/static/services_files/hcmr_service_1/" + filenameToSearchFor, 'wb')
                ftp.retrbinary('RETR ' + filenameToSearchFor, inputfile.write, 1024)
                #Parsing of inputfile
                #.............
                ftp.quit()
                inputfile.close()
                return HttpResponse('True')
            else:
                ftp.quit()
                return HttpResponse('False', status=300)

        else:
            return HttpResponse('DATETIME AND LATLON are required', status=400)


# ----------END OF HCMR Dummy Service -------------------------------------------------------------------#
