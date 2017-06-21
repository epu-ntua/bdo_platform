from __future__ import unicode_literals
# -*- coding: utf-8 -*-

from datetime import timedelta
from django.shortcuts import render
from django.utils.timezone import now

from bdo_main_app.models import EXTENDABLE_SERVICES


def pick_base_analysis(request):
    return render(request, 'basic-analytics/pick-base-analysis.html', {
        'sidebar_active': 'products',
        'base_analytics': EXTENDABLE_SERVICES,
    })
