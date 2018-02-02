# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bson import ObjectId
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from mongo_client import get_mongo_db, MongoResponse


from query_designer.api import *
from query_designer.lists import AGGREGATES
from query_designer.query import *

import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

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
    return render(request, 'query_designer/simplified.html', {
        'dimensions': Dimension.objects.all(),
    })


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

        # find the query's SELECT variables formatted as: 'variable's column name (title)': 'variable's name'
        variables = dict()
        dimensions = dict()
        for from_clause in doc['from']:
            for col in from_clause['select']:
                if col['type'] == 'VALUE':
                    variables[col['title']] = col['name']
                else:
                    dimensions[col['title']] = col['name']

        result = {'variables': variables, 'dimensions': dimensions}
        # return the found variables
        return HttpResponse(json.dumps(result), content_type="application/json")

    else:
        return JsonResponse({'error': 'Invalid query document'}, status=400)


class DefaultEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, datetime.date):
            return o.isoformat()

        return super(DefaultEncoder, self).default(o)


def filter_info(request, filter_type, pk):
    if filter_type == 'variable':
        return JsonResponse({'type': 'number', 'orderable': True})

    dimension = Dimension.objects.get(pk=pk)

    values = dimension.ranges

    if type(values) == dict and 'min' in values:
        values.update({
            'type': 'text',
            'orderable': True,
        })

        return JsonResponse(values, encoder=DefaultEncoder)

    return JsonResponse({
        'type': 'select',
        'orderable': True,
        'options': [{
            'name': v,
            'value': v,
        } for v in values]
    }, encoder=DefaultEncoder)


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


def save_formulas(request):
    user = request.user if request.user.is_authenticated() else None

    # ensure POST request
    if request.method != 'POST':
        return HttpResponse('Only `POST` method allowed', status=400)

    try:
        formulas = json.loads(request.POST.get('formulas'))
    except ValueError:
        return HttpResponse('Invalid formula input', status=400)

    # list with formulas to remove -- assume all
    to_delete_ids = [f.pk for f in Formula.objects.filter(created_by=user)]

    result = []
    with transaction.atomic():
        for formula in formulas:

            if not formula.get('formulaName') or not formula.get('formulaValue'):
                return HttpResponse('`formula_name` and `formula_value` are both required for a formula', status=400)

            # save the formula
            try:
                if not formula['formulaId']:
                    raise Formula.DoesNotExist()

                fo = Formula.objects.get(pk=formula['formulaId'])
            except Formula.DoesNotExist:
                fo = Formula.objects.create(name=formula['formulaName'], created_by=user)

            fo.value = formula['formulaValue']
            fo.name = formula['formulaName']
            fo.save()

            # remove from to_delete list
            if fo.pk in to_delete_ids:
                to_delete_ids.pop(to_delete_ids.index(fo.pk))

            # validate formula
            result.append({
                'name': fo.name,
                'id': fo.pk,
                'errors': fo.errors(),
                'unit': fo.unit,
            })

    # delete any formula not submitted
    Formula.objects.filter(pk__in=to_delete_ids, created_by=user).delete()

    # respond
    return JsonResponse(result, safe=False)


def delete_formula(request):
    # ensure POST request
    if request.method != 'POST':
        return HttpResponse('Only `POST` method allowed', status=400)

    # get the formula info
    formula_name = request.POST.get('formula_name', '')

    try:
        formula = Formula.objects.get(name=formula_name, created_by=request.user if request.user.is_authenticated() else None)
    except Formula.DoesNotExist as e:
        return HttpResponse('Formula "%s" not found' % formula_name, status=404)

    # delete & send OK response
    formula.delete()
    return HttpResponse('', status=204)


def formulas(request):
    template = 'query_designer/utils/formula-editor.html'

    if request.is_ajax():
        template = 'query_designer/utils/formula-editor-content.html'
    return render(request, template, {
        'formulas': Formula.objects.filter(created_by=request.user if request.user.is_authenticated() else None).order_by('date_created'),
        'value_properties': [(v.name, v.title) for v in Variable.objects.all()] + [(d.name, d.title) for d in Dimension.objects.all()],
        'formula_functions': Formula.safe_function_info(),
    })


def new_template(request):
    return render(request, 'query_designer/new_template.html', {})
