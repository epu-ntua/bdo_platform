# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections, json
from threading import Thread, Timer
from background_task import background
from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from aggregator.models import Variable, Dataset
from lists import *
from datasets import *
from energy_converters import *

from query_designer.models import Query, TempQuery, AbstractQuery
from service_builder.models import Service, ServiceInstance
from visualizer.utils import delete_zep_notebook, clone_zep_note, create_zep_arguments_paragraph, delete_zep_paragraph, run_zep_note, \
    get_result_dict_from_livy, create_zep_getDict_paragraph, run_zep_paragraph, get_zep_getDict_paragraph_response, close_livy_session, \
    create_livy_session
from time import sleep

from wave_energy_pilot.models import Wave_Energy_Converters


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
            new_select_list = list()
            if int(_f['type']) == int(var['variable_id']):
                new_select = dict()
                for key in _f['select'][0].keys():
                    new_select[key] = _f['select'][0][key]
                new_select['name'] = new_select['name']
                new_select['aggregate'] = agg
                new_select_list.append(new_select)
                for _s in _f['select'][1:]:
                    _s['exclude'] = True
                    # _s['aggregate'] = 'AVG'
                    _s['groupBy'] = False
                    _s.pop('joined', None)
                    new_select_list.append(_s)
                new_from.append({'select': new_select_list, 'type': _f['type'], 'name': _f['name']})
            else:
                for _s in _f['select']:
                    if _s['type'] == "VALUE":
                        _s['exclude'] = True
                        _s['groupBy'] = False
                    else:
                        _s['exclude'] = True
                        # _s['aggregate'] = 'AVG'
                        _s['groupBy'] = False
                new_from.append(_f)

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


def gather_service_args(service_args, request, service_exec, method='get'):
    args_to_note = dict()
    for arg in service_args:
        if method == 'get':
            args_to_note[arg] = request.GET[arg]
        else:
            args_to_note[arg] = request.POST[arg]
    print 'user algorithm args:'
    print args_to_note
    service_exec.arguments = args_to_note
    service_exec.save()
    return args_to_note


def get_query_with_updated_filters(request, query_id, method='get'):
    # dataset_id = request.GET["dataset_id"]
    # original_query_id = settings.LOCATION_EVALUATION_SERVICE_DATASET_QUERY[dataset_id]

    query_doc = Query.objects.get(pk=query_id).document
    if method == 'get':
        query_doc['filters'] = configure_spatial_filter(query_doc['filters'], request.GET["latitude_from"], request.GET["latitude_to"],
                                                        request.GET["longitude_from"], request.GET["longitude_to"])
        query_doc['filters'] = configure_temporal_filter(query_doc['filters'], request.GET["start_date"], request.GET["end_date"])
    else:
        query_doc['filters'] = configure_spatial_filter(query_doc['filters'], request.POST["latitude_from"], request.POST["latitude_to"],
                                                        request.POST["longitude_from"], request.POST["longitude_to"])
        query_doc['filters'] = configure_temporal_filter(query_doc['filters'], request.POST["start_date"], request.POST["end_date"])

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


def execute_service_code(request, service_exec, new_arguments_paragraph, paragraphs):
    paragraph_list = [(new_arguments_paragraph, 'gathering user arguments')]
    for p in paragraphs:
        paragraph_list.append((p['paragraph'], p['status']))

    for paragraph, status in paragraph_list:
        print 'executing paragraph: ' + paragraph
        service_exec.status = status
        service_exec.save()
        if 'no_exec' in request.GET.keys():
            pass
        else:
            if service_exec.service.through_livy:
                run_zep_paragraph(service_exec.notebook_id, paragraph, service_exec.livy_session, 'livy')
            else:
                run_zep_paragraph(service_exec.notebook_id, paragraph, service_exec.livy_session, 'zeppelin')


def clean_up_new_note(notebook_id, wait_time_seconds=0):
    print "waiting to clean up note " + str(notebook_id)
    sleep(wait_time_seconds)
    print "cleaning up note: " + str(notebook_id)
    delete_zep_notebook(notebook_id)


def wec_creation(request):
    # import pdb
    # pdb.set_trace()
    new_wec = json.loads(request.GET['wec_data'])
    print new_wec

    converter = Wave_Energy_Converters(
        title=new_wec['title'],
        image_uri='',
        min_height=new_wec['min_height'],
        max_height=new_wec['max_height'],
        min_energy_period=new_wec['min_energy_period'],
        max_energy_period=new_wec['max_energy_period'],
        sample_rows=new_wec['data'],
        owner_id=request.user
    )
    converter.save()
    return JsonResponse({'id': converter.id})


@never_cache
def energy_conversion_init(request):
    execution_steps = dict()
    execution_steps['WEC_LOCATION_EVALUATION_SERVICE'] = ['starting service', 'Initializing Spark Session'] + \
                                                         [x['status'] for x in settings.WEC_LOCATION_EVALUATION_SERVICE_PARAGRAPHS] + \
                                                         ['done']
    execution_steps['WEC_GENERATION_FORECAST_SERVICE'] = ['starting service', 'Initializing Spark Session'] + \
                                                         [x['status'] for x in settings.WEC_LOCATION_EVALUATION_SERVICE_PARAGRAPHS] + \
                                                         ['done']
    execution_steps['WEC_AREA_EVALUATION_SERVICE'] = ['starting service', 'Initializing Spark Session'] +\
                                                     [x['status'] for x in settings.WEC_LOCATION_EVALUATION_SERVICE_PARAGRAPHS] + \
                                                     ['done']
    execution_steps['WEC_LOAD_MATCHING_SERVICE'] = ['starting service', 'Initializing Spark Session'] +\
                                                   [x['status'] for x in settings.WEC_LOAD_MATCHING_SERVICE_PARAGRAPHS] + \
                                                   ['done']
    energy_converters = Wave_Energy_Converters.objects.filter(Q(owner_id=User.objects.get(username='BigDataOcean')) | Q(owner_id=request.user))
    return render(request, 'wave_energy_pilot/energy_conversion_service.html',
                  {'datasets_list': DATASETS,
                   'energy_converters': energy_converters,
                   'data_radius': DATA_RADIUS,
                   'execution_steps': execution_steps})


