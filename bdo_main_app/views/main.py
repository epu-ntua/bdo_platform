# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils.timezone import now
from datetime import datetime
import time
from aggregator.models import Dataset, Organization, Variable, Dimension
from bdo_main_app.models import Service


def home(request):
    return render(request, 'bdoindex.html')


def exploretools(request):
    return render(request, 'explore.html')


def dataset_search(request):
    data_on_top = 'false'
    if 'data-on-top' in request.GET.keys():
        data_on_top = request.GET.get('data-on-top')

    storage_target = 'UBITECH_PRESTO'
    dataset_list = Dataset.objects.filter(stored_at=storage_target).exclude(variables=None)
    # organization_list = Organization.objects.all()
    organization_list = sorted(set([d.publisher for d in dataset_list]))
    observation_list = sorted(set([d.observations for d in dataset_list]))
    license_list = sorted(set([d.license for d in dataset_list]))
    category_list = sorted(set([d.category for d in dataset_list if d.category is not None and d.category.strip() != ""]))
    variable_list = Variable.objects.all().order_by('title')
    variable_list_filter = sorted(set([(v.safe_name, v.title) for v in variable_list]))

    time_start_timestamp = min([d.temporalCoverageBeginTimestamp for d in Dataset.objects.all() if d.temporalCoverageBeginTimestamp != ""])
    date_now = datetime.now()
    time_end_timestamp = max([d.temporalCoverageEndTimestamp for d in Dataset.objects.all() if d.temporalCoverageEndTimestamp != ""] + [long(time.mktime(date_now.timetuple())) * 1000])

    return render(request, 'dataset_search.html', {
        'organizations': organization_list,
        'observations': observation_list,
        'licenses': license_list,
        'categories': category_list,
        'variables': variable_list,
        'variable_list_filter': variable_list_filter,
        'datasets': dataset_list,
        'dimensions': Dimension.objects.all(),
        'data_on_top': data_on_top,
        'time_start_timestamp': time_start_timestamp,
        'time_end_timestamp': time_end_timestamp
    })

def bdohome(request):
    return render(request, 'index.html', {
        'sidebar_active': 'products',
        'items': [
            {
                'title': 'Vessel operators',
                'image': 'fleet_operators.jpg',
                'description': 'BigDataOcean provides data and tools that allow you '
                               'to operate your fleet in a more efficient way.',
                'link': '#',
            },
            {
                'title': 'Ship builders',
                'image': 'ship_builders.jpg',
                'description': 'Acquire vessel operation data and find out how '
                               'engine components behave under different conditions.',
                'link': '#',
            },
            {
                'title': 'Public authorities',
                'image': 'public_authorities.jpg',
                'description': 'Detect anomalies in vessel behaviour and'
                               ' enable automated alarms that suit your needs in no time.',
                'link': '#',
            },
            {
                'title': 'Researchers',
                'image': 'researchers.jpg',
                'description': 'Get access to scientific as well as commercial maritime data '
                               '& run customizable big data analytics on them - '
                               'with BigDataOcean, you don\'t have to be tech savvy to do all that.',
                'link': '#',
            },
            {
                'title': 'Wave energy providers',
                'image': 'wave_energy.jpg',
                'description': 'Research potential locations for wave energy systems and '
                               'estimate their potential energy output',
                'link': '#',
            },
            {
                'title': 'Support',
                'image': 'life_belt.jpg',
                'description': 'Whatever your place in the maritime industry, '
                               'our technical team and the community can develop services that will '
                               'move your business into the era of Big Data - just test us!',
                'link': '#',
            },
        ],
    })


def search(request):
    return render(request, 'search.html', {
        'sidebar_active': 'products',
        'q': request.GET.get('q', ''),
        'facets': [],
        'results': Service.objects.filter(hidden=False),
    })




