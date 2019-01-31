# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections, json
from threading import Thread
from background_task import background
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from aggregator.models import Variable, Dataset
from lists import *
from datasets import *

from query_designer.models import Query, TempQuery, AbstractQuery
from service_builder.models import Service, ServiceInstance
from visualizer.utils import delete_zep_notebook, clone_zep_note, create_zep_arguments_paragraph, delete_zep_paragraph, run_zep_note, \
    get_result_dict_from_livy, create_zep_getDict_paragraph, run_zep_paragraph, get_zep_getDict_paragraph_response, close_livy_session, \
    create_livy_session


def configure_spatial_filter(filters, lat_from, lat_to, lon_from, lon_to):
    if type(filters) == dict:
        if 'op' in filters.keys() and filters['op'] == 'inside_rect':
            filters['b'] = '<<{0},{1}>,<{2},{3}>>'.format(lat_from, lon_from, lat_to, lon_to)
        else:
            filters['a'] = configure_spatial_filter(filters['a'], lat_from, lat_to, lon_from, lon_to)
            filters['b'] = configure_spatial_filter(filters['b'], lat_from, lat_to, lon_from, lon_to)
    return filters


def configure_temporal_filter(filters, start_date, end_date):
    if type(filters) == dict:
        if 'op' in filters.keys() and filters['op'] == 'lte_time':
            filters['b'] = "'{0}'".format(end_date)
        elif 'op' in filters.keys() and filters['op'] == 'gte_time':
            filters['b'] = "'{0}'".format(start_date)
        else:
            filters['a'] = configure_temporal_filter(filters['a'], start_date, end_date)
            filters['b'] = configure_temporal_filter(filters['b'], start_date, end_date)
    return filters


def find_visualization_variables(variables, query_id):
    return_variables = list()
    doc = AbstractQuery.objects.get(pk=query_id).document
    for var in variables:
        variable_dict = dict({'variable': var, 'query_variable': None, 'title': None, 'unit': None, 'variable_id': None})
        for _f in doc['from']:
            if str(_f['select'][0]['name'])[int(str(_f['select'][0]['name']).find('_'))+1:] == var:
                variable_dict['query_variable'] = _f['select'][0]['name']
                variable_dict['title'] = Variable.objects.get(pk=int(_f['type'])).title
                variable_dict['unit'] = Variable.objects.get(pk=int(_f['type'])).unit
                variable_dict['variable_id'] = _f['type']
        return_variables.append(variable_dict)
    return return_variables


def get_query_aggregates(query_id, var):
    temp_q = TempQuery(document=AbstractQuery.objects.get(pk=query_id).document)
    new_from = []
    for agg in ['min', 'max', 'avg']:
        for _f in temp_q.document['from']:
            if int(_f['type']) == int(var['variable_id']):
                new_select = dict()
                for key in _f['select'][0].keys():
                    new_select[key] = _f['select'][0][key]
                new_select['name'] = new_select['name']
                new_select['aggregate'] = agg
                new_from.append({'select': [new_select], 'type': _f['type'], 'name': _f['name']})
    temp_q.document['from'] = new_from

    # for _f in temp_q.document['from']:
    #     if int(_f['type']) == int(var['variable_id']):
    #         _f['select'][0]['exclude'] = False
    #         _f['select'][0]['aggregate'] = aggregate
    #         _f['select'][0]['groupBy'] = False
    #         for _s in _f['select'][1:]:
    #             _s['exclude'] = True
    #             _s['groupBy'] = False
    #     else:
    #         for _s in _f['select']:
    #             _s['exclude'] = True
    #             _s['groupBy'] = False

    results = temp_q.execute()[0]['results']
    if len(results) > 0:
        result = results[0][0], results[0][1], results[0][2]
    else:
        result = '-', '-', '-'
    return result


def convert_unicode_json(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_unicode_json, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_unicode_json, data))
    else:
        return data


def gather_service_args(service_args, request, service_exec):
    args_to_note = dict()
    for arg in service_args:
        args_to_note[arg] = request.GET[arg]
    print 'user algorithm args:'
    print args_to_note
    service_exec.arguments = args_to_note
    service_exec.save()
    return args_to_note