@never_cache
def wec_single_location_evaluation_execute(request):
    service = Service.objects.get(pk=settings.WEC_LOCATION_EVALUATION_SERVICE_ID)
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now(),
                                   status="starting service", dataframe_visualizations=[])
    service_exec.save()
    # Spawn thread to process the data
    t = Thread(target=wec_single_location_evaluation_execution_process, args=(request, service_exec.id))
    t.start()
    return JsonResponse({'exec_instance': service_exec.id})


def wec_single_location_evaluation_execution_process(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    service = Service.objects.get(pk=service_exec.service_id)
    # GATHER THE SERVICE ARGUMENTS
    service_args = ["start_date", "end_date", "latitude_from", "latitude_to", "longitude_from", "longitude_to", "dataset_id"]
    args_to_note = gather_service_args(service_args, request, service_exec)
    converters_selection = request.GET.getlist("converters[]")
    wecs = list()
    for converter_id in converters_selection:
        aWec = dict()
        converter = Wave_Energy_Converters.objects.get(pk=int(converter_id))
        aWec['name'] = converter.title
        aWec['min_H'] = str(int(round(converter.min_height, 0)))
        aWec['max_H'] = str(int(round(converter.max_height)))
        aWec['min_T'] = str(int(round(converter.min_energy_period)))
        aWec['max_T'] = str(int(round(converter.max_energy_period)))
        aWec['wec_matrix'] = converter.sample_rows
        wecs.append(aWec)
    args_to_note['wecs'] = wecs
    service_exec.arguments = args_to_note
    service_exec.save()
    # new conv
    # Wave_Energy_Converters(title=conv['title'], owner_id=User.objects.get(pk=4), image_uri='', sample_rows=conv['data'],
    #                        min_height=conv['min_height'], max_height=conv['max_height'], min_energy_period=conv['min_energy_period'],
    #                        max_energy_period=conv['max_energy_period']).save()
    # CONFIGURE THE QUERY TO BE USED
    dataset_id = str(request.GET["dataset_id"])
    query_id = settings.WEC_LOCATION_EVALUATION_SERVICE_DATASET_QUERY[dataset_id]
    wave_height_query_id = get_query_with_updated_filters(request, query_id)
    # CLONE THE SERVICE NOTE
    new_notebook_id = clone_service_note(request, service, service_exec)
    # ADD THE VISUALISATIONS TO BE CREATED
    visualisations = dict()
    power_cols_str = ''
    cap_factors_cols_str = ''
    for i, converter_id in enumerate(converters_selection):
        converter = Wave_Energy_Converters.objects.get(pk=int(converter_id))
        power_cols_str += '&y_var[]=power for ' + str(converter.title) + '&y_var_unit[]=kW/m'
        cap_factors_cols_str += '&y_var[]=capacity factor for ' + str(converter.title) + '&y_var_unit[]=%'

    visualisations['v1'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'title': "Generated Power",
                             'url': "/visualizations/get_line_chart_am/?x_var=time&df=power_df&notebook_id=" + str(
                                 new_notebook_id) + power_cols_str,
                             'done': False})
    visualisations['v2'] = ({'notebook_id': new_notebook_id,
                             'df': 'wec_cap_factors_df',
                             'query': '',
                             'title': "Capacity Factor",
                             'url': "/visualizations/get_line_chart_am/?x_var=time&df=wec_cap_factors_df&notebook_id=" + str(
                                 new_notebook_id) + cap_factors_cols_str,
                             'done': False})
    service_exec.dataframe_visualizations = visualisations
    service_exec.save()
    # CREATE NEW ARGUMENTS PARAGRAPH
    new_arguments_paragraph = create_args_paragraph(request, new_notebook_id, args_to_note, service)
    # CREATE A LIVY SESSION
    if service.through_livy:
        service_exec.status = "Initializing Spark Session"
        service_exec.save()
        service_exec.livy_session = create_service_livy_session(request, service_exec)
        service_exec.save()
    try:
        # RUN THE SERVICE CODE
        execute_service_code(request, service_exec, new_arguments_paragraph, settings.WEC_LOCATION_EVALUATION_SERVICE_PARAGRAPHS)
        service_exec.status = "done"
        service_exec.save()
        t = Thread(target=clean_up_new_note, args=(str(new_notebook_id), 180))
        t.start()
    except Exception as e:
        print 'exception in livy execution'
        print '%s (%s)' % (e.message, type(e))
        service_exec.status = "failed"
        service_exec.save()
        clean_up_new_note(service_exec.notebook_id)
        if 'livy_session' in request.GET.keys():
            pass
        else:
            if service_exec.service.through_livy:
                close_livy_session(service_exec.livy_session)


@never_cache
def wec_single_location_evaluation_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    # GET THE SERVICE RESULTS
    result = get_result_dict_from_livy(service_exec.livy_session, 'result')
    print 'result: ' + str(result)
    # clean_up_new_note(service_exec.notebook_id)

    dataset_id = str(result['dataset_id'])
    dataset_title = str(Dataset.objects.get(pk=dataset_id))
    location_lat = str(result['location_lat'])
    location_lon = str(result['location_lon'])
    start_date = str(result['start_date'])
    end_date = str(result['end_date'])
    converters = [str(name) for name in result['name']]

    # SHOW THE SERVICE OUTPUT PAGE
    return render(request, 'wave_energy_pilot/wec_location_assessment result.html',
                  {'result': result,
                   'back_url': '/wave-energy/energy_conversion/',
                   'service_title': 'Wave Energy - Assessment of Wave Energy Converters in a Single Location',
                   'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):','value': '(' + location_lat + ', ' + location_lon + ') +/- 1 degree'},
                                        {'icon': 'far fa-calendar-alt', 'text': 'Timeframe:','value': 'from ' + str(start_date) + ' to ' + str(end_date)},
                                        {'icon': 'fas fa-database', 'text': 'Dataset used:', 'value': str(dataset_title) + ' <a target="_blank" rel="noopener noreferrer"  href="/datasets/' + str(dataset_id) + '/" style="color: #1d567e;text-decoration: underline">(more info)</a>'},
                                        {'icon': 'fas fa-water', 'text': 'WEC technologies:', 'value': str(converters)}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


@never_cache
def wec_area_evaluation_execute(request):
    service = Service.objects.get(pk=settings.WEC_AREA_EVALUATION_SERVICE_ID)
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now(),
                                   status="starting service", dataframe_visualizations=[])
    service_exec.save()
    # Spawn thread to process the data
    t = Thread(target=wec_area_evaluation_execution_process, args=(request, service_exec.id))
    t.start()
    return JsonResponse({'exec_instance': service_exec.id})


