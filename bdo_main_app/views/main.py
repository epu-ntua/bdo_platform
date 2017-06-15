# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils.timezone import now

from bdo_main_app.models import SERVICES


def home(request):
    return render(request, 'index.html', {
        'sidebar_active': 'products',
        'services': SERVICES
    })


def search(request):
    return render(request, 'search.html', {
        'sidebar_active': 'products',
        'q': request.GET.get('q', ''),
        'facets': [],
        'results': SERVICES,
    })




