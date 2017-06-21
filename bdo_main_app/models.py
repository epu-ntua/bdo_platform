# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from random import randint

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
        'color': 'green',
    },
]


def get_service_type_by_id(id):
    return [st for st in SERVICE_TYPES if st['id'] == id][0]


def get_base_analysis(pk, title, moto=''):
    base_analysis = {
        'pk': int(pk),
        'title': title,
        'updated': now() - timedelta(days=14),
        'service_type': get_service_type_by_id(id='analysis'),
        'extendable': True,
        'hide_from_search': True,
        'url': '/datasets/test-dataset/',
        'provider': 'BigDataOcean',
        'stats': {'increase': randint(5, 50), 'period': 'week'}
    }

    if moto:
        base_analysis['moto'] = moto

    return base_analysis

SERVICES = [
    {
        'pk': 1,
        'title': 'On Demand Data & Services',
        'updated': now() - timedelta(hours=2),
        'service_type': get_service_type_by_id(id='on_demand'),
        'provider': 'BigDataOcean',
        'url': '/on-demand/',
        'stats': {'increase': 78, 'period': 'week'},
        'moto': '<b>Get in touch</b> with <b>BigDataOcean</b> scientists to provide fully customized services for your company <b>today</b>!',
    },
    {
        'pk': 2,
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
        'pk': 3,
        'title': 'Density map of ship routes',
        'updated': now() - timedelta(minutes=7),
        'service_type': get_service_type_by_id(id='analysis'),
        'provider': 'NTUA',
        'stats': {'increase': 22, 'period': 'week'}
    },
    {
        'pk': 4,
        'title': 'Wave energy production prediction',
        'updated': now() - timedelta(hours=2),
        'service_type': get_service_type_by_id(id='analysis'),
        'provider': 'NESTER',
        'coverage': {
            'location': 'Portugal',
            'time': '2015 - today'
        },
        'stats': {'increase': 14, 'period': 'week'}
    },
    {
        'pk': 5,
        'title': 'Anomaly detection in ship movement',
        'updated': now() - timedelta(minutes=44),
        'service_type': get_service_type_by_id(id='analysis'),
        'provider': 'EXMILE',
        'stats': {'increase': 12, 'period': 'week'}
    },
    {
        'pk': 6,
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
    },

    # Base analytics
    # Not exposed
    get_base_analysis(7, 'Clustering',
                      'Automatically categorises data into various groups (<em>clusters</em>)'),
    get_base_analysis(8, 'Regression',
                      'Helps you identify possible correlations between two or more different variables'),
    get_base_analysis(9, 'Decision tree',
                      'Generates a tree model that will be used for classifying ' +
                      'your data base on a <em>training</em> dataset'),
    get_base_analysis(10, 'Classification',
                      'Categorises data given that you classify manually some data for <em>training</em>'),
    get_base_analysis(11, 'Recommendation',
                      'Proposes recommendations based on a training dataset of historical actions'),
    get_base_analysis(12, 'Association rules',
                      'Generates a set of rules that associate different events with each other'),
]


EXPOSED_SERVICES = [s for s in SERVICES if 'hide_from_search' not in s or not s['hide_from_search']]
EXTENDABLE_SERVICES = [s for s in SERVICES if 'extendable' in s and s['extendable']]


def get_service_by_id(pk):
    return [s for s in SERVICES if s['pk'] == pk][0]
