# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils.timezone import now

from aggregator.models import Dataset


def dataset(request, dataset_id):
    return render(request, 'services/datasets/index.html', {
        'sidebar_active': 'products',
        'dataset': Dataset.objects.get(pk=dataset_id),
    })





