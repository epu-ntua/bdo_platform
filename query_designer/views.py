# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bson import ObjectId
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from mongo_client import get_mongo_db, MongoResponse


from query_designer.api import *
from query_designer.lists import AGGREGATES
from query_designer.query import *

# from query_designer.mongo_api import *
# from query_designer.mongo_query import *


def index(request):
    return render(request, 'query_designer/index.html', {
        'sidebar_active': 'queries',
    })


def load_query(request, pk):
    q = Query.objects.get(pk=pk)

    return JsonResponse({
        'pk': q.pk,
        'title': q.title,
        'design': q.design,
    })


def simplified(request, pk=None):
    return render(request, 'query_designer/simplified.html')


@csrf_exempt
def save_query(request, pk=None):
    # create or update
    if not pk:
        current_user = request.user
        if current_user.is_authenticated():
            q = Query(user=current_user)
        else:
            q = Query(user=User.objects.get(username='BigDataOcean'))
    else:
        q = Query.objects.get(pk=pk)

    # document
    if 'document' in request.POST:
        try:
            doc = json.loads(request.POST.get('document', ''))
        except ValueError:
            return JsonResponse({'error': 'Invalid query document'}, status=400)

        q.document = doc

    # design
    if 'design' in request.POST:
        try:
            design = json.loads(request.POST.get('design', ''))
        except ValueError:
            return JsonResponse({'error': 'Invalid design'}, status=400)

        q.design = design
    else:
        q.design = None

    # title
    if 'title' in request.POST:
        q.title = request.POST.get('title', 'Untitled query')

    # save
    q.save()

    # return OK response
    return JsonResponse({
        'pk': q.pk,
        'title': q.title,
    })


def get_query_variables(request):
    if 'id' in request.GET:
        id = int(request.GET.get('id'))
        doc = None
        # existing saved query
        if id >= 0:
            # get the query
            q = Query.objects.get(pk=id)
            # get the document
            doc = q.document
        # new query
        else:
            if 'document' in request.GET:
                try:
                    doc = json.loads(request.GET.get('document', ''))
                except ValueError:
                    return JsonResponse({'error': 'Invalid query document'}, status=400)

        # find the query's SELECT variables formatted as: 'variable's column name': 'variable's name'
        variables = dict()
        for var in doc['from']:
            value_name = ''
            for col_name in var['select']:
                if col_name['type'] == 'VALUE':
                    value_name = col_name['name']
            variables[value_name] = var['name']

        # return the found variables
        return HttpResponse(json.dumps(variables), content_type="application/json")

    else:
        return JsonResponse({'error': 'Invalid query document'}, status=400)


def load_to_analysis(request):
    current_user = request.user
    if current_user.is_authenticated():
        q = Query(user=current_user)
    else:
        q = Query(user=User.objects.get(username='BigDataOcean'))

    # document
    if 'document' in request.GET:
        try:
            doc = json.loads(request.GET.get('document', ''))
        except ValueError:
            return JsonResponse({'error': 'Invalid query document'}, status=400)

        q.document = doc

    # title
    if 'title' in request.GET:
        q.title = request.GET.get('title', 'Untitled query')

    # return OK response
    return JsonResponse({
        'raw_query': q.raw_query,
        'title': q.title,
    })


def get_config(request):
    field_policy = {
        'categories': [],
        'defaultAggregate': 'AVG',
        'valueFields': [],
        'aggregates': [],
        'incrStep': 1,
        'min': 1,
        'max': 4
    }

    for dimension in Dimension.objects.all():
        field_policy['categories'].append({
            'title': '%s (%s)' % (dimension.title, dimension.variable.title),
            'value': dimension.name,
            'type': dimension.pk,
            'forVariable': dimension.variable.pk,
        })

    """
    for formula in Formula.objects.filter(created_by=user, is_valid=True):
        field_policy['valueFields'].append({
            'value': formula.internal_value,
            'title': formula.name,
        })
    """

    for variable in Variable.objects.all():
        field_policy['valueFields'].append({
            'value': variable.name,
            'title': variable.title,
            'type': variable.pk,
        })

    # pass aggregates
    for aggregate in AGGREGATES:
        field_policy['aggregates'].append({
            'title': aggregate[1],
            'value': aggregate[0],
        })

    # return the structure
    return JsonResponse(field_policy)


def list_queries(request):
    # ensure GET request
    if request.method != 'GET':
        return HttpResponse('Only `GET` method allowed', status=400)

    ctx = {
        'queries': Query.objects.filter(user=request.user if request.user.is_authenticated() else None),
    }

    return render(request, 'query_designer/utils/query-table.html', ctx)


def save_chart(request):
    # ensure POST request
    if request.method != 'POST':
        return HttpResponse('Only `POST` method allowed', status=400)

    # get the chart to update (or new chart)
    chart_id = request.POST.get('chart_id', '')
    chart_title = request.POST.get('title', '')
    chart_fields = request.POST.get('chart_options', '')
    chart_filters = request.POST.get('chart_filters', '')
    chart_type = request.POST.get('chart_type', '')
    chart_format = request.POST.get('chart_format', '')

    if chart_id:  # existing chart
        try:
            chart = Chart.objects.filter(Q(created_by=request.user) | Q(is_template=True)).get(pk=chart_id)
        except Chart.DoesNotExist as e:
            return HttpResponse('Chart not found', status=404)
    else:  # new chart
        # we need all the info in this case
        if not chart_title or not chart_fields:
            return HttpResponse('`title` and `fields` are both required for a new chart', status=400)

        chart = Chart(created_by=request.user)

    # update the provided fields
    if chart_title:
        chart.title = chart_title

    if chart_fields:
        # ensure json
        chart.fields = json.dumps(json.loads(chart_fields))

    if chart_type:
        chart.chart_type = chart_type

    if chart_format:
        chart.chart_format = chart_format

    if chart_filters:
        chart.filters = chart_filters

    # make sure to clone chart for templates
    if chart.is_template and not request.user.is_superuser:
        # change owner, mark as plain chart & save as new object
        chart.created_by = request.user
        chart.is_template = False
        chart.pk = None

    # save the chart
    chart.save()

    # send the ID
    return HttpResponse(chart.pk)


def delete_chart(request, pk):
    # ensure POST request
    if request.method != 'POST':
        return HttpResponse('Only `POST` method allowed', status=400)

    try:
        chart = Chart.objects.get(pk=pk, created_by=request.user)
    except Chart.DoesNotExist as e:
        return HttpResponse('Chart not found', status=404)

    # delete & send OK response
    chart.delete()
    return HttpResponse('', status=204)


def open_chart(request, pk):
    # ensure GET request
    if request.method != 'GET':
        return HttpResponse('Only `GET` method allowed', status=400)

    # check if chart exists & is owned by this user
    try:
        chart = Chart.objects.filter(Q(created_by=request.user) | Q(is_template=True)).get(pk=pk)
    except Chart.DoesNotExist as e:
        return HttpResponse('Chart not found', status=404)

    # return the chart info
    return JsonResponse({
        'title': chart.title,
        'chartType': chart.chart_type,
        'chartFormat': chart.chart_format,
        'chartOptions': json.loads(chart.fields),
        'chartFilters': chart.filters,
        'chartPolicy': get_field_policy(user=request.user,
                                        chart_type=chart.chart_type, chart_format=chart.chart_format),
    }, safe=True, encoder=DefaultEncoder)
