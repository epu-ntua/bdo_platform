from __future__ import unicode_literals
# -*- coding: utf-8 -*-

import json

from django.http import JsonResponse

from analytics.models import *
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from bdo_main_app.models import EXTENDABLE_SERVICES, get_service_by_id


def pick_base_analysis(request):
    return render(request, 'basic-analytics/pick-base-analysis.html', {
        'sidebar_active': 'products',
        'base_analytics': EXTENDABLE_SERVICES,
    })


def config_base_analysis(request, base_analysis_id):
    base_analysis = get_service_by_id(int(base_analysis_id))

    if request.method == 'GET':
        return render(request, 'basic-analytics/config-analysis.html', {
            'sidebar_active': 'products',
            'base_analysis': base_analysis,
        })
    else:
        # gather arguments
        arguments = {}
        for argument in base_analysis['arguments']:
            arguments[argument['name']] = request.POST.get(argument['name'],
                                                           argument['default'] if 'default' in argument else '')

        # validate arguments
        # TODO validate arguments

        # create job
        user = User.objects.get(username='dpap')
        job = JobInstance.objects.create(user=user, service_id=base_analysis['pk'], arguments=arguments)

        # submit the job
        job.submit()

        # redirect to job's page
        return redirect(job.get_absolute_url())


def view_job_details(request, pk):
    # get job
    job = JobInstance.objects.get(pk=pk)

    # find appropriate template
    template = 'basic-analytics/job-details-index.html'
    if request.GET.get('partial', '').lower() == 'true':
        template = 'basic-analytics/job-details.html'

    # render
    return render(request, template, {
        'sidebar_active': 'products',
        'job': job,
        'base_analysis': get_service_by_id(int(job.service_id))
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
