# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils.timezone import now

from aggregator.models import Dataset, Organization, Variable, Dimension
from bdo_main_app.models import Service

def home(request):
    return render(request, 'bdoindex.html')
def exploretools(request):
    return render(request, 'explore.html')

def dataset_search(request):
    storage_target = 'UBITECH_PRESTO'
    dataset_list = Dataset.objects.filter(stored_at=storage_target).exclude(variables=None)
    organization_list = Organization.objects.all()
    variable_list = Variable.objects.all()

    return render(request, 'dataset_search.html', {
        'organizations': organization_list,
        'variables': variable_list,
        'datasets': dataset_list,
        'dimensions': Dimension.objects.all()
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




