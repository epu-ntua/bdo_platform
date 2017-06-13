# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils.timezone import now


def home(request):
    return render(request, 'index.html', {
        'services': [
            {
                'title': 'Vessel positions',
                'label': 'Realtime',
                'updated': now() - timedelta(minutes=1),
                'service_type': {
                    'icon': 'file-archive-o',
                    'title': 'Dataset',
                    'color': 'blue',
                },
                'provider': 'EXMILE',
                'coverage': {
                    'location': 'Worldwide',
                },
                'stats': {'increase': 52, 'period': 'week'}
            },
            {
                'title': 'Density map of ship routes',
                'updated': now() - timedelta(minutes=7),
                'service_type': {
                    'icon': 'line-chart',
                    'title': 'Analysis',
                    'color': 'red',
                },
                'provider': 'NTUA',
                'stats': {'increase': 22, 'period': 'week'}
            },
            {
                'title': 'Wave energy production prediction',
                'updated': now() - timedelta(hours=2),
                'service_type': {
                    'icon': 'cloud',
                    'title': 'Analysis (Prediction)',
                    'color': 'green',
                },
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
                'service_type': {
                    'icon': 'line-chart',
                    'title': 'Analysis',
                    'color': 'red',
                },
                'provider': 'EXMILE',
                'stats': {'increase': 12, 'period': 'week'}
            },
            {
                'title': 'Vessel operations',
                'label': 'Realtime',
                'updated': now() - timedelta(days=5),
                'service_type': {
                    'icon': 'file-archive-o',
                    'title': 'Dataset',
                    'color': 'blue',
                },
                'provider': 'ANEK',
                'coverage': {
                    'location': 'Aegean See',
                },
                'stats': {'increase': 8, 'period': 'week'}
            },
        ]
    })