def wec_area_evaluation_execution_process(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    service = Service.objects.get(pk=service_exec.service_id)
    # GATHER THE SERVICE ARGUMENTS
    service_args = ["latitude_from", "latitude_to", "longitude_from", "longitude_to"]
    args_to_note = gather_service_args(service_args, request, service_exec)
    converters_selection = request.GET.getlist("converters[]")
    wecs = list()
    for converter_id in converters_selection:
        aWec = dict()
        converter = Wave_Energy_Converters.objects.get(pk=int(converter_id))
        aWec['name'] = converter.title
        aWec['min_H'] = str(int(round(converter.min_height, 0)))
        aWec['max_H'] = str(int(round(converter.max_height)))
        aWec['min_T'] = str(int(round(converter.min_energy_period)))
        aWec['max_T'] = str(int(round(converter.max_energy_period)))
        aWec['wec_matrix'] = converter.sample_rows
        wecs.append(aWec)
    args_to_note['wecs'] = wecs
    args_to_note['dataset_id'] = settings.WEC_GENERATION_FORECAST_SERVICE_DATASET_QUERY.keys()[0]
    args_to_note['start_date'] = str(Dataset.objects.get(pk=int(args_to_note['dataset_id'])).temporalCoverageBegin)
    args_to_note['end_date'] = str(Dataset.objects.get(pk=int(args_to_note['dataset_id'])).temporalCoverageEnd)
    service_exec.arguments = args_to_note
    service_exec.save()
    # CONFIGURE THE QUERY TO BE USED
    dataset_id = settings.WEC_AREA_EVALUATION_SERVICE_DATASET_QUERY.keys()[0]
    query_id = settings.WEC_AREA_EVALUATION_SERVICE_DATASET_QUERY[dataset_id]
    wave_height_query_id = get_query_with_updated_filters(request, query_id)
    # CLONE THE SERVICE NOTE
    new_notebook_id = clone_service_note(request, service, service_exec)
    # ADD THE VISUALISATIONS TO BE CREATED
    visualisations = dict()
    power_cols_str = ''
    cap_factors_cols_str = ''
    shut_down_cols_str = ''
    for i, converter_id in enumerate(converters_selection):
        converter = Wave_Energy_Converters.objects.get(pk=int(converter_id))
        power_cols_str += '&contour_var0=power for ' + str(converter.title) + '&contour_var_unit0=kW/m'
        cap_factors_cols_str += '&contour_var0=capacity factor for ' + str(converter.title) + '&contour_var_unit0=%'
        shut_down_cols_str += '&contour_var0=danger times for ' + str(converter.title) + '&contour_var_unit0=hours'

    visualisations['v1'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'title': "WEC Average Power Output",
                             'url': "/visualizations/get_map_visualization/?layer_count=1&viz_id0=20&action0=get_map_contour&n_contours0=500&step0=0.1&agg_func=AVG&lat_col0=i0_latitude&lon_col0=i0_longitude&df0=power_df&notebook_id0=" + str(new_notebook_id) + power_cols_str,
                             'done': False})
    visualisations['v2'] = ({'notebook_id': new_notebook_id,
                             'df': 'wec_cap_factors_df',
                             'query': '',
                             'title': "WEC Capacity Factor",
                             'url': "/visualizations/get_map_visualization/?layer_count=1&viz_id0=20&action0=get_map_contour&n_contours0=500&step0=0.1&agg_func=AVG&lat_col0=i0_latitude&lon_col0=i0_longitude&df0=wec_cap_factors_df&notebook_id0=" + str(new_notebook_id) + cap_factors_cols_str,
                             'done': False})
    visualisations['v3'] = ({'notebook_id': new_notebook_id,
                             'df': 'danger_times_df',
                             'query': '',
                             'title': "Number of Shut Down Hours",
                             'url': "/visualizations/get_map_visualization/?layer_count=1&viz_id0=20&action0=get_map_contour&n_contours0=500&step0=0.1&agg_func=AVG&lat_col0=i0_latitude&lon_col0=i0_longitude&df0=danger_times_df&notebook_id0=" + str(new_notebook_id) + shut_down_cols_str,
                             'done': False})
    service_exec.dataframe_visualizations = visualisations
    service_exec.save()
    # CREATE NEW ARGUMENTS PARAGRAPH
    new_arguments_paragraph = create_args_paragraph(request, new_notebook_id, args_to_note, service)
    # CREATE A LIVY SESSION
    if service.through_livy:
        service_exec.status = "Initializing Spark Session"
        service_exec.save()
        service_exec.livy_session = create_service_livy_session(request, service_exec)
        service_exec.save()
    try:
        # RUN THE SERVICE CODE
        execute_service_code(request, service_exec, new_arguments_paragraph, settings.WEC_AREA_EVALUATION_SERVICE_PARAGRAPHS)
        service_exec.status = "done"
        service_exec.save()
        t = Thread(target=clean_up_new_note, args=(str(new_notebook_id), 180))
        t.start()
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


