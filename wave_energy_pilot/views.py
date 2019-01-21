# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from lists import *
from datasets import *

# Create your views here.
def init(request):

    return render(request, 'wave_energy_pilot/load_service.html', {'buoys_list': BUOYS, 'datasets_list': DATASETS})
