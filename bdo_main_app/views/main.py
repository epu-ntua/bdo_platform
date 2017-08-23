# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils.timezone import now

from bdo_main_app.models import Service


def home(request):
    return render(request, 'index.html', {
        'sidebar_active': 'products',
        'services': Service.objects.filter(hidden=False)
    })


def search(request):
    return render(request, 'search.html', {
        'sidebar_active': 'products',
        'q': request.GET.get('q', ''),
        'facets': [],
        'results': Service.objects.filter(hidden=False),
    })




