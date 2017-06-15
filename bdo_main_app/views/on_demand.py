# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils.timezone import now

from bdo_main_app.models import SERVICES


def on_demand_request(request):
    return render(request, 'services/on_demand/create.html', {
        'sidebar_active': 'products',
    })





