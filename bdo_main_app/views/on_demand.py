# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils.timezone import now

from bdo_main_app.models import SERVICES


def on_demand_create(request):
    return render(request, 'services/on_demand/create.html', {
        'sidebar_active': 'products',
    })


def on_demand_search(request):
    return render(request, 'services/on_demand/list.html', {
        'sidebar_active': 'products',
        'open_requests': [
            {
                'title': 'Wave heights in the Adriatic',
                'description': 'I need wave heights in the Adriatic sea, at least for the past two years!',
                'created': now() - timedelta(days=6),
                'votes': 4,
                'author': 'NESTER',
            },
            {
                'title': 'Visualize weather data affecting vessel paths',
                'description': 'Could anybody create a visualization showing how weather data affects a vessel\'s path?',
                'created': now() - timedelta(days=14),
                'votes': 7,
                'author': 'E. Biliri (Researcher)',
            },
        ],
        'closed_requests': [
            {
                'title': 'Run a correlation between Fe levels & vessel positions',
                'description': 'I want to correlate Iron concentration levels with vessel positions, anybody know who to do this?',
                'created': now() - timedelta(days=2),
                'votes': 1,
                'author': 'D. Papaspyros (Researcher)',
                'solved_by': 'J. Tsapelas (Data Scientist)'
            },
        ],
    })