def get_query_with_updated_filters(request, query_id):
    # dataset_id = request.GET["dataset_id"]
    # original_query_id = settings.LOCATION_EVALUATION_SERVICE_DATASET_QUERY[dataset_id]

    query_doc = Query.objects.get(pk=query_id).document
    query_doc['filters'] = configure_spatial_filter(query_doc['filters'], request.GET["latitude_from"], request.GET["latitude_to"],
                                                    request.GET["longitude_from"], request.GET["longitude_to"])
    query_doc['filters'] = configure_temporal_filter(query_doc['filters'], request.GET["start_date"], request.GET["end_date"])
    print "Updated Filters:"
    print query_doc['filters']
    new_query = TempQuery(document=query_doc, user=request.user)
    new_query.save()
    return new_query.id


def clone_service_note(request, service, service_exec):
    original_notebook_id = service.notebook_id
    if 'notebook_id' in request.GET.keys():
        new_notebook_id = request.GET['notebook_id']
    else:
        new_notebook_id = clone_zep_note(original_notebook_id, "")
    service_exec.notebook_id = new_notebook_id
    service_exec.save()
    print 'Notebook ID: {0}'.format(new_notebook_id)
    return new_notebook_id


def create_args_paragraph(request, new_notebook_id, args_to_note, service):
    if 'args_paragraph' in request.GET.keys():
        new_arguments_paragraph = request.GET['args_paragraph']
    else:
        new_arguments_paragraph = create_zep_arguments_paragraph(notebook_id=new_notebook_id, title='',
                                                                 args_json_string=json.dumps(args_to_note))
        if service.arguments_paragraph_id is not None:
            delete_zep_paragraph(new_notebook_id, service.arguments_paragraph_id)
    return new_arguments_paragraph


def create_service_livy_session(request, service_exec):
    if 'livy_session' in request.GET.keys():
        livy_session = request.GET['livy_session']
    else:
        # livy_session = run_zep_note(notebook_id=new_notebook_id, exclude=excluded_paragraphs, mode='livy')
        livy_session = create_livy_session(service_exec.notebook_id)
    service_exec.livy_session = livy_session
    service_exec.save()
    return livy_session


def execute_service_code(request, service_exec, new_arguments_paragraph):
    paragraph_list = [(new_arguments_paragraph, 'gathering user arguments')]
    for p in settings.LOCATION_EVALUATION_SERVICE_PARAGRAPHS:
        paragraph_list.append((p['paragraph'], p['status']))

    for paragraph, status in paragraph_list:
        print 'executing paragraph: ' + paragraph
        service_exec.status = status
        service_exec.save()
        if 'no_exec' in request.GET.keys():
            pass
        else:
            run_zep_paragraph(service_exec.notebook_id, paragraph, service_exec.livy_session, 'livy')


# @background(schedule=600)
def clean_up_new_note(notebook_id):
    delete_zep_notebook(notebook_id)


def init(request):
    return render(request, 'wave_energy_pilot/load_service.html', {'buoys_list': BUOYS, 'datasets_list': DATASETS})


