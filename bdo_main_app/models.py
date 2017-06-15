# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.db import models
from django.utils.timezone import now

SERVICE_TYPES = [
    {
        'id': 'on_demand',
        'icon': 'life-saver',
        'title': 'On demand',
        'color': 'orange',
    },
    {
        'id': 'dataset',
        'icon': 'database',
        'title': 'Dataset',
        'color': 'blue',
    },
    {
        'id': 'analysis',
        'icon': 'industry',
        'title': 'Analysis',
        'color': 'red',
    },
    {
        'id': 'analysis_prediction',
        'icon': 'line-chart',
        'title': 'Analysis (Prediction)',
        'color': 'green',
    },
]


def get_service_type_by_id(id):
    return [st for st in SERVICE_TYPES if st['id'] == id][0]


SERVICES = [
    {
        'title': 'On Demand Data & Services',
        'updated': now() - timedelta(hours=2),
        'service_type': get_service_type_by_id(id='on_demand'),
        'provider': 'BigDataOcean',
        'url': '/on-demand/create/',
        'stats': {'increase': 78, 'period': 'week'},
        'moto': '<b>Get in touch</b> with <b>BigDataOcean</b> scientists to provide fully customized services for your company <b>today</b>!',
    },
    {
        'title': 'Vessel positions',
        'label': 'Realtime',
        'updated': now() - timedelta(minutes=1),
        'service_type': get_service_type_by_id(id='dataset'),
        'provider': 'EXMILE',
        'coverage': {
            'location': 'Worldwide',
        },
        'url': '/datasets/test-dataset/',
        'stats': {'increase': 52, 'period': 'week'}
    },
    {
        'title': 'Density map of ship routes',
        'updated': now() - timedelta(minutes=7),
        'service_type': get_service_type_by_id(id='analysis'),
        'provider': 'NTUA',
        'stats': {'increase': 22, 'period': 'week'}
    },
    {
        'title': 'Wave energy production prediction',
        'updated': now() - timedelta(hours=2),
        'service_type': get_service_type_by_id(id='analysis_prediction'),
        'provider': 'NESTER',
        'coverage': {
            'location': 'Portugal',
            'time': '2015 - today'
        },
        'stats': {'increase': 14, 'period': 'week'}
    },
    {
        'title': 'Anomaly detection in ship movement',
        'updated': now() - timedelta(minutes=44),
        'service_type': get_service_type_by_id(id='analysis'),
        'provider': 'EXMILE',
        'stats': {'increase': 12, 'period': 'week'}
    },
    {
        'title': 'Vessel operations',
        'label': 'Realtime',
        'updated': now() - timedelta(days=5),
        'service_type': get_service_type_by_id(id='dataset'),
        'url': '/datasets/test-dataset/',
        'provider': 'ANEK',
        'coverage': {
            'location': 'Aegean See',
        },
        'stats': {'increase': 8, 'period': 'week'}
    }]
