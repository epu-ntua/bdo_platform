from __future__ import unicode_literals
# -*- coding: utf-8 -*-

import json
from thread import start_new_thread
from threading import Thread

from django.http import JsonResponse, HttpResponse

from analytics.models import *
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from bdo_main_app.models import Service
from query_designer.models import Query


def pick_base_analysis(request):
    return render(request, 'basic-analytics/pick-base-analysis.html', {
        'sidebar_active': 'products',
        'base_analytics': Service.objects.filter(service_type='analysis', hidden=False).order_by('id'),
    })


def config_base_analysis(request, base_analysis_id):
    base_analysis = Service.objects.get(pk=int(base_analysis_id))

    if request.method == 'GET':
        user = request.user
        if request.user.is_authenticated():
            saved_queries = Query.objects.filter(user=user)
        else:
            saved_queries = []
        return render(request, 'basic-analytics/config-analysis.html', {
            'sidebar_active': 'products',
            'base_analysis': base_analysis,
            'saved_queries': saved_queries,
        })
    else:
        # gather arguments
        arguments = {}
        for argument in base_analysis.info['arguments']:
            arguments[argument['name']] = request.POST.get(argument['name'],
                                                           argument['default'] if 'default' in argument else '')
        for parameter in base_analysis.info['parameters']:
            arguments[parameter['name']] = request.POST.get(parameter['name'],
                                                            parameter['default'] if 'default' in parameter else '')

        print arguments
        # validate arguments
        # TODO validate arguments

        # create job
        # TODO: put the logged in user
        user = request.user
        query = arguments['query']
        arguments.pop('query', None)
        job = JobInstance.objects.create(user=user, analysis_flow={"1": str(base_analysis_id)}, arguments={"1": arguments, "query": query})

        # submit the job
        Thread(target=job.submit, args=[]).start()

        # redirect to job's page
        return redirect(job.get_absolute_url())


def get_analysis_form_fields(request):
    anal_id = request.GET.get('id')
    order = request.GET.get('order')
    service = Service.objects.get(pk=anal_id)
    html = render_to_string('basic-analytics/config-analysis-form-fields.html', {'order': order, 'anal_id': anal_id, 'info': service.info})
    return HttpResponse(html)


def build_dynamic_service(request):
    if request.method == 'GET':
        user = request.user
        if request.user.is_authenticated():
            saved_queries = Query.objects.filter(user=user)
        else:
            saved_queries = []
        return render(request, 'service_builder/service_builder.html', {
            'sidebar_active': 'products',
            'saved_queries': saved_queries,
            'components': Service.objects.filter(service_type='analysis', hidden=False).order_by('id'),
        })
    else:
        # print(request.POST)
        total_args = dict()
        analysis_flow = json.loads(request.POST.get('analysis_flow'))
        print analysis_flow
        for order in range(1, len(analysis_flow)+1):
            base_analysis_id = analysis_flow[str(order)]
            base_analysis = Service.objects.get(pk=int(base_analysis_id))
            # gather arguments
            arguments = dict()
            for argument in base_analysis.info['arguments']:
                if argument['name'] != 'query':
                    arguments[argument['name']] = request.POST.get(str(order)+'+++'+argument['name'],
                                                                   argument['default'] if 'default' in argument else '')
            for parameter in base_analysis.info['parameters']:
                arguments[parameter['name']] = request.POST.get(str(order)+'+++'+parameter['name'],
                                                                parameter['default'] if 'default' in parameter else '')

            print arguments
            # validate arguments
            # TODO validate arguments
            total_args[str(order)] = arguments

        total_args['query'] = request.POST.get('query')
        print total_args
        # create job
        # TODO: put the logged in user

        user = request.user
        if not request.user.is_authenticated():
            user = User.objects.get(username='BigDataOcean')

        job = JobInstance.objects.create(user=user, analysis_flow=analysis_flow, arguments=total_args)

        # submit the job
        Thread(target=job.submit, args=[]).start()

        # #TODO: this is temporal, modify the job details!
        # return render(request, 'service_builder/service_builder.html', {
        #     'sidebar_active': 'products',
        #     'saved_queries': [],
        #     'components': Service.objects.filter(service_type='analysis').order_by('id'),
        # })

        # redirect to job's page
        return redirect(job.get_absolute_url())


def view_job_details(request, pk):
    # get job
    job = JobInstance.objects.get(pk=pk)

    # find appropriate template
    template = 'basic-analytics/job-details-index.html'
    if request.GET.get('partial', '').lower() == 'true':
        template = 'basic-analytics/job-details.html'

    # analytics_list = dict()
    for k in job.analysis_flow.keys():
        job.analysis_flow[k] = Service.objects.get(pk=int(job.analysis_flow[k])).title

    # render
    return render(request, template, {
        'sidebar_active': 'products',
        'job': job,
        'analysis_flow': sorted(job.analysis_flow.iteritems()),
    })


@csrf_exempt
def update_job(request, pk):
    try:
        job = JobInstance.objects.get(pk=pk)
    except JobInstance.DoesNotExist:
        return JsonResponse({'error': 'Invalid job id'}, status=404)

    if request.method == 'POST':
        # get spark output
        failed = request.POST.get('success', '').lower() != 'true'
        results = json.loads(request.POST.get('results', 'null'))
        error_msg = request.POST.get('error', '')

        # update job
        job.update(results=results, error_msg=error_msg)

        return JsonResponse({}, status=200)

    return JsonResponse({'error': 'Invalid method: only POST allowed'}, status=400)