@never_cache
def wec_area_evaluation_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    # GET THE SERVICE RESULTS
    result = get_result_dict_from_livy(service_exec.livy_session, 'result')
    print 'result: ' + str(result)
    # clean_up_new_note(service_exec.notebook_id)

    dataset_id = str(result['dataset_id'])
    dataset_title = str(Dataset.objects.get(pk=dataset_id))
    location_lat = str(result['location_lat'])
    location_lon = str(result['location_lon'])
    start_date = str(result['start_date'])
    end_date = str(result['end_date'])
    converters = [str(name) for name in result['name']]

    # SHOW THE SERVICE OUTPUT PAGE
    return render(request, 'wave_energy_pilot/wec_area_assessment result.html',
                  {'result': result,
                   'back_url': '/wave-energy/energy_conversion/',
                   'service_title': 'Wave Energy - Performance of Wave Energy Converter in a Wide Area',
                   'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):','value': '(' + location_lat + ', ' + location_lon + ') +/- 1 degree'},
                                        {'icon': 'far fa-calendar-alt', 'text': 'Timeframe:','value': 'from ' + str(start_date) + ' to ' + str(end_date)},
                                        {'icon': 'fas fa-database', 'text': 'Dataset used:', 'value': str(dataset_title) + ' <a target="_blank" rel="noopener noreferrer"  href="/datasets/' + str(dataset_id) + '/" style="color: #1d567e;text-decoration: underline">(more info)</a>'},
                                        {'icon': 'fas fa-water', 'text': 'WEC technologies:', 'value': str(converters)}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


@never_cache
def wec_generation_forecast_execute(request):
    service = Service.objects.get(pk=settings.WEC_GENERATION_FORECAST_SERVICE_ID)
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now(),
                                   status="starting service", dataframe_visualizations=[])
    service_exec.save()
    # Spawn thread to process the data
    t = Thread(target=wec_generation_forecast_execution_process, args=(request, service_exec.id))
    t.start()
    return JsonResponse({'exec_instance': service_exec.id})


def wec_generation_forecast_execution_process(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    service = Service.objects.get(pk=service_exec.service_id)
    # GATHER THE SERVICE ARGUMENTS
    service_args = ["start_date", "end_date", "latitude_from", "latitude_to", "longitude_from", "longitude_to"]
    args_to_note = gather_service_args(service_args, request, service_exec)
    converters_selection = request.GET.getlist("converters[]")
    wecs = list()
    for converter_id in converters_selection:
        aWec = dict()
        converter = Wave_Energy_Converters.objects.get(pk=int(converter_id))
        aWec['name'] = converter.title
        aWec['min_H'] = str(int(round(converter.min_height, 0)))
        aWec['max_H'] = str(int(round(converter.max_height)))
        aWec['min_T'] = str(int(round(converter.min_energy_period)))
        aWec['max_T'] = str(int(round(converter.max_energy_period)))
        aWec['wec_matrix'] = converter.sample_rows
        wecs.append(aWec)
    args_to_note['wecs'] = wecs
    args_to_note['dataset_id'] = settings.WEC_GENERATION_FORECAST_SERVICE_DATASET_QUERY.keys()[0]
    service_exec.arguments = args_to_note
    service_exec.save()
    # CONFIGURE THE QUERY TO BE USED
    dataset_id = settings.WEC_GENERATION_FORECAST_SERVICE_DATASET_QUERY.keys()[0]
    query_id = settings.WEC_GENERATION_FORECAST_SERVICE_DATASET_QUERY[dataset_id]
    wave_height_query_id = get_query_with_updated_filters(request, query_id)
    # CLONE THE SERVICE NOTE
    new_notebook_id = clone_service_note(request, service, service_exec)
    # ADD THE VISUALISATIONS TO BE CREATED
    visualisations = dict()
    power_cols_str = ''
    for i, converter_id in enumerate(converters_selection):
        converter = Wave_Energy_Converters.objects.get(pk=int(converter_id))
        power_cols_str += '&y_var[]=power for ' + str(converter.title) + '&y_var_unit[]=kW/m'

    visualisations['v1'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'title': "Generated Power",
                             'url': "/visualizations/get_line_chart_am/?x_var=time&df=power_df&notebook_id=" + str(
                                 new_notebook_id) + power_cols_str,
                             'done': False})
    service_exec.dataframe_visualizations = visualisations
    service_exec.save()
    # CREATE NEW ARGUMENTS PARAGRAPH
    new_arguments_paragraph = create_args_paragraph(request, new_notebook_id, args_to_note, service)
    # CREATE A LIVY SESSION
    if service.through_livy:
        service_exec.status = "Initializing Spark Session"
        service_exec.save()
        service_exec.livy_session = create_service_livy_session(request, service_exec)
        service_exec.save()
    try:
        # RUN THE SERVICE CODE
        execute_service_code(request, service_exec, new_arguments_paragraph, settings.WEC_LOCATION_EVALUATION_SERVICE_PARAGRAPHS)
        service_exec.status = "done"
        service_exec.save()
        t = Thread(target=clean_up_new_note, args=(str(new_notebook_id), 180))
        t.start()
    except Exception as e:
        print 'exception in livy execution'
        print '%s (%s)' % (e.message, type(e))
        service_exec.status = "failed"
        service_exec.save()
        clean_up_new_note(service_exec.notebook_id)
        if 'livy_session' in request.GET.keys():
            pass
        else:
            if service_exec.service.through_livy:
                close_livy_session(service_exec.livy_session)


@never_cache
def wec_generation_forecast_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    # GET THE SERVICE RESULTS
    result = get_result_dict_from_livy(service_exec.livy_session, 'result')
    print 'result: ' + str(result)
    # clean_up_new_note(service_exec.notebook_id)

    dataset_id = str(result['dataset_id'])
    dataset_title = str(Dataset.objects.get(pk=dataset_id))
    location_lat = str(result['location_lat'])
    location_lon = str(result['location_lon'])
    start_date = str(result['start_date'])
    end_date = str(result['end_date'])
    converter = str(result['name'][0])

    # SHOW THE SERVICE OUTPUT PAGE
    return render(request, 'wave_energy_pilot/wec_generation_forecast result.html',
                  {'result': result,
                   'back_url': '/wave-energy/energy_conversion/',
                   'service_title': 'Wave Energy - Wave Power Generation Forecast',
                   'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):','value': '(' + location_lat + ', ' + location_lon + ') +/- 1 degree'},
                                        {'icon': 'far fa-calendar-alt', 'text': 'Timeframe:','value': 'from ' + str(start_date) + ' to ' + str(end_date)},
                                        {'icon': 'fas fa-database', 'text': 'Dataset used:', 'value': str(dataset_title) + ' <a target="_blank" rel="noopener noreferrer"  href="/datasets/' + str(dataset_id) + '/" style="color: #1d567e;text-decoration: underline">(more info)</a>'},
                                        {'icon': 'fas fa-water', 'text': 'WEC technology used:', 'value': str(converter)}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


@never_cache
def wec_load_matching_execute(request):
    service = Service.objects.get(pk=settings.WEC_LOAD_MATCHING_SERVICE_ID)
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now(),
                                   status="starting service", dataframe_visualizations=[])
    service_exec.save()
    load_profile_csv = request.FILES['load_profile_csv']
    if not load_profile_csv.name.endswith('.csv'):
        return HttpResponse(status=500)

    # Write the file to disk
    fout = open('wave_energy_pilot/static/wave_energy_pilot/files/load_matching/' + load_profile_csv.name, 'wb')
    for chunk in load_profile_csv.chunks():
        fout.write(chunk)
    fout.close()

    # Spawn thread to process the data
    t = Thread(target=wec_load_matching_execution_process, args=(request, service_exec.id))
    t.start()
    return JsonResponse({'exec_instance': service_exec.id})


