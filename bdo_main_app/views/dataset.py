# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from aggregator.models import *
import prestodb
from django.conf import settings


def dataset(request, dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    rows_to_render = []
    variable_list_canonical = [v.safe_name for v in Variable.objects.filter(dataset=dataset)]
    variable_list_titles = [v.title for v in Variable.objects.filter(dataset=dataset)]
    variable_list_units = [v.unit for v in Variable.objects.filter(dataset=dataset)]
    dimension_list_canonical = [d.name for d in Dimension.objects.filter(variable=Variable.objects.filter(dataset=dataset)[0])]
    dimension_list_titles = [d.title for d in Dimension.objects.filter(variable=Variable.objects.filter(dataset=dataset)[0])]
    dimension_list_units = [d.unit for d in Dimension.objects.filter(variable=Variable.objects.filter(dataset=dataset)[0])]
    column_list_titles = variable_list_canonical+dimension_list_canonical
    column_list_units = variable_list_units+dimension_list_units
    column_list_string = ""
    for column in column_list_titles:
        column_list_string += ", " + column
    column_list_string = column_list_string[1:]
    if dataset.stored_at == "UBITECH_PRESTO":
        try:
            presto_credentials = settings.DATABASES['UBITECH_PRESTO']
            conn_presto = prestodb.dbapi.connect(
                host=presto_credentials['HOST'],
                port=presto_credentials['PORT'],
                user=presto_credentials['USER'],
                catalog=presto_credentials['CATALOG'],
                schema=presto_credentials['SCHEMA'],
            )
            cursor_presto = conn_presto.cursor()
            query = "SELECT " + column_list_string + " FROM " + str(dataset.table_name) + " LIMIT 5"
            print query
            cursor_presto.execute("SELECT " + column_list_string + " FROM " + str(dataset.table_name) + " LIMIT 5")
            rows_to_render = cursor_presto.fetchall()
        except Exception, e:
            print 'error'
            print str(e)

    return render(request, 'services/datasets/index.html', {
        'sidebar_active': 'products',
        'dataset': dataset,
        'rows_to_render': rows_to_render,
        'variable_list_titles': variable_list_titles,
        'dimension_list_titles': dimension_list_titles,
        'column_list': zip(column_list_titles, column_list_units)
    })





