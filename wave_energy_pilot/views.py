# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import json

from background_task import background
from bs4 import BeautifulSoup
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, Template

from lists import *
from datasets import *

# Create your views here.
from query_designer.models import Query
from service_builder.models import Service, ServiceInstance
from visualizer.utils import delete_zep_notebook, clone_zep_note, create_zep_arguments_paragraph, delete_zep_paragraph, run_zep_note, \
    get_result_dict_from_livy, create_zep_getDict_paragraph, run_zep_paragraph, get_zep_getDict_paragraph_response, close_livy_session, \
    create_livy_session


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


def init(request):

    return render(request, 'wave_energy_pilot/load_service.html', {'buoys_list': BUOYS, 'datasets_list': DATASETS})


def execute_single_location_evaluation(request):
    service = Service.objects.get(pk=137)
    livy = service.through_livy
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now())
    service_exec.save()

    # 1. GATHER THE SERVICE ARGUMENTS
    service_args = convert_unicode_json(service.arguments)
    service_algorithm_args = service_args["algorithm-arguments"]
    print 'original algorithm args:'
    print service_algorithm_args
    args_to_note = dict()
    for algorithm_arg in service_algorithm_args:
        args_to_note[algorithm_arg['name']] = request.GET.get(algorithm_arg['name'], algorithm_arg['default'])
    print 'user algorithm args:'
    print args_to_note
    service_exec.arguments = {'filter-arguments': [], 'algorithm-arguments': service_algorithm_args}
    service_exec.save()

    # 2. BRING THE CUSTOMISED QUERIES TO THE SERVICE CODE
    original_notebook_id = service.notebook_id
    excluded_paragraphs = []
    new_notebook_id = clone_zep_note(original_notebook_id, "")
    service_exec.notebook_id = new_notebook_id
    service_exec.save()
    print 'Notebook ID: {0}'.format(new_notebook_id)

    new_arguments_paragraph = create_zep_arguments_paragraph(notebook_id=new_notebook_id, title='',
                                                             args_json_string=json.dumps(args_to_note))
    if service.arguments_paragraph_id is not None:
        delete_zep_paragraph(new_notebook_id, service.arguments_paragraph_id)

    visualizations = []
    dataframe_viz = []
    dataframe_viz.append({'notebook_id': '',
                          'df': 'df1',
                          'url': '',
                          'done': False})
    service_exec.dataframe_visualizations = dataframe_viz
    service_exec.save()

    # 3.RUN THE SERVICE CODE (one by one paragraph, or all together. CHOOSE..)
    try:
        # livy_session = run_zep_note(notebook_id=new_notebook_id, exclude=excluded_paragraphs, mode='livy')
        livy_session = create_livy_session(service_exec.notebook_id)
        service_exec.livy_session = livy_session
        service_exec.save()
        for p in ['20181031-002359_901292931',
                  new_arguments_paragraph,
                  '20180501-135246_1102090558',
                  '20180330-142735_316377038',
                  '20180330-151846_1205255152',
                  '20190123-163436_1241586309']:
            print 'executing paragraph: ' + p
            run_zep_paragraph(service_exec.notebook_id, p, livy_session, 'livy')


        # 5. GET THE SERVICE RESULTS
        result = get_result_dict_from_livy(livy_session, 'result')
        print 'result: ' + str(result)
        clean_up_new_note(service_exec.notebook_id)
        return render(request, 'wave_energy_pilot/location_assessment result.html',
                      {'result': result,
                       'new_notebook_id': service_exec.notebook_id})

    except Exception as e:
        print 'exception in livy execution'
        print '%s (%s)' % (e.message, type(e))
        clean_up_new_note(service_exec.notebook_id)
        if livy:
            close_livy_session(service_exec.livy_session)
        return HttpResponse(status=500)