def wec_load_matching_execution_process(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    service = Service.objects.get(pk=service_exec.service_id)
    try:
        # GATHER THE SERVICE ARGUMENTS
        service_args = ["start_date", "end_date", "latitude_from", "latitude_to", "longitude_from", "longitude_to", "dataset_id"]
        args_to_note = gather_service_args(service_args, request, service_exec, 'post')
        load_profile_csv = request.FILES['load_profile_csv'].name
        args_to_note['load_profile_csv'] = load_profile_csv
        converters_selection = request.POST.getlist("converters[]")
        wecs = list()
        for converter_id in converters_selection:
            aWec = dict()
            converter = Wave_Energy_Converters.objects.get(pk=int(converter_id))
            aWec['name'] = converter.title
            aWec['min_H'] = str(int(round(converter.min_height, 0)))
            aWec['max_H'] = str(int(round(converter.max_height)))
            aWec['min_T'] = str(int(round(converter.min_energy_period)))
            aWec['max_T'] = str(int(round(converter.max_energy_period)))
            aWec['wec_matrix'] = converter.sample_rows
            wecs.append(aWec)
        args_to_note['wecs'] = wecs
        service_exec.arguments = args_to_note
        service_exec.save()
        # CONFIGURE THE QUERY TO BE USED
        dataset_id = request.POST['dataset_id']
        query_id = settings.WEC_LOAD_MATCHING_SERVICE_DATASET_QUERY[dataset_id]
        wave_height_query_id = get_query_with_updated_filters(request, query_id, 'post')
        # CLONE THE SERVICE NOTE
        new_notebook_id = clone_service_note(request, service, service_exec)
        # ADD THE VISUALISATIONS TO BE CREATED
        visualisations = dict()
        cols_str = ''
        for i, converter_id in enumerate(converters_selection):
            converter = Wave_Energy_Converters.objects.get(pk=int(converter_id))
            cols_str += '&y_var[]=power for ' + str(converter.title) + '&y_var_unit[]=kW/m'
        cols_str += '&y_var[]=load_profile ' + '&y_var_unit[]=load_profile_unit'

        visualisations['v1'] = ({'notebook_id': new_notebook_id,
                                 'df': 'power_df',
                                 'query': '',
                                 'title': "Generated Power",
                                 'url': "/visualizations/get_line_chart_am/?x_var=time&df=power_df&notebook_id=" + str(new_notebook_id) + cols_str,
                                 'done': False})
        service_exec.dataframe_visualizations = visualisations
        service_exec.save()
        # CREATE NEW ARGUMENTS PARAGRAPH
        new_arguments_paragraph = create_args_paragraph(request, new_notebook_id, args_to_note, service)
        # CREATE A LIVY SESSION
        if service.through_livy:
            service_exec.status = "Initializing Spark Session"
            service_exec.save()
            service_exec.livy_session = create_service_livy_session(request, service_exec)
            service_exec.save()
    except Exception as e:
        print 'exception in preparing execution'
        print '%s (%s)' % (e.message, type(e))
        service_exec.status = "failed"
        service_exec.save()
        clean_up_new_note(service_exec.notebook_id)
        if 'livy_session' in request.GET.keys():
            pass
        else:
            if service_exec.service.through_livy:
                close_livy_session(service_exec.livy_session)
    try:
        # RUN THE SERVICE CODE
        execute_service_code(request, service_exec, new_arguments_paragraph, settings.WEC_LOAD_MATCHING_SERVICE_PARAGRAPHS)
        service_exec.status = "done"
        service_exec.save()
        t = Thread(target=clean_up_new_note, args=(str(new_notebook_id), 180))
        t.start()
    except Exception as e:
        print 'exception in livy execution'
        print '%s (%s)' % (e.message, type(e))
        service_exec.status = "failed"
        service_exec.save()
        clean_up_new_note(service_exec.notebook_id)
        if 'livy_session' in request.GET.keys():
            pass
        else:
            if service_exec.service.through_livy:
                close_livy_session(service_exec.livy_session)


@never_cache
def wec_load_matching_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    # GET THE SERVICE RESULTS
    result = get_result_dict_from_livy(service_exec.livy_session, 'result')
    print 'result: ' + str(result)
    # clean_up_new_note(service_exec.notebook_id)

    dataset_id = str(result['dataset_id'])
    dataset_title = str(Dataset.objects.get(pk=dataset_id))
    location_lat = str(result['location_lat'])
    location_lon = str(result['location_lon'])
    start_date = str(result['start_date'])
    end_date = str(result['end_date'])
    converter = str(result['name'][0])

    # SHOW THE SERVICE OUTPUT PAGE
    return render(request, 'wave_energy_pilot/wec_load_matching result.html',
                  {'result': result,
                   'back_url': '/wave-energy/energy_conversion/',
                   'service_title': 'Wave Energy - Assessment of Wave Energy Generation and Load Matching',
                   'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):','value': '(' + location_lat + ', ' + location_lon + ') +/- 1 degree'},
                                        {'icon': 'far fa-calendar-alt', 'text': 'Timeframe:','value': 'from ' + str(start_date) + ' to ' + str(end_date)},
                                        {'icon': 'fas fa-database', 'text': 'Dataset used:', 'value': str(dataset_title) + ' <a target="_blank" rel="noopener noreferrer"  href="/datasets/' + str(dataset_id) + '/" style="color: #1d567e;text-decoration: underline">(more info)</a>'},
                                        {'icon': 'fas fa-water', 'text': 'WEC technology used:', 'value': str(converter)}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


@never_cache
def energy_conversion_status(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    return JsonResponse({'status': service_exec.status})


@never_cache
def init(request):
    execution_steps = dict()
    execution_steps['LOCATION_EVALUATION_SERVICE'] = ['starting service', 'Initializing Spark Session'] + [x['status'] for x in settings.LOCATION_EVALUATION_SERVICE_PARAGRAPHS] + ['done']
    execution_steps['WAVE_FORECAST_SERVICE'] = ['starting service', 'Initializing Spark Session'] + [x['status'] for x in settings.WAVE_FORECAST_SERVICE_PARAGRAPHS] + ['done']
    execution_steps['AREA_EVALUATION_SERVICE'] = ['starting service', 'Initializing Spark Session'] + [x['status'] for x in settings.AREA_EVALUATION_SERVICE_PARAGRAPHS] + ['done']
    execution_steps['DATA_VISUALISATION_SERVICE'] = ['starting service']
    for dataset in DATASETS:
        try:
            service_dataset = Dataset.objects.get(pk=dataset["id"])
            print "----------------brhkame dataset"
            try:
                dataset["min_lat"] = int(service_dataset.spatialSouth)
            except:
                dataset["min_lat"] = -90
            try:
                dataset["max_lat"] = int(service_dataset.spatialNorth)
            except:
                dataset["max_lat"] = 90
            try:
                dataset["min_lng"] = int(service_dataset.spatialWest)
            except:
                dataset["min_lng"] = -180
            try:
                dataset["max_lng"] = int(service_dataset.spatialEast)
            except:
                dataset["max_lng"] = 180
            
            dataset["min_date"] = service_dataset.temporalCoverageBegin
            dataset["max_date"] = service_dataset.temporalCoverageEnd
            print dataset["min_lat"]
            print dataset["max_lat"]
            print dataset["min_lng"]
            print dataset["max_lng"]
            print dataset["min_date"]
            print dataset["max_date"]
        except:
            print "dataset not found"
    return render(request, 'wave_energy_pilot/load_service.html',
                  {'buoys_list': BUOYS,
                   'datasets_list': DATASETS,
                   'data_radius': DATA_RADIUS,
                   'execution_steps': execution_steps})


@never_cache
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
                             'url': "/visualizations/get_line_chart_am/?"+y_var+"x_var=i0_time&limit=False&agg_func=AVG&query="+str(visualization_query_id),
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
                   'back_url': '/wave-energy/',
                   'service_title': 'Visualisation of a single data source',
                   'study_conditions': [
                       {'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):', 'value': '('+location_lat+', '+location_lon+') +/- 1 degree'},
                       {'icon': 'far fa-calendar-alt', 'text': 'Timeframe:', 'value': 'from '+ str(start_date) + ' to ' + str(end_date)},
                       {'icon': 'fas fa-database', 'text': 'Dataset used:',
                        'value': str(dataset_title) + ' <a target="_blank" rel="noopener noreferrer"  href="/datasets/'+str(dataset_id)+'/" style="color: #1d567e;text-decoration: underline">(more info)</a>'},
                       {'icon': 'fas fa-info-circle', 'text': 'Selected variables:', 'value': str(variable_list_with_commas)}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


@never_cache
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
    service_args = ["start_date", "end_date", "latitude_from", "latitude_to", "longitude_from", "longitude_to", "dataset_id"]
    args_to_note = gather_service_args(service_args, request, service_exec)
    # CONFIGURE THE QUERY TO BE USED
    dataset_id = request.GET["dataset_id"]
    query_id = settings.LOCATION_EVALUATION_SERVICE_DATASET_QUERY[dataset_id]
    wave_height_query_id = get_query_with_updated_filters(request, query_id)
    # CLONE THE SERVICE NOTE
    new_notebook_id = clone_service_note(request, service, service_exec)
    # ADD THE VISUALISATIONS TO BE CREATED
    visualisations = dict()
    # visualisations['v1'] = ({'notebook_id': '',
    #                          'df': '',
    #                          'query': wave_height_query_id,
    #                          'title': "Sea surface wave significant height",
    #                          'url': "/visualizations/get_line_chart_am/?y_var[]=i0_sea_surface_wave_significant_height&x_var=i0_time&limit=False&query="+str(wave_height_query_id),
    #                          'done': False})
    visualisations['v2'] = ({'notebook_id': '',
                             'df': '',
                             'query': wave_height_query_id,
                             'title': "Occurrence matrix",
                             'url': "/visualizations/get_histogram_2d_am?viz_id=17&action=get_histogram_2d_am&y_var=i0_sea_surface_wave_significant_height&x_var=i1_sea_surface_wave_zero_upcrossing_period&bins=10&query=" + str(
                                 wave_height_query_id),
                             'done': False})
    visualisations['v3'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'title': "Power line chart",
                             'url': "/visualizations/get_line_chart_am/?y_var[]=avg(power)&y_var_unit[]=kW/m&x_var=time&df=power_df&notebook_id="+str(new_notebook_id),
                             'done': False})
    visualisations['v4'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'title': "Power histogram",
                             'url': "/visualizations/get_histogram_chart_am/?bins=5&x_var=avg(power)&df=power_df&notebook_id="+str(new_notebook_id),
                             'done': False})

    start_year = int(args_to_note['start_date'].split('-')[0])
    end_year = int(args_to_note['end_date'].split('-')[0])
    print start_year, end_year
    power_availability_vars = ''
    for year in range(start_year, end_year+1):
        power_availability_vars += '&y_var[]=avg(power)_'+str(year)+'&y_var_unit[]=kW/m'
    visualisations['v5'] = ({'notebook_id': '',
                             'df': 'power_df_year_month',
                             'query': '',
                             'title': "Monthly availability of waves",
                             'url': "/visualizations/get_column_chart_am/?x_var=month_name&df=power_df_year_month&notebook_id="+str(new_notebook_id) + str(power_availability_vars),
                             'done': False})
    # visualisations['v5'] = ({'notebook_id': '',
    #                          'df': '',
    #                          'query': wave_height_query_id,
    #                          'title': "Monthly availability of waves",
    #                          'url': "/visualizations/get_time_series_am?viz_id=22&action=get_time_series_am&y_var[]=i0_sea_surface_wave_significant_height&temporal_resolution=date_trunc_month&agg_func=AVG&query=" + str(
    #                              wave_height_query_id),
    #                          'done': False})
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
        execute_service_code(request, service_exec, new_arguments_paragraph, settings.LOCATION_EVALUATION_SERVICE_PARAGRAPHS)
        service_exec.status = "done"
        service_exec.save()
        t = Thread(target=clean_up_new_note, args=(str(new_notebook_id), 180))
        t.start()
    except Exception as e:
        print 'exception in livy execution'
        print '%s (%s)' % (e.message, type(e))
        service_exec.status = "failed"
        service_exec.save()
        clean_up_new_note(service_exec.notebook_id)
        if 'livy_session' in request.GET.keys():
            pass
        # else:
        #     if service_exec.service.through_livy:
        #         close_livy_session(service_exec.livy_session)


@never_cache
def single_location_evaluation_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    # GET THE SERVICE RESULTS
    result = get_result_dict_from_livy(service_exec.livy_session, 'result')
    print 'result: ' + str(result)
    # clean_up_new_note(service_exec.notebook_id)

    dataset_id = str(result['dataset_id'])
    dataset_title = str(Dataset.objects.get(pk=dataset_id))
    location_lat = str(result['location_lat'])
    location_lon = str(result['location_lon'])
    start_date = str(result['start_date'])
    end_date = str(result['end_date'])

    # SHOW THE SERVICE OUTPUT PAGE
    return render(request, 'wave_energy_pilot/location_assessment result.html',
                  {'result': result,
                   'back_url': '/wave-energy/',
                   'service_title': 'Wave Energy - Evaluation of a single location',
                   'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):','value': '(' + location_lat + ', ' + location_lon + ') +/- 1 degree'},
                                        {'icon': 'far fa-calendar-alt', 'text': 'Timeframe:','value': 'from ' + str(start_date) + ' to ' + str(end_date)},
                                        {'icon': 'fas fa-database', 'text': 'Dataset used:', 'value': str(dataset_title) + ' <a target="_blank" rel="noopener noreferrer"  href="/datasets/' + str(dataset_id) + '/" style="color: #1d567e;text-decoration: underline">(more info)</a>'}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


@never_cache
def single_location_evaluation_status(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    return JsonResponse({'status': service_exec.status})


def cancel_execution(request, exec_instance):
    print "Cancelling"
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    service_exec.status = "failed"
    service_exec.save()
    close_livy_session(int(service_exec.livy_session))
    clean_up_new_note(service_exec.notebook_id)
    print "Cancelled?"
    return JsonResponse({'status': "cancelled"})


@never_cache
def area_location_evaluation_execute(request):
    service = Service.objects.get(pk=settings.AREA_EVALUATION_SERVICE_ID)
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now(),
                                   status="starting service", dataframe_visualizations=[])
    service_exec.save()
    # Spawn thread to process the data
    t = Thread(target=area_location_evaluation_execution_process, args=(request, service_exec.id))
    t.start()
    return JsonResponse({'exec_instance': service_exec.id})


def area_location_evaluation_execution_process(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    service = Service.objects.get(pk=service_exec.service_id)
    # GATHER THE SERVICE ARGUMENTS
    service_args = ["start_date", "end_date", "latitude_from", "latitude_to", "longitude_from", "longitude_to", "dataset_id"]
    args_to_note = gather_service_args(service_args, request, service_exec)
    # CONFIGURE THE QUERY TO BE USED
    dataset_id = request.GET["dataset_id"]
    query_id = settings.AREA_EVALUATION_SERVICE_DATASET_QUERY[dataset_id]
    wave_height_query_id = get_query_with_updated_filters(request, query_id)
    # CLONE THE SERVICE NOTE
    new_notebook_id = clone_service_note(request, service, service_exec)
    # ADD THE VISUALISATIONS TO BE CREATED
    visualisations = dict()
    visualisations['v1'] = ({'notebook_id': '',
                             'df': '',
                             'query': wave_height_query_id,
                             'title': "Mean significant wave height",
                             'url': "/visualizations/get_map_visualization/?layer_count=1&viz_id0=20&action0=get_map_contour&contour_var0=i0_sea_surface_wave_significant_height&n_contours0=500&step0=0.1&agg_func=AVG&query0="+str(wave_height_query_id),
                             'done': False})
    visualisations['v2'] = ({'notebook_id': '',
                             'df': '',
                             'query': wave_height_query_id,
                             'title': "Mean wave period",
                             'url': "/visualizations/get_map_visualization/?layer_count=1&viz_id0=20&action0=get_map_contour&contour_var0=i1_sea_surface_wave_zero_upcrossing_period&n_contours0=500&step0=0.1&agg_func=AVG&query0=" + str(wave_height_query_id),
                             'done': False})
    visualisations['v3'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'title': "Mean wave power",
                             'url': "/visualizations/get_map_visualization/?layer_count=1&viz_id0=20&action0=get_map_contour&contour_var0=avg_power&contour_var_unit0=kW/m&n_contours0=500&step0=0.1&agg_func=AVG&lat_col0=i0_latitude&lon_col0=i0_longitude&df0=power_df&notebook_id0=" + str(new_notebook_id),
                             'done': False})
    visualisations['v4'] = ({'notebook_id': '',
                             'df': '',
                             'query': wave_height_query_id,
                             'title': "Maximum significant wave height",
                             'url': "/visualizations/get_map_visualization/?layer_count=1&viz_id0=20&action0=get_map_contour&contour_var0=i0_sea_surface_wave_significant_height&n_contours0=80&step0=0.1&agg_func=MAX&query0=" + str(
                                 wave_height_query_id),
                             'done': False})
    visualisations['v5'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'title': "Maximum wave power",
                             'url': "/visualizations/get_map_visualization/?layer_count=1&viz_id0=20&action0=get_map_contour&contour_var0=max_power&contour_var_unit0=kW/m&n_contours0=500&step0=0.1&agg_func=AVG&lat_col0=i0_latitude&lon_col0=i0_longitude&df0=power_df&notebook_id0=" + str(new_notebook_id),
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
        execute_service_code(request, service_exec, new_arguments_paragraph, settings.AREA_EVALUATION_SERVICE_PARAGRAPHS)
        service_exec.status = "done"
        service_exec.save()
        clean_up_new_note(service_exec.notebook_id)
    except Exception as e:
        print 'exception in livy execution'
        print '%s (%s)' % (e.message, type(e))
        service_exec.status = "failed"
        service_exec.save()
        clean_up_new_note(service_exec.notebook_id)
        if 'livy_session' in request.GET.keys():
            pass
        else:
            if service_exec.service.through_livy:
                close_livy_session(service_exec.livy_session)


def area_location_evaluation_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    # GET THE SERVICE RESULTS
    result = get_result_dict_from_livy(service_exec.livy_session, 'result')
    print 'result: ' + str(result)
    # clean_up_new_note(service_exec.notebook_id)

    dataset_id = str(result['dataset_id'])
    dataset_title = str(Dataset.objects.get(pk=dataset_id))
    latitude_from = str(result['latitude_from'])
    latitude_to = str(result['latitude_to'])
    longitude_from = str(result['longitude_from'])
    longitude_to = str(result['longitude_to'])
    start_date = str(result['start_date'])
    end_date = str(result['end_date'])

    # SHOW THE SERVICE OUTPUT PAGE
    return render(request, 'wave_energy_pilot/area_assessment result.html',
                  {'result': result,
                   'back_url': '/wave-energy/',
                   'service_title': 'Wave Energy - Wave atlas of a region',
                   'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):','value': 'from (' + latitude_from + ', ' + longitude_from + ') to (' + latitude_to + ', ' + longitude_to + ')'},
                                        {'icon': 'far fa-calendar-alt', 'text': 'Timeframe:','value': 'from ' + str(start_date) + ' to ' + str(end_date)},
                                        {'icon': 'fas fa-database', 'text': 'Dataset used:', 'value': str(dataset_title) + ' <a target="_blank" rel="noopener noreferrer"  href="/datasets/' + str(dataset_id) + '/" style="color: #1d567e;text-decoration: underline">(more info)</a>'}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


@never_cache
def area_location_evaluation_status(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    return JsonResponse({'status': service_exec.status})


@never_cache
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
    service_args = ["start_date", "end_date", "latitude_from", "latitude_to", "longitude_from", "longitude_to", 'dataset_id']
    args_to_note = gather_service_args(service_args, request, service_exec)
    # CONFIGURE THE QUERY TO BE USED
    dataset_id = request.GET["dataset_id"]
    query_id = settings.WAVE_FORECAST_SERVICE_DATASET_QUERY[dataset_id]
    wave_forecast_query_id = get_query_with_updated_filters(request, query_id)
    # CLONE THE SERVICE NOTE
    new_notebook_id = clone_service_note(request, service, service_exec)
    # ADD THE VISUALISATIONS TO BE CREATED
    visualisations = dict()
    visualisations['v1'] = ({'notebook_id': '',
                             'df': '',
                             'query': wave_forecast_query_id,
                             'url': "/visualizations/get_line_chart_am/?y_var[]=i0_sea_surface_wave_significant_height&x_var=i0_time&limit=False&query="+str(wave_forecast_query_id),
                             'done': False,
                             'title': 'Wave significant height'})
    visualisations['v2'] = ({'notebook_id': '',
                             'df': '',
                             'query': wave_forecast_query_id,
                             'url': "/visualizations/get_line_chart_am/?y_var[]=i1_sea_surface_wave_zero_upcrossing_period&x_var=i0_time&limit=False&query=" + str(
                                 wave_forecast_query_id),
                             'done': False,
                             'title': 'Wave mean period'})
    visualisations['v3'] = ({'notebook_id': new_notebook_id,
                             'df': 'power_df',
                             'query': '',
                             'url': "/visualizations/get_line_chart_am/?y_var[]=avg(power)&y_var_unit[]=kW/m&x_var=time&df=power_df&notebook_id="+str(new_notebook_id),
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
        execute_service_code(request, service_exec, new_arguments_paragraph, settings.WAVE_FORECAST_SERVICE_PARAGRAPHS)
        service_exec.status = "done"
        service_exec.save()
        clean_up_new_note(service_exec.notebook_id)
    except Exception as e:
        print 'exception in livy execution'
        print '%s (%s)' % (e.message, type(e))
        service_exec.status = "failed"
        service_exec.save()
        clean_up_new_note(service_exec.notebook_id)
        if 'livy_session' in request.GET.keys():
            pass
        else:
            if service_exec.service.through_livy:
                close_livy_session(service_exec.livy_session)


@never_cache
def wave_forecast_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    # GET THE SERVICE RESULTS
    result = get_result_dict_from_livy(service_exec.livy_session, 'result')
    print 'result: ' + str(result)

    # clean_up_new_note(service_exec.notebook_id)
    dataset_id = str(result['dataset_id'])
    dataset_title = str(Dataset.objects.get(pk=dataset_id))
    location_lat = str(result['location_lat'])
    location_lon = str(result['location_lon'])
    start_date = str(result['start_date'])
    end_date = str(result['end_date'])

    # SHOW THE SERVICE OUTPUT PAGE
    return render(request, 'wave_energy_pilot/wave_forecast result.html',
                  {'result': result,
                   'back_url': '/wave-energy/',
                   'service_title': 'Wave Energy - Wave forecast in a location',
                   'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):','value': '(' + location_lat + ', ' + location_lon + ') +/- 1 degree'},
                                        {'icon': 'far fa-calendar-alt', 'text': 'Timeframe:','value': 'from ' + str(start_date) + ' to ' + str(end_date)},
                                        {'icon': 'fas fa-database', 'text': 'Dataset used:', 'value': str(dataset_title) + ' <a target="_blank" rel="noopener noreferrer"  href="/datasets/' + str(dataset_id) + '/" style="color: #1d567e;text-decoration: underline">(more info)</a>'}],
                   'no_viz': 'no_viz' in request.GET.keys(),
                   'visualisations': service_exec.dataframe_visualizations})


@never_cache
def wave_forecast_status(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    return JsonResponse({'status': service_exec.status})


def get_load_matching_file_data(request):
    import csv
    result_list = list()
    file_name = request.GET['file']
    file_path = 'wave_energy_pilot/static/wave_energy_pilot/files/load_matching/'+file_name
    # file_path = 'visualizer/static/visualizer/files/kml2.json'
    with open(file_path, mode="r") as infile:
        reader = csv.reader(infile)
        result_list = [{"time": rows[0], "value": rows[1]} for rows in reader]
    return JsonResponse({"result": result_list[1:]})