def data_visualization_results(request):
    service = Service.objects.get(pk=settings.LOCATION_EVALUATION_SERVICE_ID)
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now(),
                                   status="starting service", dataframe_visualizations=[])
    # service_exec.save()
    # print

    start_date = request.GET["start_date"]
    end_date = request.GET["end_date"]
    latitude_from = float(request.GET["latitude_from"])
    latitude_to = float(request.GET["latitude_to"])
    longitude_from = float(request.GET["longitude_from"])
    longitude_to = float(request.GET["longitude_to"])


    dataset_id = request.GET["dataset_id"]
    query_id = settings.DATA_VISUALISATION_SERVICE_DATASET_QUERY[dataset_id]
    visualization_query_id = get_query_with_updated_filters(request, query_id)

    variables_selection = request.GET.getlist("variables[]")
    variable_list = find_visualization_variables(variables_selection, visualization_query_id)

    y_var = ""
    base_string = "y_var[]="
    for variable in variable_list:
        y_var += base_string + str(variable['query_variable']) + "&"

    visualizations = dict()
    visualizations['v1'] = ({'notebook_id': '',
                             'df': '',
                             'query': visualization_query_id,
                             'title': "Time Series Graph",
                             'url': "/visualizations/get_line_chart_am/?"+y_var+"x_var=i0_time&agg_func=AVG&query="+str(visualization_query_id),
                             'done': False})
    service_exec.dataframe_visualizations = visualizations
    service_exec.save()

    result = dict()
    for var in variable_list:
        result[str(var['variable'])] = dict()
        result[str(var['variable'])]['title'] = str(var['title'])
        result[str(var['variable'])]['unit'] = str(var['unit'])
        min, max, avg = get_query_aggregates(visualization_query_id, var)
        result[str(var['variable'])]['min'] = min
        result[str(var['variable'])]['max'] = max
        result[str(var['variable'])]['avg'] = avg

    variable_list_with_commas = ''
    for var in variable_list:
        variable_list_with_commas += var['title'] + ', '
    variable_list_with_commas = variable_list_with_commas[:-2]

    dataset_title = Dataset.objects.get(pk=dataset_id).title
    location_lat = str(latitude_from + abs(latitude_to-latitude_from)/2)
    location_lon = str(longitude_from + abs(longitude_to - longitude_from) / 2)

    return render(request, 'wave_energy_pilot/data_visualisation result.html',
                  {'result': result,
                   'service_title': 'Visualisation of a single data source',
                   'study_conditions': [
                       {'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):', 'value': '('+location_lat+', '+location_lon+') +/- 10 degrees'},
                       {'icon': 'far fa-calendar-alt', 'text': 'Timeframe:', 'value': 'from '+ str(start_date) + ' to ' + str(end_date)},
                       {'icon': 'fas fa-database', 'text': 'Dataset used:',
                        'value': str(dataset_title) + ' <a target="_blank" rel="noopener noreferrer"  href="/datasets/'+str(dataset_id)+'/" style="color: #1d567e;text-decoration: underline">(more info)</a>'},
                       {'icon': 'fas fa-info-circle', 'text': 'Selected variables:', 'value': str(variable_list_with_commas)}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


def single_location_evaluation_execute(request):
    service = Service.objects.get(pk=settings.LOCATION_EVALUATION_SERVICE_ID)
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now(),
                                   status="starting service", dataframe_visualizations=[])
    service_exec.save()
    # Spawn thread to process the data
    t = Thread(target=single_location_evaluation_execution_process, args=(request, service_exec.id))
    t.start()
    return JsonResponse({'exec_instance': service_exec.id})


def single_location_evaluation_execution_process(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    service = Service.objects.get(pk=service_exec.service_id)
    # GATHER THE SERVICE ARGUMENTS
    service_args = ["start_date", "end_date", "latitude_from", "latitude_to", "longitude_from", "longitude_to"]
    args_to_note = gather_service_args(service_args, request, service_exec)
    # CONFIGURE THE QUERY TO BE USED
    wave_height_query_id = get_query_with_updated_filters(request)
    # CLONE THE SERVICE NOTE
    new_notebook_id = clone_service_note(request, service, service_exec)
    # ADD THE VISUALISATIONS TO BE CREATED
    visualisations = dict()
    visualisations['v1'] = ({'notebook_id': '',
                             'df': '',
                             'query': wave_height_query_id,
                             'title': "Sea surface wave significant height",
                             'url': "/visualizations/get_line_chart_am/?y_var[]=i0_sea_surface_wave_significant_height&x_var=i0_time&query="+str(wave_height_query_id),
                             'done': False})
    visualisations['v2'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'title': "Wave period",
                             'url': "/visualizations/get_line_chart_am/?y_var[]=avg(power)&x_var=time&df=power_df&notebook_id="+str(new_notebook_id),
                             'done': False})
    visualisations['v3'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'title': "Power histogram",
                             'url': "/visualizations/get_histogram_chart_am/?bins=5&x_var=avg(power)&df=power_df&notebook_id="+str(new_notebook_id),
                             'done': False})
    service_exec.dataframe_visualizations = visualisations
    service_exec.save()
    # CREATE NEW ARGUMENTS PARAGRAPH
    new_arguments_paragraph = create_args_paragraph(request, new_notebook_id, args_to_note, service)
    # CREATE A LIVY SESSION
    service_exec.status = "Initializing Spark Session"
    service_exec.save()
    livy_session = create_service_livy_session(request, service_exec)
    try:
        # RUN THE SERVICE CODE
        execute_service_code(request, service_exec, new_arguments_paragraph)
        service_exec.status = "done"
        service_exec.save()

    except Exception as e:
        print 'exception in livy execution'
        print '%s (%s)' % (e.message, type(e))
        service_exec.status = "failed"
        service_exec.save()
        # clean_up_new_note(service_exec.notebook_id)
        if 'livy_session' in request.GET.keys():
            pass
        else:
            if service_exec.service.through_livy:
                close_livy_session(service_exec.livy_session)


def single_location_evaluation_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    # GET THE SERVICE RESULTS
    result = get_result_dict_from_livy(service_exec.livy_session, 'result')
    print 'result: ' + str(result)
    # clean_up_new_note(service_exec.notebook_id)

    # SHOW THE SERVICE OUTPUT PAGE
    return render(request, 'wave_energy_pilot/location_assessment result.html',
                  {'result': result,
                   'service_title': 'Wave Energy - Evaluation of a single location',
                   'study_conditions': [
                       {'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):', 'value': '(35.1, -11.3) +/- 10 degrees'},
                       {'icon': 'fas fa-database', 'text': 'Dataset used:',
                        'value': 'Nester Maretec Waves Forecast <a target="_blank" rel="noopener noreferrer"  href="/datasets/111/" style="color: #1d567e;text-decoration: underline">(more info)</a>'}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


def single_location_evaluation_status(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    return JsonResponse({'status': service_exec.status})


def wave_forecast_execute(request):
    service = Service.objects.get(pk=settings.WAVE_FORECAST_SERVICE_ID)
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now(),
                                   status="starting service", dataframe_visualizations=[])
    service_exec.save()
    # Spawn thread to process the data
    t = Thread(target=wave_forecast_execution_process, args=(request, service_exec.id))
    t.start()
    return JsonResponse({'exec_instance': service_exec.id})


def wave_forecast_execution_process(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    service = Service.objects.get(pk=service_exec.service_id)
    # GATHER THE SERVICE ARGUMENTS
    service_args = ["start_date", "end_date", "latitude_from", "latitude_to", "longitude_from", "longitude_to"]
    args_to_note = gather_service_args(service_args, request, service_exec)
    # CONFIGURE THE QUERY TO BE USED
    wave_forecast_query_id = get_query_with_updated_filters(request)
    # CLONE THE SERVICE NOTE
    new_notebook_id = clone_service_note(request, service, service_exec)
    # ADD THE VISUALISATIONS TO BE CREATED
    visualisations = dict()
    visualisations['v1'] = ({'notebook_id': '',
                             'df': '',
                             'query': wave_forecast_query_id,
                             'url': "/visualizations/get_line_chart_am/?y_var[]=i0_sea_surface_wave_significant_height&x_var=i0_time&query="+str(wave_forecast_query_id),
                             'done': False,
                             'title': 'Wave significant height'})
    visualisations['v2'] = ({'notebook_id': '',
                             'df': '',
                             'query': wave_forecast_query_id,
                             'url': "/visualizations/get_line_chart_am/?y_var[]=i1_sea_surface_wave_zero_upcrossing_period&x_var=i0_time&query=" + str(
                                 wave_forecast_query_id),
                             'done': False,
                             'title': 'Wave mean period'})
    visualisations['v3'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'url': "/visualizations/get_line_chart_am/?y_var[]=avg(power)&x_var=time&df=power_df&notebook_id="+str(new_notebook_id),
                             'done': False,
                             'title': 'Wave Energy'})
    service_exec.dataframe_visualizations = visualisations
    service_exec.save()
    # CREATE NEW ARGUMENTS PARAGRAPH
    new_arguments_paragraph = create_args_paragraph(request, new_notebook_id, args_to_note, service)
    # CREATE A LIVY SESSION
    service_exec.status = "Initializing Spark Session"
    service_exec.save()
    livy_session = create_service_livy_session(request, service_exec)
    try:
        # RUN THE SERVICE CODE
        execute_service_code(request, service_exec, new_arguments_paragraph)
        service_exec.status = "done"
        service_exec.save()

    except Exception as e:
        print 'exception in livy execution'
        print '%s (%s)' % (e.message, type(e))
        service_exec.status = "failed"
        service_exec.save()
        # clean_up_new_note(service_exec.notebook_id)
        if 'livy_session' in request.GET.keys():
            pass
        else:
            if service_exec.service.through_livy:
                close_livy_session(service_exec.livy_session)


def wave_forecast_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    # GET THE SERVICE RESULTS
    result = get_result_dict_from_livy(service_exec.livy_session, 'result')
    print 'result: ' + str(result)
    # clean_up_new_note(service_exec.notebook_id)

    # SHOW THE SERVICE OUTPUT PAGE
    return render(request, 'wave_energy_pilot/wave_forecast result.html',
                  {'result': result,
                   'service_title': 'Wave Energy - Wave forecast in a location',
                   'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):', 'value': '(35.1, -11.3) +/- 10 degrees'},
                                        {'icon': 'fas fa-database', 'text': 'Dataset used:', 'value': 'Nester Maretec Waves Forecast <a target="_blank" rel="noopener noreferrer"  href="/datasets/111/" style="color: #1d567e;text-decoration: underline">(more info)</a>'}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


def wave_forecast_status(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    return JsonResponse({'status': service_exec.status})
