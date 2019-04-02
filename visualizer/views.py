from __future__ import unicode_literals, division
# -*- coding: utf-8 -*-
import prestodb
from django.conf import settings
from django.http.response import HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect
from django.db import connection, connections
from rest_framework.views import APIView
from forms import MapForm
import time
from django.db import ProgrammingError

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import namedtuple
import os, re, time
from nvd3 import pieChart, lineChart
import psycopg2

from django.template.loader import render_to_string

from service_builder.models import ServiceInstance
from service_builder.views import updateServiceInstanceVisualizations
import numpy as np

import matplotlib
from matplotlib import use
# import matplotlib.pyplot as plt
from matplotlib.figure import Figure
use('Agg')
import matplotlib.pyplot as plt
import pylab as pl
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import time
import traceback
from query_designer.models import TempQuery
from visualizer.models import Visualization
from aggregator.models import *

from utils import *
from tests import *

from folium import CustomIcon
from folium.plugins import HeatMap, MarkerCluster
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

FOLIUM_COLORS = ['red', 'blue', 'gray', 'darkred', 'lightred', 'orange', 'beige', 'green', 'darkgreen', 'lightgreen', 'darkblue',
                 'lightblue', 'purple', 'darkpurple', 'pink', 'cadetblue', 'lightgray']

AGGREGATE_VIZ = ['max', 'min', 'avg', 'sum', 'count']


def get_vessel_ids_info(request, query_id):
    return_dict = dict()
    q = AbstractQuery.objects.get(pk=int(query_id))
    dataset_list = []
    for el in q.document['from']:
        dataset_list.append(Variable.objects.get(id=int(el['type'])).dataset)
    for dataset in set(dataset_list):
        for vi in dataset.vessel_identifiers.all():
            return_dict[vi.column_name] = [x[0] for x in vi.values_list[:1000]]
    # print return_dict[:2]
    return JsonResponse(return_dict)


def get_data_parameters(request, layer_count):
    query_pk = str(request.GET.get('query'+layer_count, '0'))
    try:
        query_pk = int(query_pk)
    except ValueError:
        raise ValueError('The given Query ID not valid.')
    df = str(request.GET.get('df'+layer_count, ''))
    notebook_id = str(request.GET.get('notebook_id'+layer_count, ''))
    return query_pk, df, notebook_id


def get_contour_parameters(request, count):
    cached_file = str(request.GET.get('cached_file_id' + str(count), str(time.time()).split('.')[0]))
    n_contours = str(request.GET.get('n_contours' + str(count), 20))
    try:
        n_contours = int(n_contours)
    except ValueError:
        raise ValueError('Number of contours is not valid.')
    step = str(request.GET.get('step' + str(count), 0.1))
    try:
        step = float(step)
    except ValueError:
        raise ValueError('Step is not valid.')
    variable = str(request.GET.get('contour_var' + str(count), ''))
    if variable == '':
        raise ValueError('A variable has to be selected for the contours to be created on the map.')

    agg_function = str(request.GET.get('agg_func', 'avg'))
    if not agg_function.lower() in AGGREGATE_VIZ:
        raise ValueError('The given aggregate function is not valid.')

    return cached_file, n_contours, step, variable, agg_function


def get_markers_parameters(request, count):
    cached_file = str(request.GET.get('cached_file_id' + str(count), str(time.time()).split('.')[0]))
    marker_limit = str(request.GET.get("marker_limit" + str(count), '1'))
    try:
        vessel_id_column = str(request.GET.get("vessel-id-columns-select" + str(count), ''))
        vessel_id = request.GET.getlist("vessel-id" + str(count)+'[]', '')
    except ValueError:
        raise ValueError('Platform ID has a numeric value.(cannot be empty)')
    try:
        marker_limit = int(marker_limit)
    except ValueError:
        raise ValueError('Number of positions is not valid.')
    if marker_limit <= 0:
        raise ValueError('Number of positions has to be a positive number.')
    variable = str(request.GET.get('variable' + str(count), ''))
    if variable == '':
        raise ValueError('A variable has to be selected for each marker to show its value in a specific location.')
    agg_function = str(request.GET.get('agg_func', 'avg'))
    if not agg_function.lower() in AGGREGATE_VIZ:
        raise ValueError('The given aggregate function is not valid.')
    use_color_col = request.GET.get('use_existing_temp_res'+str(count), '') == 'on'
    color_col = str(request.GET.get('color_var'+str(count), ''))
    lat_col = str(request.GET.get('lat_col' + str(count), 'latitude'))
    lon_col = str(request.GET.get('lon_col' + str(count), 'longitude'))
    return cached_file, variable, vessel_id_column, vessel_id, color_col, marker_limit, use_color_col, agg_function, lat_col, lon_col


def get_plotline_parameters(request, count):
    cached_file = str(request.GET.get('cached_file_id' + str(count), str(time.time()).split('.')[0]))
    try:
        vessel_id_column = str(request.GET.get("vessel-id-columns-select" + str(count), ''))
        vessel_id = str(request.GET.get("vessel-id" + str(count), ''))
    except ValueError:
        raise ValueError('Platform ID has a numeric value.(cannot be empty)')
    color = str(request.GET.get('plotline_color' + str(count), 'blue'))
    if color not in FOLIUM_COLORS:
        raise ValueError('The chosen color is not supported.')
    marker_limit = str(request.GET.get("points_limit" + str(count), '1'))
    try:
        marker_limit = int(marker_limit)
    except ValueError:
        raise ValueError('Number of positions is not valid.')
    if marker_limit <= 0:
        raise ValueError('Number of positions has to be a positive number.')
    lat_col = str(request.GET.get('lat_col' + str(count), 'lat'))
    lon_col = str(request.GET.get('lon_col' + str(count), 'lon'))
    return cached_file, marker_limit, vessel_id_column, vessel_id, color, lat_col, lon_col

def get_heatmap_parameters(request, count):
    cached_file = str(request.GET.get('cached_file_id' + str(count), str(time.time()).split('.')[0]))
    lat_col = str(request.GET.get('lat_col' + str(count), 'latitude'))
    lon_col = str(request.GET.get('lon_col' + str(count), 'longitude'))
    heat_col = str(request.GET.get('heat_col' + str(count), ''))
    if heat_col == '':
        raise ValueError('The heatmap variable has to be selected.')
    heat_points_limit = str(request.GET.get("points_limit" + str(count), '1'))
    try:
        heat_points_limit = int(heat_points_limit)
    except ValueError:
        raise ValueError('Number of heatmap points is not valid.')
    if heat_points_limit <= 0:
        raise ValueError('Number of heatmap points has to be a positive number.')
    return cached_file, heat_col, heat_points_limit, lat_col,lon_col


def load_modify_query_marker_vessel(query_pk, variable, marker_limit, vessel_column, vessel_id, color_col, agg_function, use_color_col):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document
    time_flag = platform_flag = lat_flag = lon_flag = var_flag = color_flag = False

    for f in doc['from']:
        for s in f['select']:
            if (s['name'].split('_', 1)[1] == 'time') and (s['exclude'] is not True):
                order_var = s['name']
                s['groupBy'] = True
                if s['aggregate'] == '':
                    s['aggregate'] = 'date_trunc_hour'
                time_flag = True
            elif s['name'] == color_col and (s['exclude'] is not True):
                s['exclude'] = False
                # s['aggregate'] = agg_function
                s['groupBy'] = True
                color_flag = True
                if (s['name'].split('_', 1)[1] == vessel_column) and (s['exclude'] is not True):
                    platform_id_filtername = str(s['name'])
                    if str(s['type']) == "VALUE":
                        platform_id_datatype = Variable.objects.get(pk=int(f['type'])).dataType
                    else:
                        platform_id_datatype = Dimension.objects.get(pk=int(s['type'])).dataType
                    platform_flag = True
            elif(s['name'] == variable) and (s['exclude'] is not True):
                s['exclude'] = False
                if s['datatype'] == 'STRING':
                    s['aggregate'] = 'MIN'
                elif s['datatype'] == 'TIMESTAMP':
                    s['aggregate'] = 'MIN'
                else:
                    s['aggregate'] = 'AVG'
                var_flag = True
                if (s['name'].split('_', 1)[1] == vessel_column) and (s['exclude'] is not True):
                    platform_id_filtername = str(s['name'])
                    if str(s['type']) == "VALUE":
                        platform_id_datatype = Variable.objects.get(pk=int(f['type'])).dataType
                    else:
                        platform_id_datatype = Dimension.objects.get(pk=int(s['type'])).dataType
                    platform_flag = True
            elif (s['name'].split('_', 1)[1] == vessel_column) and (s['exclude'] is not True):
                platform_id_filtername = str(s['name'])
                s['exclude'] = True
                if str(s['type']) == "VALUE":
                    platform_id_datatype = Variable.objects.get(pk=int(f['type'])).dataType
                else:
                    platform_id_datatype = Dimension.objects.get(pk=int(s['type'])).dataType
                platform_flag = True
            elif (s['name'].split('_', 1)[1] == 'latitude') and (s['exclude'] is not True):
                s['exclude'] = False
                # s['groupBy'] = True
                if s['aggregate'] == '':
                    s['aggregate'] = 'round1'
                s['groupBy'] = True
                lat_flag = True
            elif (s['name'].split('_', 1)[1] == 'longitude') and (s['exclude'] is not True):
                s['exclude'] = False
                if s['aggregate'] == '':
                    s['aggregate'] = 'round1'
                s['groupBy'] = True
                lon_flag = True
            else:
                s['exclude'] = True

    if not time_flag:
        raise ValueError('Time is not a dimension of the chosen query. The requested visualisation cannot be executed.')
    else:
        # doc['orderings'] = doc['orderings'].append({'name': order_var, 'type': 'ASC'})
        found = False
        for ord in doc['orderings']:
            if ord['name'] == order_var:
                found = True
        if not found:
            doc['orderings'].append({'name': order_var, 'type': 'ASC'})

    if not platform_flag:
        raise ValueError('Ship/Vessel/Route/Platform ID is not a dimension of the chosen query. The requested visualisation cannot be executed.')
    else:
        if vessel_id == '':
            vessel_id = []

        doc['filters'] = filtering_vessels(doc, vessel_id, platform_id_filtername, platform_id_datatype)

    if not lat_flag or not lon_flag:
        raise ValueError('Latitude and Longitude are not dimensions of the chosen query. The requested visualisation cannot be executed.')

    if not var_flag:
        raise ValueError('The variable is missing from the selected query. The requested visualisation cannot be executed.')
    doc['limit'] = marker_limit

    if use_color_col:
        if not color_flag:
            raise ValueError('A variable or dimension has to be selected, if color separation is enabled.')

    query.document = doc
    return query


def load_modify_query_marker_grid(query_pk, variable, marker_limit, agg_function):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document
    lat_flag = lon_flag = var_flag = False

    for f in doc['from']:
        for s in f['select']:
            if(s['name'] == variable) and (s['exclude'] is not True):
                s['exclude'] = False
                s['aggregate'] = agg_function
                var_flag = True
            elif (s['name'].split('_', 1)[1] == 'latitude') and (s['exclude'] is not True):
                s['exclude'] = False
                s['groupBy'] = True
                if s['aggregate'] == '':
                    s['aggregate'] = 'round2'
                lat_flag = True
            elif (s['name'].split('_', 1)[1] == 'longitude') and (s['exclude'] is not True):
                s['exclude'] = False
                if s['aggregate'] == '':
                    s['aggregate'] = 'round2'
                s['groupBy'] = True
                lon_flag = True
            elif (s['name'].split('_', 1)[1] == 'time') and (s['exclude'] is not True):
                # s['exclude'] = True
                s['groupBy'] = False
                # if s['aggregate'] == '':
                s['aggregate'] = 'MAX'
            else:
                if s['datatype'] == 'STRING':
                    s['aggregate'] = 'MIN'
                elif s['datatype'] == 'TIMESTAMP':
                    s['aggregate'] = 'MIN'
                else:
                    s['aggregate'] = 'AVG'
                # s['exclude'] = True

    if not lat_flag or not lon_flag:
        raise ValueError('Latitude and Longitude are not dimensions of the chosen query. The requested visualisation cannot be executed.')

    if not var_flag:
        raise ValueError('The variable is missing from the selected query. The requested visualisation cannot be executed.')
    doc['limit'] = marker_limit

    query.document = doc
    return query


def load_modify_query_plotline_vessel(query_pk, marker_limit, vessel_column, vessel_id):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document
    time_flag = platform_flag = lat_flag = lon_flag = False
    for f in doc['from']:
        for s in f['select']:
            if (s['name'].split('_', 1)[1] == 'time') and (s['exclude'] is not True):
                order_var = s['name']
                s['groupBy'] = True
                if s['aggregate'] == '':
                    s['aggregate'] = 'date_trunc_minute'
                time_flag = True
            elif (s['name'].split('_', 1)[1] == vessel_column) and (s['exclude'] is not True):
                platform_id_filtername = str(s['name'])
                s['exclude'] = False
                s['groupBy'] = True
                if str(s['type']) == "VALUE":
                    platform_id_datatype = Variable.objects.get(pk=int(f['type'])).dataType
                else:
                    platform_id_datatype = Dimension.objects.get(pk=int(s['type'])).dataType
                platform_flag = True
            elif (s['name'].split('_', 1)[1] == 'latitude') and (s['exclude'] is not True):
                s['exclude'] = False
                if s['aggregate'] == '':
                    s['aggregate'] = 'round1'
                s['groupBy'] = True
                lat_flag = True
            elif (s['name'].split('_', 1)[1] == 'longitude') and (s['exclude'] is not True):
                s['exclude'] = False
                if s['aggregate'] == '':
                    s['aggregate'] = 'round1'
                s['groupBy'] = True
                lon_flag = True
            else:
                s['exclude'] = True
    if not time_flag:
        raise ValueError('Time is not a dimension of the chosen query. The requested visualisation cannot be executed.')
    else:
        # doc['orderings'] = doc['orderings'].append({'name': order_var, 'type': 'ASC'})
        doc['orderings'] = [{'name': order_var, 'type': 'ASC'}]
    if not platform_flag:
        raise ValueError('Ship/Vessel/Route/Platform ID is not a dimension of the chosen query. The requested visualisation cannot be executed.')
    else:
        if vessel_id == '':
            vessel_id = []
        else:
            vessel_id = [vessel_id]
        doc['filters'] = filtering_vessels(doc, vessel_id, platform_id_filtername, platform_id_datatype)

    if not lat_flag or not lon_flag:
        raise ValueError('Latitude and Longitude are not dimensions of the chosen query. The requested visualisation cannot be executed.')

    doc['limit'] = marker_limit

    query.document = doc
    return query


def filtering_vessels(doc, vessel_id, platform_id_filtername, platform_id_datatype):
    # import pdb
    # pdb.set_trace()
    if len(vessel_id) > 0:
        vessel_argument = ''
        for vessel in vessel_id:
            if vessel_argument.__len__() == 0:
                if platform_id_datatype == "STRING":
                    vessel_argument = json.loads(
                        '{"a":"' + str(platform_id_filtername) + '", "b": "\'' + str(vessel) + '\'", "op": "eq"}')
                else:
                    vessel_argument = json.loads(
                        '{"a":"' + str(platform_id_filtername) + '", "b": ' + str(vessel) + ', "op": "eq"}')
            else:
                alpha_argument = vessel_argument
                if platform_id_datatype == "STRING":
                    beta_argument = json.loads(
                        '{"a":"' + str(platform_id_filtername) + '", "b": "\'' + str(vessel) + '\'", "op": "eq"}')
                else:
                    beta_argument = json.loads(
                        '{"a":"' + str(platform_id_filtername) + '", "b": ' + str(vessel) + ', "op": "eq"}')
                vessel_argument = json.loads(
                    '{"a":' + json.dumps(alpha_argument) + ', "b":' + json.dumps(beta_argument) + ', "op": "OR"}')
        if doc['filters'].__len__() == 0:
            doc['filters'] = vessel_argument
        else:
            alpha_argument = doc["filters"]
            beta_argument = vessel_argument
            doc['filters'] = json.loads(
                '{"a":' + json.dumps(alpha_argument) + ', "b":' + json.dumps(beta_argument) + ', "op": "AND"}')
    # print 'Vessel course filters'
    # print doc['filters']
    return doc['filters']


def load_modify_query_polygon(query_pk, marker_limit):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document
    lat_flag = lon_flag = False

    for f in doc['from']:
        for s in f['select']:
            if (s['name'].split('_', 1)[1] == 'latitude') and (s['exclude'] is not True):
                s['exclude'] = False
                lat_flag = True
            elif (s['name'].split('_', 1)[1] == 'longitude') and (s['exclude'] is not True):
                s['exclude'] = False
                lon_flag = True
            else:
                s['exclude'] = True

    if not lat_flag or not lon_flag:
        raise ValueError('Latitude and Longitude are not dimensions of the chosen query. The requested visualisation cannot be executed.')

    doc['limit'] = marker_limit

    query.document = doc
    return query


def load_modify_query_polygon_for_dataset_coverage(query_pk, aggregate):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document
    lat_flag = lon_flag = False
    for f in doc['from']:
        for s in f['select']:
            if (s['name'].split('_', 1)[1] == 'latitude') and (s['exclude'] is not True):
                s['exclude'] = False
                s['aggregate'] = aggregate
                lat_flag = True
            elif (s['name'].split('_', 1)[1] == 'longitude') and (s['exclude'] is not True):
                s['exclude'] = False
                s['aggregate'] = aggregate
                lon_flag = True
            else:
                s['exclude'] = True
    if not lat_flag or not lon_flag:
        raise ValueError('Latitude and Longitude are not dimensions of the chosen query. The requested visualisation cannot be executed.')

    query.document = doc
    return query


def load_modify_query_map(query_pk, variable, order_var, lat_col, lon_col, color_col, marker_limit, auto_order=False):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document

    time_flag = False
    if auto_order == True:
        for f in doc['from']:
            for s in f['select']:
                if (s['name'].split('_', 1)[1] == 'time') and (s['exclude'] is not True):
                    order_var = s['name']
                    time_flag = True

    if auto_order == True and time_flag == False:
        raise ValueError('Time is not a dimension of the chosen query. The requested visualisation cannot be executed.')

    for f in doc['from']:
        for s in f['select']:
            if s['name'] == variable:
                s['exclude'] = False
            elif s['name'] == order_var:
                s['exclude'] = False
            elif s['name'] == color_col:
                s['exclude'] = False
            elif s['name'] == lat_col:
                s['exclude'] = False
            elif s['name'] == lon_col:
                s['exclude'] = False
            else:
                s['exclude'] = True

    if order_var != '':
        doc['orderings'] = doc['orderings'].append({'name': order_var, 'type': 'ASC'})
    if marker_limit != '':
        doc['limit'] = marker_limit

    query.document = doc
    return query


def load_modify_query_heatmap(query_pk, heat_col, marker_limit):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document
    lat_flag = lon_flag = heat_col_flag = False
    for f in doc['from']:
        for s in f['select']:
            if (s['name'] == heat_col) and (s['exclude'] is not True):
                s['exclude'] = False
                heat_col_flag = True
                if s['aggregate'] == '':
                    if s['datatype'] == 'STRING':
                        s['aggregate'] = 'MIN'
                    elif s['datatype'] == 'TIMESTAMP':
                        s['aggregate'] = 'MIN'
                    else:
                        s['aggregate'] = 'AVG'
            elif s['name'].split('_', 1)[1] == 'latitude':
                s['exclude'] = False
                lat_flag = True
                # if heat_col == 'heatmap_frequency':
                s['aggregate'] = 'round2'
                s['groupBy'] = True
            elif s['name'].split('_', 1)[1] == 'longitude':
                s['exclude'] = False
                lon_flag = True
                # if heat_col == 'heatmap_frequency':
                s['aggregate'] = 'round2'
                s['groupBy'] = True
            else:
                s['exclude'] = True
                s['aggregate'] = ''
                s['groupBy'] = False

    if not heat_col_flag:
        if heat_col != 'heatmap_frequency':
            raise ValueError(
                'The heatmap variable must be either a variable from the selected query or "Frequency".')

    if not lat_flag or not lon_flag:
        raise ValueError('Latitude and Longitude are not dimensions of the chosen query. The requested visualisation cannot be executed.')

    doc['limit'] = marker_limit

    query.document = doc
    return query


def load_modify_query_contours(agg_function, query_pk, round_num, variable):
    query = AbstractQuery.objects.get(pk=int(query_pk))
    query = TempQuery(document=query.document)
    doc = query.document

    doc['orderings'] = []
    doc['limit'] = []
    var_query_id = variable[:variable.find('_')]
    lat_flag = lon_flag = cont_var_flag = False
    for f in doc['from']:
        right_var = False
        for s in f['select']:
            # import pdb
            # pdb.set_trace()
            if s['name'] == variable and (s['exclude'] is not True):
                s['aggregate'] = agg_function
                s['exclude'] = False
                cont_var_flag = True
                right_var = True
            # elif s['name'].split('_', 1)[1] == 'latitude' and str(s['name']).find(var_query_id) >= 0 and s['exclude'] is not True:
            elif s['name'].split('_', 1)[1] == 'latitude':
                s['groupBy'] = True
                s['aggregate'] = 'round' + str(round_num)
                s['exclude'] = False
                doc['orderings'].append({'name': str(s['name']), 'type': 'ASC'})
                lat_flag = True
            # elif s['name'].split('_', 1)[1] == 'longitude' and str(s['name']).find(var_query_id) >= 0 and s['exclude'] is not True:
            elif s['name'].split('_', 1)[1] == 'longitude':
                s['groupBy'] = True
                s['aggregate'] = 'round' + str(round_num)
                s['exclude'] = False
                doc['orderings'].insert(0, {'name': str(s['name']), 'type': 'ASC'})
                lon_flag = True
            else:
                s['exclude'] = True
                s['groupBy'] = False

    if not lat_flag or not lon_flag:
        raise ValueError('Latitude and Longitude are not dimensions of the chosen query. The requested visualisation cannot be executed.')
    if not cont_var_flag:
        raise ValueError('The feature variable is missing from the selected query. The requested visualisation cannot be executed.')

    return query



def create_map():
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 30
    min_zoom = 2

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   min_zoom=min_zoom,
                   max_bounds=True,
                   tiles=tiles_str + token_str,
                   attr=attr_str)

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True).add_to(m)
    return m


def map_visualizer(request):
    m = create_map()
    js_list = []
    old_map_id_list = []
    extra_js = ""
    try:
        try:
            layer_count = int(request.GET.get("layer_count", 0))
        except ValueError:
            raise ValueError('Layer counter is not valid.')

        for count in range(0, layer_count):
            try:
                layer_id = int(request.GET.get("viz_id" + str(count)))
            except ValueError:
                raise ValueError('Visualisation ID of layer ' + str(count) + 'is not valid.')

            query_pk, df, notebook_id = get_data_parameters(request, str(count))
            # Plotline VesselCourse
            try:
                if (layer_id == Visualization.objects.get(view_name='get_map_plotline_vessel_course').id):
                    cached_file, marker_limit, vessel_column, vessel_id, color, lat_col, lon_col = get_plotline_parameters(request, count)
                    m, extra_js = get_map_plotline_vessel_course(marker_limit, vessel_column, vessel_id, color, query_pk, df, notebook_id, lat_col,
                                               lon_col, m, request, cached_file)
            except ObjectDoesNotExist:
                pass
            # Map Polygon - Line
            try:
                if (layer_id == Visualization.objects.get(view_name='get_map_polygon').id):
                    cached_file, marker_limit, null_var1, null_var2, color, lat_col, lon_col = get_plotline_parameters(
                        request, count)
                    m, extra_js = get_map_polygon(marker_limit, color, query_pk, df,
                                                                 notebook_id, lat_col,
                                                                 lon_col, m, request, cached_file)
            except ObjectDoesNotExist:
                pass
            # Map Polygon - For dataset coverage
            try:
                if (layer_id == Visualization.objects.get(view_name='get_map_polygon_for_dataset_coverage').id):
                    dataset_id = str(request.GET.get('dataset_id'))
                    m, extra_js = get_map_polygon_for_dataset_coverage(dataset_id, m)
            except ObjectDoesNotExist:
                pass
            # Map Grid - For dataset coverage
            try:
                if (layer_id == Visualization.objects.get(view_name='get_map_markers_grid_for_dataset_coverage').id):
                    dataset_id = str(request.GET.get('dataset_id'))
                    cached_file, variable, platform_id, color_col, marker_limit, use_color_column, agg_function, lat_col, lon_col = get_markers_parameters(request, count)
                    query_pk = load_modify_query_for_grid_coverage(dataset_id, marker_limit)
                    variable = AbstractQuery.objects.get(pk=int(query_pk)).document['from'][0]['select'][0]['name']
                    m, extra_js = get_map_markers_grid(query_pk, df, notebook_id, marker_limit,
                                                       variable, agg_function,
                                                       lat_col, lon_col, m,
                                                       request, cached_file, dataset_id)
            except ObjectDoesNotExist:
                pass

            # Heatmap
            try:
                if layer_id == Visualization.objects.get(view_name='get_map_heatmap').id:
                    cached_file, heat_col, heat_points_limit, lat_col, lon_col = get_heatmap_parameters(request,
                                                                                                        count)
                    m, extra_js = get_map_heatmap(query_pk, df, notebook_id, lat_col, lon_col, heat_col,
                                                  heat_points_limit, m, cached_file, request)
            except ObjectDoesNotExist:
                pass
            # Contours
            try:
                if (layer_id == Visualization.objects.get(view_name='get_map_contour').id):
                    cached_file, n_contours, step, variable, agg_function = get_contour_parameters(request, count)
                    m, extra_js, old_map_id = get_map_contour(n_contours, step, variable, query_pk, agg_function, m,
                                                                     cached_file)
                    old_map_id_list.append(old_map_id)
            except ObjectDoesNotExist:
                pass
                # Map Markers Course Vessel
            try:
                if (layer_id == Visualization.objects.get(view_name='get_map_markers_vessel_course').id):
                    cached_file, variable, vessel_column, vessel_id, color_col, marker_limit, use_color_column, agg_function, lat_col, lon_col = get_markers_parameters(request, count)
                    m, extra_js = get_map_markers_vessel_course(query_pk, df, notebook_id, marker_limit, vessel_column, vessel_id, variable, agg_function,
                                             lat_col, lon_col, color_col, use_color_column, m, request, cached_file)
            except ObjectDoesNotExist:
                pass
                # Map Markers Grid
            try:
                if (layer_id == Visualization.objects.get(view_name='get_map_markers_grid').id):
                    cached_file, variable, vessel_column, vessel_id, color_col, marker_limit, use_color_column, agg_function, lat_col, lon_col = get_markers_parameters(
                        request, count)
                    m, extra_js = get_map_markers_grid(query_pk, df, notebook_id, marker_limit,
                                                                variable, agg_function,
                                                                lat_col, lon_col, m,
                                                                request, cached_file)
            except ObjectDoesNotExist:
                pass

            if (extra_js != ""):
                js_list.append(extra_js)
    except (ValueError, Exception) as e:
        traceback.print_exc()
        return render(request, 'error_page.html', {'message': e.message})

    folium.LayerControl().add_to(m)
    temp_map = 'templates/map1'+str(int(time.time()))+'.html'
    m.save(temp_map)
    map_html = open(temp_map, 'r').read()
    soup = BeautifulSoup(map_html, 'html.parser')
    map_id = soup.find("div", {"class": "folium-map"}).get('id')
    js_all = soup.findAll('script')

    # changes the wrong map_id's for all the extra scripts used
    for mid in old_map_id_list:
        for js in js_list:
            js.replace(mid, map_id)

    # print(js_all)
    if len(js_all) > 5:
        js_all = [js.prettify() for js in js_all[5:]]
    # print(js_all)
    if js_list:
        js_all.extend(js_list)
    css_all = soup.findAll('link')
    if len(css_all) > 3:
        css_all = [css.prettify() for css in css_all[3:]]
    # js_all = [js.replace('worldCopyJump', 'preferCanvas: false , worldCopyJump') for js in js_all]
    html1 = render_to_string('visualizer/final_map_folium_template.html',
                             {'map_id': map_id, 'js_all': js_all, 'css_all': css_all})
    # print(html1)
    return HttpResponse(html1)



def get_map_plotline_vessel_query_data(query):
    try:
        query_data = execute_query_method(query)
    except:
        raise ValueError('The requested visualisation cannot be executed for the chosen query.')
    data = query_data[0]['results']
    result_headers = query_data[0]['headers']

    time_index = lat_index = lon_index = -1
    for idx, c in enumerate(result_headers['columns']):
        if c['name'].split('_', 1)[1] == 'latitude':
            lat_index = idx
        elif c['name'].split('_', 1)[1] == 'longitude':
            lon_index = idx
        elif c['name'].split('_', 1)[1] == 'time':
            time_index = idx
    return data, lat_index, lon_index, time_index




def get_map_plotline_vessel_course(marker_limit, vessel_column, vessel_id, color, query_pk, df, notebook_id, lat_col, lon_col, m, request, cached_file):
    dict = {}
    if not os.path.isfile('visualizer/static/visualizer/temp/' + cached_file):
        if query_pk != 0:
            query = load_modify_query_plotline_vessel(query_pk, marker_limit, vessel_column, vessel_id)
            data, lat_index, lon_index, time_index = get_map_plotline_vessel_query_data(query)
            points, min_lat, max_lat, min_lon, max_lon = create_plotline_points(data, lat_index, lon_index)

        elif df != '':
            data, y_m_unit, y_title_list = get_chart_dataframe_data(request, notebook_id, df, '', [], False)
            points, min_lat, max_lat, min_lon, max_lon = create_plotline_points(data, lat_col, lon_col)
        else:
            raise ValueError('Either query ID or dataframe name has to be specified.')

        dict['min_lat'] = min_lat
        dict['max_lat'] = max_lat
        dict['min_lon'] = min_lon
        dict['max_lon'] = max_lon
        dict['points'] = points
        # create cached file with necessary data and info
        with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
            json.dump(dict, f)
    else:
        print('Plotline Data is Cached!')
        with open('visualizer/static/visualizer/temp/' + cached_file) as f:
            cached_data = json.load(f)
        min_lat = cached_data['min_lat']
        max_lat = cached_data['max_lat']
        min_lon = cached_data['min_lon']
        max_lon = cached_data['max_lon']

        points = cached_data['points']

    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])

    pol_group_layer = folium.map.FeatureGroup(name='Plotline - Layer:' + str(time.time()).replace(".","_") + ' / Ship ID: ' + str(vessel_id), overlay=True,
                                              control=True).add_to(m)
    folium.PolyLine(points, color=color, weight=2.5, opacity=0.8,
                    ).add_to(pol_group_layer)
    if points.__len__() != 0:
        create_plotline_arrows(points, m, pol_group_layer, color)
    ret_html = ""
    return m, ret_html


def get_map_polygon(marker_limit, color, query_pk, df, notebook_id, lat_col, lon_col, m, request, cached_file):
    dict = {}
    if not os.path.isfile('visualizer/static/visualizer/temp/' + cached_file):
        if query_pk != 0:
            query = load_modify_query_polygon(query_pk, marker_limit)
            data, lat_index, lon_index, time_index = get_map_plotline_vessel_query_data(query)
            points, min_lat, max_lat, min_lon, max_lon = create_plotline_points(data, lat_index, lon_index)

        elif df != '':
            data, y_m_unit, y_title_list = get_chart_dataframe_data(request, notebook_id, df, '', [], False)
            points, min_lat, max_lat, min_lon, max_lon = create_plotline_points(data, lat_col, lon_col)
        else:
            raise ValueError('Either query ID or dataframe name has to be specified.')

        dict['min_lat'] = min_lat
        dict['max_lat'] = max_lat
        dict['min_lon'] = min_lon
        dict['max_lon'] = max_lon
        dict['points'] = points
        # create cached file with necessary data and info
        with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
            json.dump(dict, f)
    else:
        print('Plotline Data is Cached!')
        with open('visualizer/static/visualizer/temp/' + cached_file) as f:
            cached_data = json.load(f)
        min_lat = cached_data['min_lat']
        max_lat = cached_data['max_lat']
        min_lon = cached_data['min_lon']
        max_lon = cached_data['max_lon']

        points = cached_data['points']

    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])

    pol_group_layer = folium.map.FeatureGroup(name='Polygon - Layer:' + str(time.time()).replace(".","_") , overlay=True,
                                              control=True).add_to(m)
    folium.PolyLine(points, color=color, weight=2.0, opacity=0.8,
                    ).add_to(pol_group_layer)
    ret_html = ""
    return m, ret_html


def load_modify_query_for_polygon_coverage(dataset_id):
    doc = {
        'distinct': False,
        'filters': {},
        'from': [{'name': 'sea_surface_wave_significant_height_0',
                  'select': [{'aggregate': '',
                              'datatype': 'None',
                              'exclude': True,
                              'groupBy': False,
                              'name': 'i0_sea_surface_wave_significant_height',
                              'title': 'sea_surface_wave_significant_height',
                              'type': 'VALUE'},
                             {'aggregate': '',
                              'datatype': 'None',
                              'exclude': '',
                              'groupBy': False,
                              'name': 'i0_longitude',
                              'title': 'longitude',
                              'type': 7140},
                             {'aggregate': '',
                              'datatype': 'None',
                              'exclude': '',
                              'groupBy': False,
                              'name': 'i0_latitude',
                              'title': 'latitude',
                              'type': 7141}],
                  'type': 2191}],
        'limit': '',
        'offset': 0,
        'orderings': []}
    var = Variable.objects.filter(dataset=Dataset.objects.get(pk=int(dataset_id))).first()
    doc['from'][0]['type'] = var.id
    doc['from'][0]['select'][0]['title'] = var.title
    doc['from'][0]['select'][0]['name'] = 'i0_' + var.name
    lat_dim = Dimension.objects.filter(variable=var, name='latitude').first().pk
    lon_dim = Dimension.objects.filter(variable=var, name='longitude').first().pk
    doc['from'][0]['select'][1]['type'] = lon_dim
    doc['from'][0]['select'][2]['type'] = lat_dim
    query = TempQuery(document=doc, user=User.objects.get(username='BigDataOcean'))
    query.save()
    query_pk = query.id
    return query_pk


def load_modify_query_for_grid_coverage(dataset_id, marker_limit=100):
    doc = {
        'distinct': False,
        'filters': {},
        'from': [{'name': 'sea_surface_wave_significant_height_0',
                  'select': [{'aggregate': '',
                              'datatype': 'None',
                              'exclude': True,
                              'groupBy': False,
                              'name': 'i0_sea_surface_wave_significant_height',
                              'title': 'sea_surface_wave_significant_height',
                              'type': 'VALUE'},
                             {'aggregate': 'round2',
                              'datatype': 'None',
                              'exclude': '',
                              'groupBy': True,
                              'name': 'i0_longitude',
                              'title': 'longitude',
                              'type': 7140},
                             {'aggregate': 'round2',
                              'datatype': 'None',
                              'exclude': '',
                              'groupBy': True,
                              'name': 'i0_latitude',
                              'title': 'latitude',
                              'type': 7141}],
                  'type': 2191}],
        'limit': marker_limit,
        'offset': 0,
        'orderings': []}
    var = Variable.objects.filter(dataset=Dataset.objects.get(pk=int(dataset_id))).first()
    doc['from'][0]['type'] = var.id
    doc['from'][0]['select'][0]['title'] = var.title
    doc['from'][0]['select'][0]['name'] = 'i0_' + var.name
    lat_dim = Dimension.objects.filter(variable=var, name='latitude').first().pk
    lon_dim = Dimension.objects.filter(variable=var, name='longitude').first().pk
    doc['from'][0]['select'][1]['type'] = lon_dim
    doc['from'][0]['select'][2]['type'] = lat_dim
    query = TempQuery(document=doc, user=User.objects.get(username='BigDataOcean'))
    query.save()
    query_pk = query.id
    return query_pk


# def get_map_polygon_for_dataset_coverage(query_pk, m):
def get_map_polygon_for_dataset_coverage(dataset_id, m):
    query_pk = load_modify_query_for_polygon_coverage(dataset_id)
    query = load_modify_query_polygon_for_dataset_coverage(query_pk, 'MIN')
    data, lat_index, lon_index, time_index = get_map_plotline_vessel_query_data(query)
    min_lat = data[0][lat_index]
    min_lon = data[0][lon_index]
    query = load_modify_query_polygon_for_dataset_coverage(query_pk, 'MAX')
    data, lat_index, lon_index, time_index = get_map_plotline_vessel_query_data(query)
    max_lat = data[0][lat_index]
    max_lon = data[0][lon_index]
    points = list()
    points.append([min_lat, min_lon])
    points.append([min_lat, max_lon])
    points.append([max_lat, max_lon])
    points.append([max_lat, min_lon])
    points.append([min_lat, min_lon])

    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])

    pol_group_layer = folium.map.FeatureGroup(name='Polygon - Layer:' + str(time.time()).replace(".","_") , overlay=True,
                                              control=True).add_to(m)
    folium.PolyLine(points, color='green', weight=2.0, opacity=0.8, fill='green').add_to(pol_group_layer)
    ret_html = ""
    return m, ret_html


def create_plotline_points(data, lat_index, lon_index):
    points = []
    min_lat = 90
    max_lat = -90
    min_lon = 180
    max_lon = -180


    for s in data:
        points.append([float(s[lat_index]), float(s[lon_index])])
        if s[lat_index] > max_lat:
            max_lat = s[lat_index]
        if s[lat_index] < min_lat:
            min_lat = s[lat_index]
        if s[lon_index] > max_lon:
            max_lon = s[lon_index]
        if s[lon_index] < min_lon:
            min_lon = s[lon_index]

    max_lat = float(max_lat)
    min_lat = float(min_lat)
    max_lon = float(max_lon)
    min_lon = float(min_lon)

    return points, min_lat, max_lat, min_lon, max_lon



def get_map_heatmap(query_pk, df, notebook_id, lat_col, lon_col, heat_col, heat_points_limit, m, cached_file, request):
    dict = {}
    max_intensity = 1.0
    if not os.path.isfile('visualizer/static/visualizer/temp/' + cached_file):
        if query_pk != 0:
            query = load_modify_query_heatmap(query_pk, heat_col, heat_points_limit)
            data, lat_index, lon_index, heat_var_index = get_heatmap_query_data(query, heat_col)
        else:
            data, headers = load_execute_dataframe_data(request, df, notebook_id)
            heatmap_data = []
            lat_index = 0
            lon_index = 1
            heat_var_index = 2
            for s in data:
                row = [float(s[lat_col]), float(s[lon_col]), float(s[heat_col])]
                heatmap_data.append(row)

        heatmap_result_data, min_lat, min_lon, max_lat, max_lon, max_intensity = create_heatmap_points(heat_col, data, lat_index, lon_index, heat_var_index)
        dict['min_lat'] = min_lat
        dict['max_lat'] = max_lat
        dict['min_lon'] = min_lon
        dict['max_lon'] = max_lon
        dict['heatmap_result_data'] = heatmap_result_data

        with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
            json.dump(dict, f)
    else:
        print ('Heatmap Data is Cached!')
        with open('visualizer/static/visualizer/temp/' + cached_file) as f:
            cached_data = json.load(f)
        min_lat = cached_data['min_lat']
        max_lat = cached_data['max_lat']
        min_lon = cached_data['min_lon']
        max_lon = cached_data['max_lon']
        heatmap_result_data = cached_data['heatmap_result_data']

    HeatMap(heatmap_result_data,max_val=1.0, radius = 15,name="Heat Map - Layer: "+str(time.time()).replace(".","_")).add_to(m)
    # if needed use gradient above gradient={0: 'blue',0.2: 'lightblue',0.3:'cadetblue', 0.4: 'lightgreen',0.5:'green',0.6:'lime', 0.7:'yellow',0.9:'orange',1: 'red'}
    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
    ret_html = ""
    return m, ret_html


def get_heatmap_query_data(query, heat_variable):
    try:
        query_data = execute_query_method(query)
    except ProgrammingError:
        raise ValueError('The requested visualisation cannot be executed for the chosen query.')
    data = query_data[0]['results']
    result_headers = query_data[0]['headers']

    heat_var_index = lat_index = lon_index = -1

    for idx, c in enumerate(result_headers['columns']):
        if c['name'].split('_', 1)[1] == 'latitude':
            lat_index = idx
        elif c['name'].split('_', 1)[1] == 'longitude':
            lon_index = idx
        elif c['name'] == heat_variable:
            heat_var_index = idx
    return data, lat_index, lon_index, heat_var_index


def get_map_contour(n_contours, step, variable, query_pk, agg_function, m, cached_file, tries=0):
    try:
        round_num = get_contour_step_rounded(step)
        dict = {}
        if not os.path.isfile('visualizer/static/visualizer/temp/'+cached_file):
            query = load_modify_query_contours(agg_function, query_pk, round_num, variable)
            data, lat_index, lon_index, var_index = get_contours_query_data(query, variable)
            Lats, Lons, lats_bins, lons_bins, max_lat, max_lon, max_val, min_lat, min_lon, min_val = get_contour_grid(data, lat_index, lon_index, step, var_index)
            # final_data, data_grid = get_contour_points(data, lat_index, lats_bins, lon_index, lons_bins, min_lat, min_lon, step, var_index)
            data_grid = []
            # mappath = create_contour_image(Lats, Lons, final_data, max_val, min_val, n_contours)

            xi = np.arange(min_lon, max_lon + 0.00001, step)
            yi = np.arange(min_lat, max_lat + 0.00001, step)
            mappath = create_contour_image(yi, xi, data, max_val, min_val, n_contours, lat_index, lon_index, var_index)
            print 'mappath'
            print mappath
            # legpath = get_contour_legend(max_val, min_val)
            legpath = ''

            dict['min_lat'] = min_lat
            dict['max_lat'] = max_lat
            dict['min_lon'] = min_lon
            dict['max_lon'] = max_lon
            dict['lats_bins_min'] = lats_bins_min = lats_bins[0]
            dict['lons_bins_min'] = lons_bins_min = lons_bins[0]
            dict['lats_bins_max'] = lats_bins_max = lats_bins[-1]
            dict['lons_bins_max'] = lons_bins_max = lons_bins[-1]
            dict['image_path'] = mappath
            dict['leg_path'] = legpath
            dict['data_grid'] = data_grid
            with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
                json.dump(dict, f)
        else:
            print ('Contours data is cached!')
            with open('visualizer/static/visualizer/temp/' + cached_file) as f:
                cached_data = json.load(f)
            min_lat = cached_data['min_lat']
            max_lat = cached_data['max_lat']
            min_lon = cached_data['min_lon']
            max_lon = cached_data['max_lon']
            lats_bins_min = cached_data['lats_bins_min']
            lons_bins_min = cached_data['lons_bins_min']
            lats_bins_max = cached_data['lats_bins_max']
            lons_bins_max = cached_data['lons_bins_max']
            mappath = cached_data['image_path'].encode('ascii')
            legpath = cached_data['leg_path'].encode('ascii')
            data_grid = cached_data['data_grid']
            data_grid = [[j.encode('ascii') for j in i] for i in data_grid]

        mapname = create_contour_map_html(lats_bins_max, lats_bins_min, lons_bins_max, lons_bins_min, m, mappath, max_lat,
                                max_lon, min_lat, min_lon, legpath)
        print 'mapname ok'
        map_id, ret_html = parse_contour_map_html(agg_function, data_grid, legpath, max_lat, max_lon, min_lat, min_lon,
                                                  step, mapname)
        return m, ret_html, map_id

    except Exception, e:
        print e
        traceback.print_exc()
        if tries == 0:
            return get_map_contour(n_contours, step, variable, query_pk, agg_function, m, cached_file, tries=1)
        else:
            raise Exception('An error occurred while creating the contours on map.')


def parse_contour_map_html(agg_function, data_grid, legpath, max_lat, max_lon, min_lat, min_lon, step, mapname):
    f = open(mapname, 'r')
    map_html = f.read()
    soup = BeautifulSoup(map_html, 'html.parser')
    map_id = soup.find("div", {"class": "folium-map"}).get('id')
    js_all = soup.findAll('script')
    if len(js_all) > 5:
        js_all = [js.prettify() for js in js_all[5:]]
    css_all = soup.findAll('link')
    if len(css_all) > 3:
        css_all = [css.prettify() for css in css_all[3:]]
    f.close()
    # import pdb
    # pdb.set_trace()
    temp_html = render_to_string('visualizer/map_viz_folium.html',
                                 {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'step': step,
                                  'data_grid': data_grid, 'min_lat': min_lat,
                                  'max_lat': max_lat, 'min_lon': min_lon, 'max_lon': max_lon,
                                  'agg_function': agg_function, 'legend_id': legpath})
    if "var startsplitter = 42;" in temp_html:
        ret_html = "<script> " + temp_html.split("var startsplitter = 42;")[1].split("var endsplitter = 42;")[
            0] + " </script>"
    else:
        ret_html = ""
    return map_id, ret_html


def create_contour_map_html(lats_bins_max, lats_bins_min, lons_bins_max, lons_bins_min, m, mappath, max_lat, max_lon,
                            min_lat, min_lon, legpath):
    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
    # read in png file to numpy array
    data_img = Image.open(mappath)
    data = trim(data_img)
    data_img.close()
    # Overlay the image
    contour_layer = plugins.ImageOverlay(data, zindex=1, opacity=0.8, mercator_project=True,
                                         bounds=[[lats_bins_min, lons_bins_min], [lats_bins_max, lons_bins_max]])
    contour_layer.layer_name = 'Contours On Map - Layer:' + str(time.time()).replace(".","_")
    m.add_child(contour_layer)
    # legend_img = Image.open(legpath)
    # legend = trim(legend_img)
    # legend_img.close()
    # contour_legend_layer = plugins.ImageOverlay(legend, zindex=2, opacity=1,bounds=[[-60, -173], [-55, -90]])
    # contour_legend_layer.layer_name = 'Contours Legend - Layer:' + str(time.time()).replace(".", "_")
    # m.add_child(contour_legend_layer)
    # Overlay an extra coastline field (to be removed)
    folium.GeoJson(open('ne_50m_land.geojson').read(),
                   style_function=lambda feature: {'fillColor': '#002a70', 'color': 'black', 'weight': 3}) \
        .add_to(m) \
        .layer_name = 'Coastline - Layer'
    # Parse the HTML to pass to template through the render
    mapname = 'templates/map'+str(mappath).split('/temp/')[1].split('.png')[0]+'.html'
    print 'mapname'
    print mapname
    m.save(mapname)
    return mapname


def get_contour_legend(max_val, min_val):
    a = np.array([[min_val, max_val]])
    pl.figure(figsize=(2.8, 0.4))
    img = pl.imshow(a, cmap=plt.cm.coolwarm)
    pl.gca().set_visible(False)
    cax = pl.axes([0.1, 0.2, 0.8, 0.6])
    cbar = pl.colorbar(orientation="horizontal", cax=cax)
    cbar.ax.tick_params(labelsize=9, colors="#ffffff")
    ts = str(time.time()).replace(".", "")
    legpath = 'visualizer/static/visualizer/img/temp/' + ts + 'colorbar.png'
    pl.savefig(legpath, transparent=True, bbox_inches='tight')
    # legpath = legpath.split("static/", 1)[1]
    pl.clf()
    pl.close()
    return legpath


def create_contour_image(yi, xi, final_data, max_val, min_val, n_contours, lat_index, lon_index, var_index):
    levels = np.linspace(start=min_val, stop=max_val, num=n_contours)
    print 'levels ok'
    import matplotlib.tri as tri
    from mpl_toolkits.basemap import Basemap
    bm = Basemap()
    x = np.array([i[lon_index] for i in final_data])
    y = np.array([i[lat_index] for i in final_data])
    z = np.array([i[var_index] for i in final_data])
    min_x = min(x)
    min_y = min(y)
    max_x = max(x)
    max_y = max(y)

    triang = tri.Triangulation(x, y)
    interpolator = tri.LinearTriInterpolator(triang, z)
    Xi, Yi = np.meshgrid(xi, yi)
    zi = interpolator(Xi, Yi)
    # print zi[:1]
    # print xi[:3]
    # print yi[:3]
    # print len(zi)  # rows
    # print len(yi)
    # print len(zi[0])  # columns
    # print len(xi)
    for x_index, x in enumerate(xi):
        for y_index, y in enumerate(yi):
            if bm.is_land(x, y):
                zi[y_index][x_index] = None
    # fig, ax1 = plt.subplots(nrows=1)
    min_val = min(z)
    max_val = max(z)
    # levels = np.linspace(start=min_val, stop=max_val, num=n_contours)
    # ax1.contour(xi, yi, zi, levels=levels, linewidths=0.5, colors='k')
    # cntr1 = ax1.contourf(xi, yi, zi, levels=levels, cmap="RdBu_r")
    # fig.colorbar(cntr1, ax=ax1)
    # plt.show()

    fig = Figure()
    ax = fig.add_subplot(111)
    # plt.contourf(Lons, Lats, final_data, levels=levels, cmap=plt.cm.coolwarm)
    # ax1.contour(xi, yi, zi, levels=levels, linewidths=0.5, colors='k')
    plt.contourf(xi, yi, zi, levels=levels, cmap="RdBu_r")
    # plt.tricontourf(x, y, z, levels=levels, cmap="RdBu_r")
    plt.axis('off')
    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    plt.draw()
    ts = str(time.time()).replace(".", "")
    mappath = 'visualizer/static/visualizer/img/temp/' + ts + 'map.png'
    print 'trying to save fig at '+str(mappath)
    plt.savefig(mappath, bbox_inches=extent, transparent=True, frameon=False, pad_inches=0)
    print 'saved fig'
    plt.clf()
    plt.close()
    fig = None
    ax = None
    return mappath


def get_contour_points(data, lat_index, lats_bins, lon_index, lons_bins, min_lat, min_lon, step, var_index):
    from mpl_toolkits.basemap import Basemap
    bm = Basemap()
    final_data = []
    data_grid = []
    it = iter(data)
    try:
        val = map(float, next(it))
    except:
        val = [-300, -300, -300]
    for lon in lons_bins:
        row = list()
        pop_row = list()
        for lat in lats_bins:
            if bm.is_land(float(lon), float(lat)):
                row.append(None)
            else:
                row.append(None)
            pop_row.append(('None').encode('ascii'))
        final_data.append(row)
        data_grid.append(pop_row)
    for d in data:
        lon_pos = int((d[lon_index] - min_lon) / step)
        lat_pos = int((d[lat_index] - min_lat) / step)
        final_data[lon_pos][lat_pos] = d[var_index]
        if d[var_index] != 'None':
            data_grid[lon_pos][lat_pos] = str(d[var_index])
        else:
            data_grid[lon_pos][lat_pos] = str(-9999999)

    return final_data, data_grid


def get_contour_grid(data, lat_index, lon_index, step, var_index):
    min_lat = 90
    max_lat = -90
    min_lon = 180
    max_lon = -180
    min_val = 9999999999
    max_val = -9999999999
    # print data[:3]
    for row in data:
        if row[lat_index] > max_lat:
            max_lat = row[lat_index]
        if row[lat_index] < min_lat:
            min_lat = row[lat_index]
        if row[lon_index] > max_lon:
            max_lon = row[lon_index]
        if row[lon_index] < min_lon:
            min_lon = row[lon_index]
        if row[var_index] > max_val:
            max_val = row[var_index]
        if row[var_index] is not None and row[var_index] < min_val:
            min_val = row[var_index]
    max_lat = float(max_lat)
    min_lat = float(min_lat)
    max_lon = float(max_lon)
    min_lon = float(min_lon)
    max_val = float(max_val)
    min_val = float(min_val)
    lats_bins = np.arange(min_lat, max_lat + 0.00001, step)
    lons_bins = np.arange(min_lon, max_lon + 0.00001, step)
    Lats, Lons = np.meshgrid(lats_bins, lons_bins)
    return Lats, Lons, lats_bins, lons_bins, max_lat, max_lon, max_val, min_lat, min_lon, min_val


def get_contours_query_data(query, variable):
    try:
        result = execute_query_method(query)[0]
    except ProgrammingError:
        raise ValueError('The requested visualisation cannot be executed for the chosen query.')
    result_data = result['results']
    result_headers = result['headers']

    var_index = lat_index = lon_index = -1
    # print result_headers
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] == variable:
            var_index = idx
        elif c['name'].split('_', 1)[1] == 'latitude':
            lat_index = idx
        elif c['name'].split('_', 1)[1] == 'longitude':
            lon_index = idx
    data = [row for row in result_data if row[var_index] is not None]
    return data, lat_index, lon_index, var_index



def get_contour_step_rounded(step):
    round_num = 0
    if step == 1:
        round_num = 0
    elif step == 0.1:
        round_num = 1
    elif step == 0.01:
        round_num = 2
    elif step == 0.001:
        round_num = 3
    return round_num


def get_marker_query_data(query, variable, color_col):
    try:
        query_data = execute_query_method(query)
    except:
        raise ValueError('The requested visualisation cannot be executed for the chosen query.')
    data = query_data[0]['results']
    result_headers = query_data[0]['headers']
    var_title = var_unit = None
    time_index = lat_index = lon_index = var_index = color_index = -1
    for idx, c in enumerate(result_headers['columns']):
        if c['name'].split('_', 1)[1] == 'latitude':
            lat_index = idx
        elif c['name'].split('_', 1)[1] == 'longitude':
            lon_index = idx
        elif c['name'].split('_', 1)[1] == 'time':
            time_index = idx
        elif c['name'] == variable:
            var_index = idx
            var_title = c['title'].encode('ascii')
            var_unit = c['unit'].encode('ascii')
        elif c['name'] == color_col:
            color_index = idx
    return data, lat_index, lon_index, time_index, var_index, color_index, var_title, var_unit



def get_map_markers_grid(query_pk, df, notebook_id, marker_limit, variable, agg_function, lat_col, lon_col, m, request, cached_file, dataset_id=None):
    dic = {}
    print variable
    if not os.path.isfile('visualizer/static/visualizer/temp/' + cached_file):
        if query_pk != 0:
            if dataset_id is not None:
                query = AbstractQuery.objects.get(pk=int(load_modify_query_for_grid_coverage(dataset_id, marker_limit)))
            else:
                query = load_modify_query_marker_grid(query_pk, variable, marker_limit, agg_function)
            data, lat_index, lon_index, time_null, var_index, color_null, var_title, var_unit = get_marker_query_data(query, variable, '')
        elif df != '':
            data, lat_index, lon_index, var_index, color_index, time_index = get_makers_dataframe_data(df, lat_col, lon_col, notebook_id, request, variable)
            var_title = 'title'
            var_unit = 'unit'
        else:
            raise ValueError('Either query ID or dataframe name has to be specified.')

        dic['data'] = data
        dic['lat_index'] = lat_index
        dic['lon_index'] = lon_index
        dic['var_index'] = var_index
        dic['var_title'] = var_title
        dic['var_unit'] = var_unit
        with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
            json.dump(dic, f, default=myconverter)
    else:
        print "Markers Grid data is cached!"
        with open('visualizer/static/visualizer/temp/' + cached_file) as f:
            cached_data = json.load(f)
        data = cached_data['data']
        lat_index = cached_data['lat_index']
        lon_index = cached_data['lon_index']
        var_index = cached_data['var_index']
        var_title = cached_data['var_title']
        var_unit = cached_data['var_unit']

    ret_html = create_marker_grid_points(data, lat_index, lon_index, m, var_index, var_title, var_unit)
    return m, ret_html



def get_map_markers_vessel_course(query_pk, df, notebook_id, marker_limit, vessel_column, vessel_id, variable, agg_function, lat_col, lon_col, color_col, use_color_col, m, request,cached_file):
    dic = {}
    if not os.path.isfile('visualizer/static/visualizer/temp/' + cached_file):
        if query_pk != 0:
            query = load_modify_query_marker_vessel(query_pk, variable, marker_limit, vessel_column, vessel_id, color_col, agg_function, use_color_col)
            data, lat_index, lon_index, time_index, var_index, color_index, var_title, var_unit = get_marker_query_data(query, variable, color_col)
        elif df != '':
            data, lat_index, lon_index, var_index, color_index, time_index = get_makers_dataframe_data(color_col, df, lat_col, lon_col, notebook_id, request, variable)
        else:
            raise ValueError('Either query ID or dataframe name has to be specified.')

        dic['data'] = data
        dic['color_index'] = color_index
        dic['lat_index'] = lat_index
        dic['lon_index'] = lon_index
        dic['time_index'] = time_index
        dic['var_index'] = var_index
        dic['var_title'] = var_title
        dic['var_unit'] = var_unit
        with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
            json.dump(dic, f, default=myconverter)
    else:
        print "Markers Course data is cached!"
        with open('visualizer/static/visualizer/temp/' + cached_file) as f:
            cached_data = json.load(f)
        data = cached_data['data']
        color_index = cached_data['color_index']
        lat_index = cached_data['lat_index']
        lon_index = cached_data['lon_index']
        var_index = cached_data['var_index']
        time_index = cached_data['time_index']
        var_title = cached_data['var_title']
        var_unit = cached_data['var_unit']

    ret_html = create_marker_vessel_points(color_col, color_index, data, lat_index, lon_index, m, time_index,
                                           var_index, var_title, var_unit, vessel_id)
    return m, ret_html


def create_marker_vessel_points(color_col, color_index, data, lat_index, lon_index, m, time_index, var_index,
                                var_title, var_unit, vessel_id):
    pol_group_layer = folium.map.FeatureGroup(name='Markers - Vessel Course Layer : ' + str(time.time()).replace(".","_") + '/ Ship ID: ' + str(vessel_id),
                                              overlay=True,
                                              control=True).add_to(m)
    color_dict = dict()
    color_cnt = 0
    min_lat = 90
    max_lat = -90
    min_lon = 180
    max_lon = -180

    for d in data:
        if color_col != '':
            if d[color_index] not in color_dict.keys():
                if color_cnt < len(FOLIUM_COLORS):
                    color_dict[d[color_index]] = FOLIUM_COLORS[color_cnt]
                else:
                    color_dict[d[color_index]] = FOLIUM_COLORS[len(FOLIUM_COLORS) - 1]
                color_cnt += 1
            marker_color = color_dict[d[color_index]]
        else:
            marker_color = 'blue'

        if d[lat_index] > max_lat:
            max_lat = d[lat_index]
        if d[lat_index] < min_lat:
            min_lat = d[lat_index]
        if d[lon_index] > max_lon:
            max_lon = d[lon_index]
        if d[lon_index] < min_lon:
            min_lon = d[lon_index]

        try:
            var_val = str(round(d[var_index], 3))
        except:
            var_val = str(d[var_index])
        if var_val == "None":
            var_val = 'unavailable'
        else:
            var_val = var_val + " " + str(var_unit)

        folium.Marker(
            location=[d[lat_index], d[lon_index]],
            popup=str(var_title) + ": " + var_val + "<br>Time: " + str(d[time_index]) + "<br>Latitude: " + str(
                d[lat_index]) + "<br>Longitude: " + str(d[lon_index]),
            icon=folium.Icon(color=marker_color),
            # radius=2,

        ).add_to(pol_group_layer)
    max_lat = float(max_lat)
    min_lat = float(min_lat)
    max_lon = float(max_lon)
    min_lon = float(min_lon)
    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
    ret_html = ""
    return ret_html


def create_marker_grid_points(data, lat_index, lon_index, m, var_index, var_title, var_unit):
    pol_group_layer = folium.map.FeatureGroup(name='Markers - Grid Layer : ' + str(time.time()).replace(".","_") ,
                                              overlay=True,
                                              control=True).add_to(m)
    min_lat = 90
    max_lat = -90
    min_lon = 180
    max_lon = -180
    marker_color = 'orange'
    marker_cluster = MarkerCluster().add_to(pol_group_layer)
    for d in data:
        if d[lat_index] > max_lat:
            max_lat = d[lat_index]
        if d[lat_index] < min_lat and d[lat_index] is not None:
            min_lat = d[lat_index]
        if d[lon_index] > max_lon:
            max_lon = d[lon_index]
        if d[lon_index] < min_lon and d[lon_index] is not None:
            min_lon = d[lon_index]
        if d[var_index] is not None:
            folium.Marker(
                location=[d[lat_index], d[lon_index]],
                popup=str(var_title) + ": " + str(round(d[var_index],3)) +" "+ str(var_unit)+"<br>Latitude: " + str(d[lat_index]) + "<br>Longitude: " + str(d[lon_index]),icon=folium.Icon(color=marker_color)).add_to(marker_cluster)
    max_lat = float(max_lat)
    min_lat = float(min_lat)
    max_lon = float(max_lon)
    min_lon = float(min_lon)
    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
    ret_html = ""
    return ret_html


def get_makers_dataframe_data(color_col, df, lat_col, lon_col, notebook_id, request, variable):
    service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')[0]  # GET LAST
    livy = service_exec.service.through_livy
    session_id = service_exec.livy_session
    exec_id = service_exec.id
    updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
    if not livy:
        toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df,
                                                          order_by='time')
    else:
        json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df, order_by='time')
    if not livy:
        run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
        json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
    data = []
    lat_index = 0
    lon_index = 1
    var_index = 2
    color_index = 3
    time_index = 4
    for s in json_data:
        row = [float(s[lat_col]), float(s[lon_col])]
        if variable != '':
            row.append(str(s[variable]))
        else:
            row.append('')
        if color_col != '':
            row.append(s[color_col])
        else:
            row.append('')
        data.append(row)
    return data, lat_index, lon_index, var_index, color_index, time_index


def map_course_mt(request):
    df1 = str(request.GET.get('df1', ''))
    df2 = str(request.GET.get('df2', ''))
    notebook_id = str(request.GET.get('notebook_id', ''))

    order_var1 = str(request.GET.get('order_var1', ''))
    order_var2 = str(request.GET.get('order_var2', ''))
    variable1 = str(request.GET.get('col_var1', ''))
    variable2 = str(request.GET.get('col_var2', ''))

    lat_col1 = str(request.GET.get('lat_col1', 'latitude'))
    lon_col1 = str(request.GET.get('lon_col1', 'longitude'))
    lat_col2 = str(request.GET.get('lat_col2', 'latitude'))
    lon_col2 = str(request.GET.get('lon_col2', 'longitude'))

    color_col1 = str(request.GET.get('color_col1', ''))
    color_col2 = str(request.GET.get('color_col2', ''))

    diameter_col1 = str(request.GET.get('diameter_col1', ''))

    try:
        marker_limit = int(request.GET.get('m_limit', '200'))
    except:
        marker_limit = 1000


    print ("json-case")
    service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')[0] #GET LAST
    livy = service_exec.service.through_livy
    session_id = service_exec.livy_session
    exec_id = service_exec.id
    updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
    if order_var1 != "":
        if not livy:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df1)
        else:
            json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df1)

    else:
        if not livy:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df1, order_by=order_var1)
        else:
            json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df1, order_by=order_var1)

    # if order_var1 != "":
    #     toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df1)
    # else:
    #     toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df1, order_by=order_var1)
    if not livy:
        run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
        json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        # print json_data

    data1 = []
    lat_index = 0
    lon_index = 1
    order_var_index = 2
    var_index = 3
    color_index = 4
    diameter_index = 5
    for s in json_data:
        row = [float(s[lat_col1]), float(s[lon_col1])]
        if order_var1 != '':
            row.append(str(s[order_var1]))
        else:
            row.append('')
        if variable1 != '':
            row.append(str(s[variable1]))
        else:
            row.append('')
        if color_col1 != '':
            row.append(s[color_col1])
        else:
            row.append('')
        if diameter_col1 != '':
                row.append(float(s[diameter_col1]))
        else:
            row.append('')
        data1.append(row)

    print data1[:4]



    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    if len(data1) > 0:
        min_lat = float(min(data1, key=lambda x: x[lat_index])[lat_index])
        max_lat = float(max(data1, key=lambda x: x[lat_index])[lat_index])
        min_lon = float(min(data1, key=lambda x: x[lon_index])[lon_index])
        max_lon = float(max(data1, key=lambda x: x[lon_index])[lon_index])
    else:
        min_lat = -90
        max_lat = 90
        min_lon = -180
        max_lon = 180
    zoom_lat = (min_lat + max_lat) / 2
    zoom_lon = (min_lon + max_lon) / 2
    location = [zoom_lat, zoom_lon]
    zoom_start = 4
    max_zoom = 30
    min_zoom = 2

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   min_zoom=min_zoom,
                   max_bounds=True,
                   tiles=tiles_str + token_str,
                   attr=attr_str,
                   )

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True).add_to(m)

    color_dict = dict()
    color_cnt = 0

    print "Map course top 10 points"
    print data1[:10]

    featureCollection1 = {'type': 'FeatureCollection', 'features': []}

    features = []
    for d in data1:
        # if color_col1 != '':
        #     if d[color_index] not in color_dict.keys():
        #         if color_cnt < len(FOLIUM_COLORS):
        #             color_dict[d[color_index]] = FOLIUM_COLORS[color_cnt]
        #         else:
        #             # color_dict[d[color_index]] = FOLIUM_COLORS[len(FOLIUM_COLORS)-1]
        #             color_dict[d[color_index]] = FOLIUM_COLORS[color_cnt % (len(FOLIUM_COLORS))]
        #         color_cnt += 1
        #     marker_color = color_dict[d[color_index]]
        # else:
        #     marker_color = 'blue'
        marker_color = 'green'

        featureCollection1['features'].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(d[lon_index]), float(d[lat_index])],
            },
            "properties": {
                "style": {
                    "fillColor": marker_color,
                    # 'fillColor': 'green',
                    'opacity': 0.6,
                    'stroke': 'false',
                    'radius': int(d[diameter_index]*1000)
                },
                'icon': 'circle',
                'popup': str(d[var_index]),
            }
        })



    print ("json-case")
    service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')[0] #GET LAST
    livy = service_exec.service.through_livy
    session_id = service_exec.livy_session
    exec_id = service_exec.id
    updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
    if order_var2 != "":
        if not livy:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df2)
        else:
            json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df2)

    else:
        if not livy:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df2, order_by=order_var2)
        else:
            json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df2, order_by=order_var2)
    # if order_var2 != "":
    #     toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df2)
    # else:
    #     toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df2, order_by=order_var2)
    if not livy:
        run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
        json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        # print json_data

    data2 = []
    lat_index = 0
    lon_index = 1
    order_var_index = 2
    var_index = 3
    color_index = 4
    for s in json_data:
        row = [float(s[lat_col2]), float(s[lon_col2])]
        if order_var2 != '':
            row.append(str(s[order_var2]))
        else:
            row.append('')
        if variable2 != '':
            row.append(str(int(s[variable2])))
        else:
            row.append('')
        if color_col2 != '':
            row.append(s[color_col2])
        else:
            row.append('')
        data2.append(row)

    print data2[:4]

    color_dict = dict()
    color_cnt = 0

    print "Map course top 10 points"
    print data2[:10]

    featureCollection2 = {'type': 'FeatureCollection', 'features': []}

    features = []
    for d in data2:
        if color_col2 != '':
            if d[color_index] not in color_dict.keys():
                if color_cnt < len(FOLIUM_COLORS):
                    color_dict[d[color_index]] = FOLIUM_COLORS[color_cnt]
                else:
                    # color_dict[d[color_index]] = FOLIUM_COLORS[len(FOLIUM_COLORS)-1]
                    color_dict[d[color_index]] = FOLIUM_COLORS[color_cnt % (len(FOLIUM_COLORS))]
                color_cnt += 1
            marker_color = color_dict[d[color_index]]
        else:
            marker_color = 'blue'

        featureCollection2['features'].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(d[lon_index]), float(d[lat_index])],
            },
            "properties": {
                "style": {
                    "fillColor": marker_color,
                    # 'fillColor': 'green',
                    'opacity': 0.6,
                    'stroke': 'false',
                    'radius': 100
                },
                'icon': 'circle',
                'popup': 'Ship ID: '+str(d[var_index]),
            }
        })

    # m.add_child(folium.features.GeoJson(featureCollection))

    # Add layer contorl
    folium.LayerControl().add_to(m)

    m.save('templates/map.html')

    map_html = open('templates/map.html', 'r').read()
    soup = BeautifulSoup(map_html, 'html.parser')
    map_id = soup.find("div", {"class": "folium-map"}).get('id')
    # print map_id
    js_all = soup.findAll('script')
    # print(js_all)
    if len(js_all) > 5:
        js_all = [js.prettify() for js in js_all[5:]]
    # print(js_all)
    css_all = soup.findAll('link')
    if len(css_all) > 3:
        css_all = [css.prettify() for css in css_all[3:]]
    # print js
    # os.remove('templates/map.html')
    return render(request, 'visualizer/map_course_mt.html',
                  {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'markerType':'circle', 'centroids': convert_unicode_json(featureCollection1), 'data_points': convert_unicode_json(featureCollection2)})



def map_markers_in_time(request):
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 30
    min_zoom = 2

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   min_zoom=min_zoom,
                   max_bounds=True,
                   tiles=tiles_str + token_str,
                   attr=attr_str)

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True).add_to(m)

    marker_limit = int(request.GET.get('markers', 1000))
    # var = str(request.GET.get('var'))
    order_var = str(request.GET.get('order_var', 'time'))
    query_pk = int(str(request.GET.get('query', 0)))

    notebook_id = str(request.GET.get('notebook_id', ''))
    df = str(request.GET.get('df', ''))

    lat_col = str(request.GET.get('lat_col', 'latitude'))
    lon_col = str(request.GET.get('lon_col', 'longitude'))

    markerType = str(request.GET.get('markerType', ''))
    FMT = '%Y-%m-%d %H:%M:%S'

    if query_pk!=0:
        q = AbstractQuery.objects.get(pk=int(query_pk))
        q = Query(document=q.document)
        doc = q.document

        doc['limit'] =  marker_limit
        doc['orderings'] = [{'name': order_var, 'type': 'ASC'}]

        for f in doc['from']:
            for s in f['select']:
                if s['name'] == order_var:
                    s['exclude'] = False
                elif s['name'].split('_', 1)[1] == 'latitude':
                    s['exclude'] = False
                elif s['name'].split('_', 1)[1] == 'longitude':
                    s['exclude'] = False
                # elif s['name'] == var:
                #     s['exclude'] = False
                else:
                    s['exclude'] = True


        # print doc
        q.document = doc

        query_data = execute_query_method(q)
        data = query_data[0]['results']
        result_headers = query_data[0]['headers']
        print(result_headers)

        var_index = order_index = lon_index = lat_index = -1

        for idx, c in enumerate(result_headers['columns']):
            # if c['name'] == var:
            #     var_index = idx
            if c['name'].split('_', 1)[1] == 'latitude':
                lat_index = idx
            elif c['name'].split('_', 1)[1] == 'longitude':
                lon_index = idx
            elif c['name'] == order_var:
                order_index = idx

        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(d[lon_index]), float(d[lat_index])],
                },
                "properties": {
                    "times": [str(d[order_index])],
                    "style": {
                        "color": "blue",
                    }
                }
            }
            for d in data
        ]
        tdelta = data[1][order_index] - data[0][order_index]
        period = 'PT{0}S'.format(tdelta.seconds)
    else:
        livy = False
        service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')
        if len(service_exec) > 0:
            service_exec = service_exec[0]  # GET LAST
            session_id = service_exec.livy_session
            exec_id = service_exec.id
            updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
            livy = service_exec.service.through_livy
        if livy:
            data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df, order_by=order_var, order_type='ASC')
        else:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=order_var, order_type='ASC')
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
            data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)

        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(d[lon_col]), float(d[lat_col])],
                },
                "properties": {
                    "times": [str(d[order_var])],
                    "style": {
                        "color": "blue",
                    }
                }
            }
            for d in data
        ]
        tdelta = time.strptime(data[1][order_var], FMT) - time.strptime(data[0][order_var], FMT)
        period = 'PT2H'

    features = convert_unicode_json(features)
    # plugins.TimestampedGeoJson({
    #     'type': 'FeatureCollection',
    #     'features': features,
    # }, period='PT1M', add_last_point=False, auto_play=False, loop=False).add_to(m)


    duration='PT0H'
    # plugins.TimestampedGeoJson({
    #     'type': 'FeatureCollection',
    #     'features': geo_list,
    # }, period='PT1H', add_last_point=False, auto_play=False, loop=False).add_to(m)
    # geo_list= str(geo_list).replace("'","\"")
    m.save('templates/map.html')
    f = open('templates/map.html', 'r')
    map_html = f.read()
    soup = BeautifulSoup(map_html, 'html.parser')
    map_id = soup.find("div", {"class": "folium-map"}).get('id')
    js_all = soup.findAll('script')
    if len(js_all) > 5:
        js_all = [js.prettify() for js in js_all[5:]]
    css_all = soup.findAll('link')
    if len(css_all) > 3:
        css_all = [css.prettify() for css in css_all[3:]]
    f.close()

    os.remove('templates/map.html')

    return render(request, 'visualizer/map_markers_in_time.html',
                      {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'data': features, 'time_interval': period,'duration':duration, 'markerType': markerType})



def create_heatmap_points(heat_col, data, lat_index, lon_index, heat_var_index):
    min_lat = 90
    max_lat = -90
    min_lon = 180
    max_lon = -180
    heatmap_result_data = []
    maximum = 1.0
    if (heat_col == 'heatmap_frequency'):
        for d in data:
            heatmap_result_data.append(
                (np.array([float(d[lat_index]), float(d[lon_index])]) * np.array([1, 1])).tolist())
            if d[lat_index] > max_lat:
                max_lat = d[lat_index]
            if d[lat_index] < min_lat:
                min_lat = d[lat_index]
            if d[lon_index] > max_lon:
                max_lon = d[lon_index]
            if d[lon_index] < min_lon:
                min_lon = d[lon_index]
    else:
        maximum = -999999999
        minimum = 999999999

        for d in data:
            if d[heat_var_index] is not None:
                if d[heat_var_index] > maximum:
                    maximum = float(d[heat_var_index])
                if d[heat_var_index] < minimum:
                    minimum = float(d[heat_var_index])
        if (len(data) != 1) and (maximum != minimum):
            for d in data:
                if d[heat_var_index] is not None:
                    heatmap_result_data.append((np.array([float(d[lat_index]), float(d[lon_index]), float((d[heat_var_index]) - minimum )/( maximum - minimum)])).tolist())
                    # heatmap_result_data.append((np.array([float(d[lat_index]), float(d[lon_index]),
                    #                                       float(d[heat_var_index])])).tolist())

                    if d[lat_index] > max_lat:
                        max_lat = d[lat_index]
                    if d[lat_index] < min_lat:
                        min_lat = d[lat_index]
                    if d[lon_index] > max_lon:
                        max_lon = d[lon_index]
                    if d[lon_index] < min_lon:
                        min_lon = d[lon_index]
        else:
            for d in data:
                heatmap_result_data.append((np.array([float(data[0][lat_index]), float(data[0][lon_index]),
                                                  float(1)])).tolist())

    max_lat = float(max_lat)
    min_lat = float(min_lat)
    max_lon = float(max_lon)
    min_lon = float(min_lon)

    return heatmap_result_data, min_lat, min_lon, max_lat, max_lon, maximum



def map_viz_folium_heatmap_time(request):
    query = int(str(request.GET.get('query', '0')))
    heat_col = str(request.GET.get('heat_col', 'frequency'))
    order_var = str(request.GET.get('order_var', 'time'))

    df = str(request.GET.get('df', ''))
    notebook_id = str(request.GET.get('notebook_id', ''))
    lat_col = str(request.GET.get('lat_col', 'latitude'))
    lon_col = str(request.GET.get('lon_col', 'longitude'))

    FMT = '%Y-%m-%d %H:%M:%S'

    if query != 0:
        q = AbstractQuery.objects.get(pk=int(query))
        q = TempQuery(document=q.document)
        doc = q.document

        doc['orderings'] = [{'name': order_var, 'type': 'ASC'}]

        for f in doc['from']:
            for s in f['select']:
                if s['name'] == order_var:
                    s['exclude'] = False
                elif s['name'].split('_', 1)[1] == 'latitude':
                    s['exclude'] = False
                elif s['name'].split('_', 1)[1] == 'longitude':
                    s['exclude'] = False
                elif s['name'] == heat_col:
                    s['exclude'] = False
                else:
                    s['exclude'] = True

        q.document = doc

        lat_index = lon_index = var_index = 0
        result = execute_query_method(q)[0]
        result_data = result['results']
        result_headers = result['headers']

        print result_headers
        for idx, c in enumerate(result_headers['columns']):
            if c['name'].split('_', 1)[1] == 'latitude':
                lat_index = idx
            elif c['name'].split('_', 1)[1] == 'longitude':
                lon_index = idx
            elif c['name'] == heat_col:
                var_index = idx
            elif c['name'] == order_var:
                order_index = idx

        data = result_data
    else:
        print ("json-case")
        toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=order_var,
                                                          order_type='ASC')
        run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)

        # print json_data

        data = []
        lat_index = 0
        lon_index = 1
        var_index = 2
        order_index = 3

        for s in json_data:
            row = [float(s[lat_col]), float(s[lon_col]), float(s[heat_col]),str(s[order_var])]
            data.append(row)


    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 13
    min_zoom = 2


    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   min_zoom=min_zoom,
                   max_bounds=True,
                   tiles=tiles_str+token_str,
                   attr=attr_str)

    curr_time = data[0][order_index]
    data_list = []
    time_list = []
    data_moment_list=[]

    for d in data:
        if (d[order_index] == curr_time):
            data_moment_list.append([float(d[lat_index]),float(d[lon_index]),float(d[var_index])])
        else:
            data_list.append(data_moment_list)
            time_list.append(curr_time.strftime("%Y-%m-%dT%H:%M:%S"))
            data_moment_list = []
            data_moment_list.append([float(d[lat_index]), float(d[lon_index]), float(d[var_index])])
            curr_time = d[order_index]
    data_list.append(data_moment_list)
    time_list.append(curr_time.strftime("%Y-%m-%dT%H:%M:%S"))

    hm = plugins.HeatMapWithTime(
        data_list,
        index=time_list,
        radius=0.5,
        scale_radius=True,
        auto_play=True,
        max_opacity=0.9,
    )

    hm.add_to(m)

    m.save('templates/map.html')
    map_html = open('templates/map.html', 'r').read()
    soup = BeautifulSoup(map_html, 'html.parser')
    map_id = soup.find("div", {"class": "folium-map"}).get('id')
    # print map_id
    js_all = soup.findAll('script')
    # print(js_all)
    if len(js_all) > 5:
        js_all = [js.prettify() for js in js_all[5:]]
    # print(js_all)
    css_all = soup.findAll('link')
    if len(css_all) > 3:
        css_all = [css.prettify() for css in css_all[3:]]
    # print js
    # os.remove('templates/map.html')
    return render(request, 'visualizer/map_wjs.html', {'map_id': map_id, 'js_all': js_all, 'css_all': css_all})


def get_histogram_chart_am(request):
    query_pk = int(str(request.GET.get('query', '0')))

    df = str(request.GET.get('df', ''))
    notebook_id = str(request.GET.get('notebook_id', ''))

    x_var = str(request.GET.get('x_var', ''))
    bins = int(str(request.GET.get('bins', '5')))

    if query_pk != 0:
        query = AbstractQuery.objects.get(pk=query_pk)
        query = TempQuery(document=query.document)
        doc = query.document

        from_table = ''
        table_col = ''
        cursor = None
        for f in doc['from']:
            for s in f['select']:
                if s['name'] == x_var:
                    var_title = s['title']
                    if s['type'] == 'VALUE':
                        v_obj = Variable.objects.get(pk=int(f['type']))
                        if v_obj.dataset.stored_at == 'LOCAL_POSTGRES':
                            from_table = f['name'][:-2] + '_' + f['type']
                            table_col = 'value'
                            cursor = connections['default'].cursor()
                        elif v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
                            from_table = str(v_obj.dataset.table_name)
                            table_col = str(v_obj.name)
                            cursor = connections['UBITECH_POSTGRES'].cursor()
                        elif v_obj.dataset.stored_at == 'UBITECH_PRESTO':
                            from_table = str(v_obj.dataset.table_name)
                            table_col = str(v_obj.name)
                            cursor = get_presto_cursor()
                    else:
                        d_obj = Dimension.objects.get(pk=int(s['type']))
                        v_obj = d_obj.variable
                        if v_obj.dataset.stored_at == 'LOCAL_POSTGRES':
                            from_table = f['name'][:-2] + '_' + f['type']
                            table_col = d_obj.name + '_' + s['type']
                            cursor = connections['default'].cursor()
                        elif v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
                            from_table = str(v_obj.dataset.table_name)
                            table_col = str(d_obj.name)
                            cursor = connections['UBITECH_POSTGRES'].cursor()
                        elif v_obj.dataset.stored_at == 'UBITECH_PRESTO':
                            from_table = str(v_obj.dataset.table_name)
                            table_col = str(d_obj.name)
                            cursor = get_presto_cursor()
                else:
                    s['exclude'] = True
        # print doc
        query.document = doc
        raw = query.raw_query
        print raw
        try:
            where_clause = ' WHERE ' + str(raw.split("WHERE")[1].split(') AS')[0].split("GROUP")[0].split("ORDER")[0]) + ' '
        except:
            where_clause = ''
        bins -= 1
        if where_clause == '':
            raw_query = """with drb_stats as (select min({0}) as min, max({0}) as max from {1} {3}),
                        histogram as (select width_bucket({0}, min, max, {2}) ,
                         (min({0}), max({0})) as range,
                         count(*) as freq from {1}, drb_stats {3} where {0} IS NOT NULL
    
                         group by 1
                         order by 1)
                        select range, freq
                        from histogram""".format(table_col, from_table, bins, where_clause)
        else:
            raw_query = """with drb_stats as (select min({0}) as min, max({0}) as max from {1} {3}),
                                histogram as (select width_bucket({0}, min, max, {2}) ,
                                 (min({0}), max({0})) as range,
                                 count(*) as freq from {1}, drb_stats {3} AND {0} IS NOT NULL

                                 group by 1
                                 order by 1)
                                select range, freq
                                from histogram""".format(table_col, from_table, bins, where_clause)
        # This tries to execute the existing query just to check the access to the datasets and has no additional functions.
        print raw_query
        # result = execute_query_method(query)[0]

        cursor.execute(raw_query)
        data = cursor.fetchall()
        json_data = []
        for d in data:
            if d[0][0] is not None :
                start_value = str(float(d[0][0]))
            else :
                start_value = 'None'
            if d[0][1] is not None :
                end_value = str(float(d[0][1]))
            else :
                end_value = 'None'
            json_data.append({"startValues": '['+ start_value + ',' + end_value + ']', "counts": str(d[1])})
        y_var = 'counts'
        x_var = 'startValues'
        # print data
        json_data = convert_unicode_json(json_data)
    else:
        bins += 1
        var_title = x_var
        livy = False
        service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')
        if len(service_exec) > 0:
            service_exec = service_exec[0]  # GET LAST
            session_id = service_exec.livy_session
            exec_id = service_exec.id
            updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
            livy = service_exec.service.through_livy
        if livy:
            tempView_paragraph_id = create_zep_tempView_paragraph(notebook_id=notebook_id, title='', df_name=df)
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=tempView_paragraph_id, livy_session_id=session_id, mode='livy')
            scala_histogram_paragraph_id = create_zep_scala_histogram_paragraph(notebook_id=notebook_id, title='', df_name=df, hist_col=x_var,num_of_bins=bins)
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=scala_histogram_paragraph_id, livy_session_id=session_id, mode='livy')
            json_data = create_livy_scala_toJSON_paragraph(session_id=session_id, df_name=df)

            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=tempView_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=scala_histogram_paragraph_id)
        else:
            tempView_paragraph_id = create_zep_tempView_paragraph(notebook_id=notebook_id, title='', df_name=df)
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=tempView_paragraph_id, livy_session_id=0, mode='zeppelin')
            scala_histogram_paragraph_id = create_zep_scala_histogram_paragraph(notebook_id=notebook_id, title='', df_name=df, hist_col=x_var, num_of_bins=bins)
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=scala_histogram_paragraph_id, livy_session_id=0, mode='zeppelin')
            toJSON_paragraph_id = create_zep_scala_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df)
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
            json_data = get_zep_scala_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=tempView_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=scala_histogram_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)

        for i in range(0, len(json_data) - 1):
            json_data[i]['startValues'] = str('[' + str(json_data[i]['startValues']) + ',' + str(json_data[i + 1]['startValues']) + ']')
        json_data = json_data[:-1]
        y_var = 'counts'
        x_var = 'startValues'

    return render(request, 'visualizer/histogram_simple_am.html', {'data': convert_unicode_json(json_data), 'value_col': y_var, 'category_col': x_var, 'category_title': var_title})


def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Arguments:
        data       : A 2D numpy array of shape (N,M)
        row_labels : A list or array of length N with the labels
                     for the rows
        col_labels : A list or array of length M with the labels
                     for the columns
    Optional arguments:
        ax         : A matplotlib.axes.Axes instance to which the heatmap
                     is plotted. If not provided, use current axes or
                     create a new one.
        cbar_kw    : A dictionary with arguments to
                     :meth:`matplotlib.Figure.colorbar`.
        cbarlabel  : The label for the colorbar
    All other arguments are directly passed on to the imshow call.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom", labelpad=10)
    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-50, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Arguments:
        im         : The AxesImage to be labeled.
    Optional arguments:
        data       : Data used to annotate. If None, the image's data is used.
        valfmt     : The format of the annotations inside the heatmap.
                     This should either use the string format method, e.g.
                     "$ {x:.2f}", or be a :class:`matplotlib.ticker.Formatter`.
        textcolors : A list or array of two color specifications. The first is
                     used for values below a threshold, the second for those
                     above.
        threshold  : Value in data units according to which the colors from
                     textcolors are applied. If None (the default) uses the
                     middle of the colormap as separation.

    Further arguments are passed on to the created text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[im.norm(data[i, j]) > threshold])
            # text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            # texts.append(text)
            texts.append('')

    return texts



def get_histogram_2d_matplotlib(request):
    query_pk = int(str(request.GET.get('query', '0')))
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))
    bins = int(str(request.GET.get('bins', '3')))
    if query_pk != 0:
        print('Loading/Modifying Query')
        query, y_var_title, y_from_table, y_table_col, x_var_title, x_from_table, x_table_col,cursor = histogram2d_load_modify_query(query_pk, x_var, y_var)
        print('Executing Query')
        # x_var_index, y_var_index, result_data, x_var_title, y_var_title = histogram2d_execute_query(query, x_var, y_var)
        raw_query = ("SELECT * FROM (SELECT count(*), round({0}, 0),round({1}, 0) FROM {2} WHERE {0} IS NOT NULL AND {1} IS NOT  NULL group by round({0}, 0), round({1}, 0) order by  round({0}, 0), round({1},0)) AS SQ1 ").format(x_table_col, y_table_col, x_from_table)
        cursor.execute(raw_query)
        result_data = cursor.fetchall()
        count_index = 0
        x_var_index = 1
        y_var_index = 2
    else:
        x_var_index, y_var_index, result_data, x_var_title, y_var_title = histogram2d_dataframe(x_var, y_var)

    print('Creating lists of data for histogram-2d')
    list_x = []
    list_y = []
    list_counts = []
    total = 0
    for el in result_data:
        if el[x_var_index] is not None:
            list_x.append(el[x_var_index])
        else:
            list_x.append(0)
        if el[y_var_index] is not None:
            list_y.append(el[y_var_index])
        else:
            list_y.append(0)
        list_counts.append(el[count_index])
        total = total + el[count_index]
    # total = result_data.__len__()

    print('Creating Histogram-2d')
    freq, xedges, yedges = np.histogram2d(list_x, list_y, bins, weights=list_counts)
    new_table = []

    for el in freq:
        hor_table = []
        for i in el:
            new_el = i/total
            hor_table.append(new_el)
        new_table.append(hor_table)
    new_table = np.array(new_table)

    xedges = [round(x, 2) for x in xedges]
    yedges = [round(y, 2) for y in yedges]


    # print('Creating X-Axis and Y-Axis different bins')
    # bin_x_cont = []
    # iter1 = iter(xedges)
    # iter1.next()
    # for el in xedges:
    #     try:
    #         temp = [round(el, 2), round(iter1.next(), 3)]
    #     except:
    #         break
    #     bin_x_cont.append(temp)
    #
    # bin_y_cont = []
    # iter1 = iter(yedges)
    # iter1.next()
    # for el in yedges:
    #     try:
    #         temp = [round(el, 2), round(iter1.next(),3)]
    #     except:
    #         break
    #     bin_y_cont.append(temp)

    fig, ax = plt.subplots()

    im, cbar = heatmap(new_table, xedges, yedges, ax=ax,
                       cmap="YlGn", cbarlabel="Percentage %")

    plt.xlabel(x_var_title, labelpad=10)
    plt.ylabel(y_var_title,  labelpad=10)
    fig.tight_layout()
    plt.draw()
    ts = str(time.time()).replace(".", "")
    html_path = ts + 'histogram2d.png'
    histpath = 'visualizer/static/visualizer/img/temp/' + html_path
    plt.savefig(histpath,  transparent=True, frameon=False, pad_inches=0)
    return render(request, 'visualizer/histogram_2d_matplotlib.html',
                  {'hist_path': html_path})


def histogram2d_dataframe(x_var, y_var):
    print ("dataframe")
    with open('visualizer/static/visualizer/histogrammyfile.json', 'r') as json_fd:
        jsonfile = json_fd.read()
    print(jsonfile)
    jsonfile = json.loads(jsonfile)
    print jsonfile
    jsondata = []
    x_var_index = 0
    y_var_index = 1
    for idy, s in enumerate(jsonfile['data']):
        jsondata.append([float(s[x_var].encode('ascii')), float(s[y_var].encode('ascii'))])
    x_var_title = 'X Title'
    y_var_title = 'Y Title'
    result_data = jsondata
    print result_data
    return x_var_index, y_var_index, result_data, x_var_title, y_var_title



def histogram2d_execute_query(query, x_var, y_var):
    query_data = execute_query_method(query)
    result_data = query_data[0]['results']
    result_headers = query_data[0]['headers']
    # TODO: find out why result_data SOMETIMES contains a [None,None] element in the last position
    try:
        result_data.remove([None, None])
    except ValueError:
        pass
        print('Error element does not exist in list')

    x_var_index = -1
    y_var_index = -1
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] == y_var:
            y_var_index = idx
            y_var_title = c['title']
        elif c['name'] == x_var:
            x_var_index = idx
            x_var_title = c['title']
    return x_var_index, y_var_index, result_data, x_var_title, y_var_title


def histogram2d_load_modify_query(query_pk, x_var, y_var):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document

    # for f in doc['from']:
    #     for s in f['select']:
    #         if s['name'] == y_var:
    #             s['groupBy'] = True
    #             s['aggregate'] = 'round0'
    #             s['exclude'] = False
    #         elif s['name'] == x_var:
    #             s['groupBy'] = True
    #             s['aggregate'] = 'round0'
    #             s['exclude'] = False
    #         else:
    #             s['exclude'] = True
    # print doc
    # doc['limit'] = []
    # # doc['orderings'] = [{'name': x_var, 'type': 'ASC'}, {'name': y_var, 'type': 'ASC'}]
    # query.document = doc
    # TODO: Query can be created using the query designer.Fix the error about the double grouping
    xfrom_table = ''
    xtable_col = ''
    yfrom_table = ''
    ytable_col = ''
    xvar_title = ''
    yvar_title = ''
    cursor = None
    for f in doc['from']:
        for s in f['select']:
            if s['name'] == x_var:
                xvar_title = s['title']
                if s['type'] == 'VALUE':
                    v_obj = Variable.objects.get(pk=int(f['type']))
                    if v_obj.dataset.stored_at == 'LOCAL_POSTGRES':
                        xfrom_table = f['name'][:-2] + '_' + f['type']
                        xtable_col = 'value'
                        cursor = connections['default'].cursor()
                    elif v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
                        xfrom_table = str(v_obj.dataset.table_name)
                        xtable_col = str(v_obj.name)
                        cursor = connections['UBITECH_POSTGRES'].cursor()
                    elif v_obj.dataset.stored_at == 'UBITECH_PRESTO':
                        xfrom_table = str(v_obj.dataset.table_name)
                        xtable_col = str(v_obj.name)
                        cursor = get_presto_cursor()
                else:
                    d_obj = Dimension.objects.get(pk=int(s['type']))
                    v_obj = d_obj.variable
                    if v_obj.dataset.stored_at == 'LOCAL_POSTGRES':
                        xfrom_table = f['name'][:-2] + '_' + f['type']
                        xtable_col = d_obj.name + '_' + s['type']
                        cursor = connections['default'].cursor()
                    elif v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
                        xfrom_table = str(v_obj.dataset.table_name)
                        xtable_col = str(d_obj.name)
                        cursor = connections['UBITECH_POSTGRES'].cursor()
                    elif v_obj.dataset.stored_at == 'UBITECH_PRESTO':
                        xfrom_table = str(v_obj.dataset.table_name)
                        xtable_col = str(d_obj.name)
                        cursor = get_presto_cursor()
            elif s['name'] == y_var:
                yvar_title = s['title']
                if s['type'] == 'VALUE':
                    v_obj = Variable.objects.get(pk=int(f['type']))
                    if v_obj.dataset.stored_at == 'LOCAL_POSTGRES':
                        yfrom_table = f['name'][:-2] + '_' + f['type']
                        ytable_col = 'value'
                        cursor = connections['default'].cursor()
                    elif v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
                        yfrom_table = str(v_obj.dataset.table_name)
                        ytable_col = str(v_obj.name)
                        cursor = connections['UBITECH_POSTGRES'].cursor()
                    elif v_obj.dataset.stored_at == 'UBITECH_PRESTO':
                        yfrom_table = str(v_obj.dataset.table_name)
                        ytable_col = str(v_obj.name)
                        cursor = get_presto_cursor()
                else:
                    d_obj = Dimension.objects.get(pk=int(s['type']))
                    v_obj = d_obj.variable
                    if v_obj.dataset.stored_at == 'LOCAL_POSTGRES':
                        yfrom_table = f['name'][:-2] + '_' + f['type']
                        ytable_col = d_obj.name + '_' + s['type']
                        cursor = connections['default'].cursor()
                    elif v_obj.dataset.stored_at == 'UBITECH_POSTGRES':
                        yfrom_table = str(v_obj.dataset.table_name)
                        ytable_col = str(d_obj.name)
                        cursor = connections['UBITECH_POSTGRES'].cursor()
                    elif v_obj.dataset.stored_at == 'UBITECH_PRESTO':
                        yfrom_table = str(v_obj.dataset.table_name)
                        ytable_col = str(d_obj.name)
                        cursor = get_presto_cursor()
            else:
                s['exclude'] = True
    return query, xvar_title, xfrom_table, xtable_col, yvar_title, yfrom_table, ytable_col,cursor




def get_histogram_2d_am(request):
    query_pk = int(str(request.GET.get('query', '0')))
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))
    bins = int(str(request.GET.get('bins', '3')))
    # agg_function = str(request.GET.get('agg_func', 'avg'))
    if query_pk != 0:
        query = AbstractQuery.objects.get(pk=query_pk)
        query = TempQuery(document=query.document)
        doc = query.document

        for f in doc['from']:
            for s in f['select']:
                if s['name'] == y_var:
                    # s['groupBy'] = False
                    # s['aggregate'] = ''
                    s['exclude'] = False
                elif s['name'] == x_var:
                    # s['groupBy'] = False
                    s['exclude'] = False
                    # s['aggregate'] = ''
                else:
                    s['exclude'] = True
        print doc
        doc['limit'] = []
        doc['orderings'] = [{'name': x_var, 'type': 'ASC'}, {'name': y_var, 'type': 'ASC'}]
        query.document = doc

        query_data = execute_query_method(query)

        result_data = query_data[0]['results']
        result_headers = query_data[0]['headers']

        # TODO: find out why result_data SOMETIMES contains a [None,None] element in the last position

        try:
            result_data.remove([None, None])
        except ValueError:
            pass
            print('Error element does not exist in list')

        x_var_index = -1
        y_var_index = -1
        for idx, c in enumerate(result_headers['columns']):
            if c['name'] == y_var:
                y_var_index = idx
            elif c['name'] == x_var:
                x_var_index = idx
    else:
        print ("json-case")
        with open('visualizer/static/visualizer/histogrammyfile.json', 'r') as json_fd:
            jsonfile = json_fd.read()
        print(jsonfile)
        jsonfile = json.loads(jsonfile)
        print jsonfile
        jsondata = []
        x_var_index = 0
        y_var_index = 1
        for idy, s in enumerate(jsonfile['data']):
            jsondata.append([float(s[x_var].encode('ascii')), float(s[y_var].encode('ascii'))])

        result_data = jsondata
        print result_data




    min_x_var = float(min(result_data, key=lambda x: x[x_var_index])[x_var_index])
    max_x_var = float(max(result_data, key=lambda x: x[x_var_index])[x_var_index])
    min_y_var = float(min(result_data, key=lambda x: x[y_var_index])[y_var_index])
    max_y_var = float(max(result_data, key=lambda x: x[y_var_index])[y_var_index])

    mybin_x = np.linspace(start=min_x_var, stop=max_x_var, num=bins + 1)
    mybin_y = np.linspace(start=min_y_var, stop=max_y_var, num=bins + 1)

    # Create Bins for both columns

    bin_x_cont = []
    iter1 = iter(mybin_x)
    iter1.next()
    for el in mybin_x:
        try:
            temp = [el, iter1.next()]
        except:
            break
        bin_x_cont.append(temp)

    bin_y_cont = []
    iter1 = iter(mybin_y)
    iter1.next()
    for el in mybin_y:
        try:
            temp = [el, iter1.next()]
        except:
            break
        bin_y_cont.append(temp)

    # Find Frequency of each combination of bins
    x_col = []
    y_col = []
    for d in result_data:
        x_col.append(float(d[x_var_index]))
        y_col.append(float(d[y_var_index]))
    data_count = len(result_data)
    freq, npbinx, npbiny = np.histogram2d(x_col, y_col, bins=bins)
    freq = [[round((s / data_count), 5) for s in xs] for xs in freq]
    # print freq

    # Create Color Levels
    cmap = plt.cm.coolwarm
    colormap = []
    levels_list = np.linspace(start=0, stop=1, num=bins)
    for el in levels_list:
        colormap.append(float(el))
    # print colormap

    # Create Value Levels
    min_lev = 1
    max_lev = 0
    for rt in freq:
        if (min(rt) < min_lev):
            min_lev = min(rt)
        if (max(rt) > max_lev):
            max_lev = max(rt)

    value_lev = np.linspace(start=min_lev, stop=max_lev, num=bins + 1)
    value_lev_cont = []
    iter3 = iter(value_lev)
    iter3.next()
    for el in value_lev:
        try:
            temp = [el, iter3.next()]
        except:
            break
        value_lev_cont.append(temp)
    # print value_lev_cont


    json_data = []
    bin_x_contr = [[round(s, 3) for s in xs] for xs in bin_x_cont]
    bin_y_contr = [[round(s, 3) for s in xs] for xs in bin_y_cont]
    count = 0
    for count in range(0, len(freq[0])):
        dict = {}
        col_var_name = ("x").encode('ascii')
        row_var_name = ("y").encode('ascii')
        row_var_value = str(1).encode('ascii')
        col_var_value = str(count + 1).encode('ascii')
        dict.update({col_var_name: col_var_value})
        dict.update({row_var_name: row_var_value})
        col_count = 1
        for row in freq:
            value_var_name = ("value" + str(col_count)).encode('ascii')
            dict.update({value_var_name: str(row[count] * 100)})
            color_var_name = ("color" + str(col_count)).encode('ascii')
            dict.update({color_var_name: str(
                convert_to_hex(cmap(color_choice(row[count], colormap, value_lev_cont)))).replace('0x', '#').encode(
                'ascii')})
            val_row_cat_name = ("row_cat" + str(col_count)).encode('ascii')
            dict.update({val_row_cat_name: str(
                str(x_var) + ": " + str(bin_x_contr[count]) + "</br>" + str(y_var) + ": " + str(
                    bin_y_contr[col_count - 1]))})
            col_count = col_count + 1
        json_data.append(dict)
        count = count + 1
    # print (json_data)

    # Create legend for the contour map
    a = np.array([[min_lev * 100, max_lev * 100]])
    pl.figure(figsize=(4, 0.5))
    img = pl.imshow(a, cmap=plt.cm.coolwarm)
    pl.gca().set_visible(False)
    cax = pl.axes([0.1, 0.2, 0.8, 0.6])
    cbar = pl.colorbar(orientation="horizontal", cax=cax)

    cbar.ax.tick_params(labelsize=10, colors="#000000")
    pl.xlabel("'Percentage %'", labelpad=10)
    ts = str(time.time()).replace(".", "")
    legpath = ('visualizer/static/visualizer/img/temp/' + ts + 'h2dcolorbar.png').encode('ascii')
    pl.savefig(legpath, transparent=True, bbox_inches='tight')
    legpath = legpath.split("static/", 1)[1]
    pl.clf()
    pl.close()

    return render(request, 'visualizer/histogram_2d_am.html',
                  {'data': json_data, 'value_col': y_var, 'category_col': x_var, 'bin_count': bins,
                   'bin_x': bin_x_contr, 'bin_y': bin_y_contr, 'legend_id': legpath})



def load_modify_query_chart(query_pk, x_var, y_var_list, agg_function, chart_type, ordering = True):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document
    x_flag = False
    for f in doc['from']:
        for s in f['select']:
            if (s['name'] in y_var_list) and (s['exclude'] is not True):
                s['aggregate'] = agg_function
                s['exclude'] = False
            elif (s['name'] == x_var) and (s['exclude'] is not True):
                s['groupBy'] = True
                s['exclude'] = False
                x_flag = True
            else:
                s['aggregate'] = ''
                s['groupBy'] = False
                s['exclude'] = True
    if ordering == True:
        if x_flag == True:
            doc['orderings'] = [{'name': x_var, 'type': 'ASC'}]
        else:
            raise ValueError('-Variable or Dimension for the X-Axis of Line-Charts and Column-Charts is needed.\n-Variable or Dimension for creating the sub-groups of the Pie-Chart is needed.')
    try:
        with open('visualizer/static/visualizer/visualisations_settings.json') as f:
            json_data = json.load(f)
        doc['limit'] = json_data['visualiser'][chart_type]['limit']
    except:
        pass
    query.document = doc
    return query


def load_modify_query_aggregate(query_pk, var, agg_function):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document
    for f in doc['from']:
        for s in f['select']:
            if (s['name'] == var):
                s['groupBy'] = False
                s['exclude'] = False
                s['aggregate'] = agg_function
            else:
                s['aggregate'] = ''
                s['groupBy'] = False
                s['exclude'] = True
        doc['orderings'] = []

    query.document = doc
    return query



def load_modify_query_timeseries(query_pk, existing_temp_res, temporal_resolution, y_var_list, agg_function,chart_type, ordering = True):
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    doc = query.document

    x_flag = False
    for f in doc['from']:
        for s in f['select']:
            if (s['name'] in y_var_list) and (s['exclude'] is not True):
                s['aggregate'] = agg_function
                s['exclude'] = False
            elif (s['name'].split('_', 1)[1] == 'time') and (s['exclude'] is not True):
                order_var = s['name'].encode('ascii')
                s['groupBy'] = True
                if not existing_temp_res:
                    s['aggregate'] = temporal_resolution
                    min_period = temporal_resolution
                else:
                    # s['aggregate'] = ''
                    min_period = s['aggregate']
                s['exclude'] = False
                x_flag = True
            else:
                # s['aggregate'] = ''
                s['groupBy'] = False
                s['exclude'] = True
    if ordering == True:
        if x_flag == True:
            doc['orderings'] = [{'name': order_var, 'type': 'ASC'}]
        else:
            raise ValueError('Time is not a dimension of the chosen query. The requested visualisation cannot be executed.')
    try:
        with open('visualizer/static/visualizer/visualisations_settings.json') as f:
            json_data = json.load(f)
        doc['limit'] = json_data['visualiser'][chart_type]['limit']
    except:
        pass
    query.document = doc
    return query, order_var, min_period


def get_chart_query_data(query, x_var, y_var_list):
    try:
        query_data = execute_query_method(query)
    except ProgrammingError:
        raise ValueError('The requested visualisation cannot be executed for the chosen query.')
    data = query_data[0]['results']
    result_headers = query_data[0]['headers']

    x_var_index = 0
    y_var_index = []
    y_var_indlist = []
    y_m_unit = []
    y_title_list = []

    for idx, c in enumerate(result_headers['columns']):
        if c['name'] in y_var_list:
            y_var_index.insert(len(y_var_index), idx)
            y_var_indlist.insert(len(y_var_indlist), c['name'])
            y_m_unit.insert(len(y_m_unit), c['unit'].encode('ascii'))
            y_title_list.insert(len(y_title_list), c['title'].encode('ascii'))
        elif c['name'] == x_var:
            x_var_index = idx
            x_var_title = c['title'].encode('ascii')

    json_data = []
    for d in data:
        count = 0
        dict = {}
        for y_index in y_var_index:
            newvar = str(y_var_indlist[count]).encode('ascii')
            dict.update({newvar: str(d[y_index]).encode('ascii')})
            count = count + 1

        dict.update({x_var: str(d[x_var_index])})
        json_data.append(dict)
    return json_data, y_m_unit, y_title_list, x_var_title


def get_chart_dataframe_data(request, notebook_id, df, x_var, y_var_list, ordering = True):
    y_m_unit = []
    y_title_list = []
    livy = False
    service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')
    if len(service_exec) > 0:
        service_exec = service_exec[0]  # GET LAST
        session_id = service_exec.livy_session
        exec_id = service_exec.id
        updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
        livy = service_exec.service.through_livy
    if livy:
        if ordering:
            json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df, order_by=x_var, order_type='ASC')
        else:
            json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df)
    else:
        if ordering:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=x_var,
                                                          order_type='ASC')
        else:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df)
        run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
        json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)

    for x in y_var_list:
        # TODO: use proper names
        y_title_list.insert(0, str(x))
        y_m_unit.insert(0, str('unknown unit'))
    x_var_title = x_var

    return json_data, y_m_unit, y_title_list, x_var_title



def get_line_chart_am(request):
    try:
        query_pk, df, notebook_id = get_data_parameters(request, '')
        x_var = str(request.GET.get('x_var', ''))
        y_var_list = request.GET.getlist('y_var[]')
        agg_function = str(request.GET.get('agg_func', 'avg'))
        if not agg_function.lower() in AGGREGATE_VIZ:
            raise ValueError('The given aggregate function is not valid.')
        if query_pk != 0:
            query = load_modify_query_chart(query_pk, x_var, y_var_list, agg_function, 'line_chart_am')
            json_data, y_m_unit, y_var_title_list, x_var_title = get_chart_query_data(query, x_var, y_var_list)
        elif df != '':
            json_data, y_m_unit, y_var_title_list,x_var_title = get_chart_dataframe_data(request, notebook_id, df, x_var, y_var_list, True)
        else:
            raise ValueError('Either query ID or dataframe name has to be specified.')
    except ValueError as e:
        return render(request, 'error_page.html', {'message': e.message})

    if 'time' in x_var:
        isDate = 'true'
    else:
        isDate = 'false'

    return render(request, 'visualizer/line_chart_am.html',
                  {'data': json.dumps(json_data), 'value_col': y_var_list, 'm_units':y_m_unit, 'title_col': y_var_title_list, 'category_title': x_var_title, 'category_col': x_var, 'isDate': isDate, 'min_period': 'ss'})



def get_time_series_am(request):
    try:
        query_pk, df, notebook_id = get_data_parameters(request, '')
        existing_temp_res = request.GET.get('use_existing_temp_res', '') == 'on'
        temporal_resolution = str(request.GET.get('temporal_resolution', ''))
        y_var_list = request.GET.getlist('y_var[]')
        agg_function = str(request.GET.get('agg_func', 'avg'))
        chart_type = str(request.GET.get('chart_type', 'line'))
        if not agg_function.lower() in AGGREGATE_VIZ:
            raise ValueError('The given aggregate function is not valid.')
        if query_pk != 0:
            query, order_var, min_period = load_modify_query_timeseries(query_pk, existing_temp_res, temporal_resolution, y_var_list, agg_function, 'time_series_am')
            json_data, y_m_unit, y_var_title_list,x_var_title = get_chart_query_data(query, order_var, y_var_list)
            min_chart_period = chart_min_period_finder(min_period)
        elif df != '':
            json_data, y_m_unit, y_var_title_list,x_var_title = get_chart_dataframe_data(request, notebook_id, df, 'time', y_var_list, True)
            order_var = 'time'.encode('ascii')
            min_chart_period = 'ss'
        else:
            raise ValueError('Either query ID or dataframe name has to be specified.')
    except ValueError as e:
        traceback.print_exc()
        return render(request, 'error_page.html', {'message': e.message})
    if chart_type == 'line':
        return render(request, 'visualizer/line_chart_am.html',
                      {'data': json_data, 'value_col': y_var_list, 'm_units': y_m_unit, 'title_col': y_var_title_list, 'category_col': order_var, 'isDate': 'true', 'min_period':min_chart_period})
    else:
        return render(request, 'visualizer/column_chart_am.html',
                      {'data': json_data, 'value_col': y_var_list, 'm_units': y_m_unit, 'title_col': y_var_title_list, 'category_col': order_var, 'isDate': 'true', 'min_period': min_chart_period})


def get_column_chart_am(request):
    try:
        query_pk, df, notebook_id = get_data_parameters(request, '')

        x_var = str(request.GET.get('x_var', ''))
        y_var_list = request.GET.getlist('y_var[]')
        agg_function = str(request.GET.get('agg_func', 'avg'))
        if not agg_function.lower() in AGGREGATE_VIZ:
            raise ValueError('The given aggregate function is not valid.')
        if query_pk != 0:
            query = load_modify_query_chart(query_pk, x_var, y_var_list, agg_function,'column_chart_am')
            json_data, y_m_unit, y_var_title_list, x_var_title = get_chart_query_data(query, x_var, y_var_list)
        elif df != '':
            json_data, y_m_unit, y_var_title_list, x_var_title = get_chart_dataframe_data(request, notebook_id, df, x_var, y_var_list, True)
        else:
            raise ValueError('Either query ID or dataframe name has to be specified.')
    except ValueError as e:
        return render(request, 'error_page.html', {'message': e.message})

    if 'time' in x_var:
        isDate = 'true'
    else:
        isDate = 'false'

    return render(request, 'visualizer/column_chart_am.html',
                  {'data': json_data, 'value_col': y_var_list, 'm_units':y_m_unit, 'title_col':y_var_title_list, 'category_title': x_var_title, 'category_col': x_var, 'isDate': isDate, 'min_period': 'ss'})


def get_pie_chart_am(request):
    try:
        query_pk, df, notebook_id = get_data_parameters(request, '')
        key_var = str(request.GET.get('key_var', ''))
        value_var = str(request.GET.get('value_var', ''))
        agg_function = str(request.GET.get('agg_func', 'sum'))
        if not agg_function.lower() in AGGREGATE_VIZ:
            raise ValueError('The given aggregate function is not valid.')
        if query_pk != 0:
            query = load_modify_query_chart(query_pk, key_var, [value_var], agg_function, 'pie_chart_am')
            json_data, y_m_unit, y_var_title_list, key_var_title = get_chart_query_data(query, key_var, [value_var])
        elif df !='':
            json_data, y_m_unit, y_var_title_list,key_var_title = get_chart_dataframe_data(request, notebook_id, df, key_var, [value_var], True)
        else:
            raise ValueError('Either query ID or dataframe name has to be specified.')
    except ValueError as e:
        return render(request, 'error_page.html', {'message': e.message})

    return render(request, 'visualizer/pie_chart_am.html', {'data': json_data, 'value_var': value_var, 'key_var': key_var, 'var_title': y_var_title_list[0],'category_title':key_var_title, 'agg_function': agg_function.capitalize(), 'unit':y_m_unit[0]})



def load_execute_query_data_table(query_pk, offset, limit, column_choice, chart_type):
    query = AbstractQuery.objects.get(pk=query_pk)
    q = TempQuery(document=query.document)
    doc = q.document
    for f in doc['from']:
        for s in f['select']:
            if (s['name'] in column_choice) and (s['exclude'] is not True):
                s['exclude'] = False
            else:
                s['exclude'] = True
    try:
        with open('visualizer/static/visualizer/visualisations_settings.json') as f:
            json_data = json.load(f)
        doc['limit'] = json_data['visualiser'][chart_type]['limit']
    except:
        pass
    doc['offset'] = offset
    q.document = doc
    try:
        result = execute_query_method(q)[0]
    except ProgrammingError:
        raise ValueError('The requested visualisation cannot be executed for the chosen query.')
    data = result['results']
    headers = result['headers']['columns']
    return data, headers


def load_execute_dataframe_data(request, df, notebook_id):
    livy = False
    service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')
    if len(service_exec) > 0:
        service_exec = service_exec[0]  # GET LAST
        session_id = service_exec.livy_session
        exec_id = service_exec.id
        updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
        livy = service_exec.service.through_livy
    if livy:
        data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df)
    else:
        toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df)
        run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
        data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
    headers = [key for key in data[0].keys()]
    return data, headers



def get_data_table(request):
    try:
        query_pk, df, notebook_id = get_data_parameters(request, '')
        column_choice = request.GET.getlist('column_choice[]')
        limit = 500
        offset = int(request.GET.get('offset', 0))
        if not column_choice:
            raise ValueError('At least one column of the given query has to be selected.')
        if query_pk != 0:
            if column_choice.__len__() != 0:
                data, headers = load_execute_query_data_table(query_pk, offset, limit, column_choice,'data_table')
            else:
                data = []
                headers = []
            isJSON = False
        elif df != '':
            data, headers = load_execute_dataframe_data(request, df, notebook_id)
            isJSON = True
        else:
            raise ValueError('Either query ID or dataframe name has to be specified.')
    except ValueError as e:
        return render(request, 'error_page.html', {'message': e.message})

    if data.__len__() < limit:
        has_next = False
    else:
        has_next = True

    return render(request, 'visualizer/data_table.html', {'headers': headers, 'data': data, 'query_pk': int(query_pk), 'offset':offset,'has_next': has_next, 'neg_step': limit*(-1), 'pos_step': limit, 'column_choice': column_choice, 'isJSON': isJSON, 'df': df, 'notebook_id': notebook_id})

def map_oil_spill_hcmr(map):
    filepath = 'visualizer/static/visualizer/files/kml.json'
    color = 'green'
    map, polygons = hcmr_create_polygons_on_map(map, filepath, color)
    return map, polygons


def hcmr_create_polygons_on_map(map, filepath, polygon_color):
    with open(filepath) as f:
        kml_data = json.load(f)

    shapely_polygons = []
    pol_group_layer = folium.map.FeatureGroup(name='Protected Areas Layer:' + str(time.time()).replace(".", "_"),
                                              overlay=True,
                                              control=True).add_to(map)
    count_polygons = 0
    for placemark in kml_data['placemarks']:
        for polygon in placemark['polygons']:
                points_inner = []
                points_outer = []
                points = []
                external_shapely = []
                internal_shapely = []
                for coordinate in polygon['outer_boundary']['coordinates']:
                    points_outer.append([float(coordinate['latitude']), float(coordinate['longitude'])])
                    external_shapely.append((float(coordinate['latitude']), float(coordinate['longitude'])))
                points.append(points_outer)
                for inner_polygon in polygon['inner_boundaries']:
                    hole = []
                    single_internal_shapely = []
                    for coordinate in inner_polygon['coordinates']:
                        hole.append([float(coordinate['latitude']), float(coordinate['longitude'])])
                        single_internal_shapely.append((float(coordinate['latitude']), float(coordinate['longitude'])))
                    points.append(hole)
                    points_inner.append(hole)
                    internal_shapely.append(single_internal_shapely)
                count_polygons = count_polygons+1
                folium.PolyLine(points, color=polygon_color, weight=2.0, opacity=0.8,
                                fill=polygon_color
                                ).add_to(pol_group_layer)
                shapely_polygons.append(Polygon(external_shapely, internal_shapely))
    return map, shapely_polygons


def color_point_oil_spill(shapely_polygons, point_lat,point_lon):
    shapely_point = Point(point_lat, point_lon)
    color = 'lightblue'
    for pol in shapely_polygons:
        if pol.contains(shapely_point):
            color = 'red'
    return color

def color_point_oil_spill2(red_points_list, point):
    if point in red_points_list:
        return 'red'
    else:
        return 'lightblue'

def map_routes(m):
    routes_query = """SELECT centroids_ci_1.latitude, centroids_ci_1.longitude,centroids_ci_1.route FROM centroids_ci_1  ORDER BY centroids_ci_1.route,centroids_ci_1.latitude, centroids_ci_1.longitude """
    cursor = connections['UBITECH_POSTGRES'].cursor()
    cursor.execute(routes_query)
    data = cursor.fetchall()
    pol_group_layer = folium.map.FeatureGroup(
        name='Vessel-Routes - Layer:' + str(time.time()).replace(".", "_") , overlay=True,
        control=True).add_to(m)

    curr_route = data[0][2]
    route_points = []
    for d in data:
        if d[2] == curr_route:
            route_points.append([float(d[0]), float(d[1])])
        else:
            folium.PolyLine(route_points, color='orange', weight=2.5, opacity=0.8,
                            ).add_to(pol_group_layer)
            route_points = []
            route_points.append([float(d[0]), float(d[1])])
            curr_route = d[2]

    folium.PolyLine(route_points, color='orange', weight=2.5, opacity=0.8,
                    ).add_to(pol_group_layer)

    return m


def add_oil_spill_ais_layer(m):
    pol_group_layer = folium.map.FeatureGroup(name='AIS data layer : ' + str(time.time()).replace(".", "_"),
                                              overlay=True,
                                              control=True).add_to(m)

    q = AbstractQuery(document={"from": [{"name": "platform_type_name_0", "type": 1824, "select": [
        {"name": "platform_type_name_0", "type": "VALUE", "title": "platform_type_name_0", "exclude": False, "groupBy": False, "datatype": "STRING",
         "aggregate": ""},
        {"name": "i0_time", "type": 5615, "title": "time", "exclude": "", "groupBy": False, "datatype": "TIMESTAMP", "aggregate": ""},
        {"name": "i0_latitude", "type": 5614, "title": "latitude", "exclude": "", "groupBy": False, "datatype": "FLOAT", "aggregate": ""},
        {"name": "i0_longitude", "type": 5613, "title": "longitude", "exclude": "", "groupBy": False, "datatype": "FLOAT", "aggregate": ""},
        {"name": "i0_platform_id", "type": 5612, "title": "platform_id", "exclude": "", "groupBy": False, "datatype": "FLOAT", "aggregate": ""}]}],
                                "limit": 100, "offset": 0, "filters": {"a": {"a": "<5614,5613>", "b": "<<36,23>,<38,26>>", "op": "inside_rect"},
                                                                      "b": {"a": {"a": "i0_time", "b": "'2011-03-12 13:00'", "op": "lte_time"},
                                                                            "b": {"a": "i0_time", "b": "'2011-03-01 12:00'", "op": "gte_time"},
                                                                            "op": "AND"}, "op": "AND"}, "distinct": False, "orderings": []})

    data = q.execute()[0]['results']

    for d in data:
        folium.Marker(
            location=[d[2], d[3]],
            icon=folium.Icon()).add_to(pol_group_layer)
    return m


def map_markers_in_time_hcmr(request):
    m = create_map()
    # comment out map_routes until you find a way to cleanup the route-data
    # m = map_routes(m)
    FMT, df, duration, lat_col, lon_col, markerType, marker_limit, notebook_id, order_var, query_pk, data_file, rp_file, natura_layer, ais_layer, time_interval = hcmr_service_parameters(request)
    if query_pk != 0:
        q = AbstractQuery.objects.get(pk=int(query_pk))
        q = Query(document=q.document)
        doc = q.document

        doc['limit'] = marker_limit
        doc['orderings'] = [{'name': order_var, 'type': 'ASC'}]

        for f in doc['from']:
            for s in f['select']:
                if s['name'] == order_var:
                    s['exclude'] = False
                elif s['name'].split('_', 1)[1] == 'latitude':
                    s['exclude'] = False
                elif s['name'].split('_', 1)[1] == 'longitude':
                    s['exclude'] = False
                # elif s['name'] == var:
                #     s['exclude'] = False
                else:
                    s['exclude'] = True

        q.document = doc

        query_data = execute_query_method(q)
        data = query_data[0]['results']
        result_headers = query_data[0]['headers']
        print(result_headers)
        has_data = len(data) > 0
        var_index = order_index = lon_index = lat_index = -1

        for idx, c in enumerate(result_headers['columns']):
            # if c['name'] == var:
            #     var_index = idx
            if c['name'].split('_', 1)[1] == 'latitude':
                lat_index = idx
            elif c['name'].split('_', 1)[1] == 'longitude':
                lon_index = idx
            elif c['name'] == order_var:
                order_index = idx

        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(d[lon_index]), float(d[lat_index])],
                },
                "properties": {
                    "times": [str(d[order_index])],
                    "style": {
                        "color": "blue",
                    }
                }
            }
            for d in data
        ]
        tdelta = data[1][order_index] - data[0][order_index]
        period = 'PT{0}S'.format(tdelta.seconds)
    else:
        livy = False
        service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')
        if len(service_exec) > 0:
            service_exec = service_exec[0]  # GET LAST
            session_id = service_exec.livy_session
            exec_id = service_exec.id
            updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
            livy = service_exec.service.through_livy
        if livy:
            data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df, order_by=order_var, order_type='ASC')
        else:
            # toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=order_var, order_type='ASC')
            # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
            # data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            # delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            data = []
            with open('visualizer/static/visualizer/files/' + data_file) as json_data:
                data = json.load(json_data)
                print(data[:3])
        has_data = len(data) > 0
        min_lat = 90
        max_lat = -90
        min_lon = 180
        max_lon = -180
        for d in data:
            min_lat, max_lat, min_lon, max_lon = max_min_lat_lon_check(min_lat, max_lat, min_lon, max_lon, float(d[lat_col]), float(d[lon_col]))
        m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
        # filtered_polygons = []
        # simulation_frame = Polygon([(min_lat, min_lon), (max_lat,min_lon), (max_lat,max_lon),(min_lat,max_lon)])
        # count_inters = 0
        # for pol in shapely_polygons:
        #     if simulation_frame.intersects(pol):
        #         filtered_polygons.append(pol)
        #         count_inters = count_inters + 1
        # print 'intersects:' + str(count_inters)
        red_points = []
        if natura_layer == "true":
            with open('visualizer/static/visualizer/files/'+ rp_file, 'r') as file:
                line = file.readline()
                while line:
                    red_points.append((float(line.split(',')[0]), float(line.split(',')[1])))
                    line = file.readline()
                file.close()
        # red_points = []
        # with open('red_points.txt', 'r') as file:
        #     line = file.readline()
        #     red_points.append((float(line.split(',')[0]), float(line.split(',')[1])))
        #     file.close()

        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(d[lon_col]), float(d[lat_col])],
                },
                "properties": {
                    "times": [str(d[order_var])],
                    "style": {
                        # "color": color_point_oil_spill(filtered_polygons, float(d[lat_col]), float(d[lon_col])),
                        "color": color_point_oil_spill2(red_points, (d[lat_col], d[lon_col])),
                        # "color": "red"
                    }
                }
            }
            for d in data
        ]
        # print data

        # tdelta = datetime.strptime(data[1][order_var], FMT) - datetime.strptime(data[0][order_var], FMT)

        available_times = set([d[order_var] for d in data])
        period = 'PT'+ str(time_interval) +'H'


    if has_data:
        if ais_layer == "true":
            m = add_oil_spill_ais_layer(m)

        if natura_layer == "true":
            m, shapely_polygons = map_oil_spill_hcmr(m)

    features = convert_unicode_json(features)
    # folium.LayerControl().add_to(m)

    # FOR SCREENSHOTS EVERY 6 or 4 hours
    print 'time interval ' + str(time_interval)
    if int(time_interval) == 4:
        ignore_every = 4
    elif int(time_interval) >= 1 and int(time_interval) <= 6:
        ignore_every = 6/int(time_interval)
    else:
        ignore_every = 1


    m.save('templates/map.html')
    f = open('templates/map.html', 'r')
    map_html = f.read()
    soup = BeautifulSoup(map_html, 'html.parser')
    map_id = soup.find("div", {"class": "folium-map"}).get('id')
    js_all = soup.findAll('script')
    if len(js_all) > 5:
        js_all = [js.prettify() for js in js_all[5:]]
    css_all = soup.findAll('link')
    if len(css_all) > 3:
        css_all = [css.prettify() for css in css_all[3:]]
    f.close()
    js_all = [js.replace('worldCopyJump', 'preferCanvas: true , worldCopyJump') for js in js_all]
    os.remove('templates/map.html')

    return render(request, 'visualizer/map_markers_in_time.html',
                      {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'data': features, 'time_interval': period,'duration':duration, 'markerType': markerType, 'has_data': has_data, 'ignore_every': ignore_every, 'available_times': available_times})


def hcmr_service_parameters(request):
    marker_limit = int(request.GET.get('markers', 1000))
    order_var = str(request.GET.get('order_var', 'time'))
    query_pk = int(str(request.GET.get('query', 0)))
    notebook_id = str(request.GET.get('notebook_id', ''))
    df = str(request.GET.get('df', ''))
    lat_col = str(request.GET.get('lat_col', 'latitude'))
    lon_col = str(request.GET.get('lon_col', 'longitude'))
    markerType = str(request.GET.get('markerType', ''))
    FMT = '%Y-%m-%d %H:%M:%S'
    duration = 'PT0H'
    data_file = str(request.GET.get('data_file', ''))
    rp_file = str(request.GET.get('red_points_file', ''))
    natura_layer = str(request.GET.get('natura_layer', 'false'))
    ais_layer = str(request.GET.get('ais_layer', 'false'))
    time_interval = str(request.GET.get('time_interval',2))
    return FMT, df, duration, lat_col, lon_col, markerType, marker_limit, notebook_id, order_var, query_pk, data_file, rp_file, natura_layer, ais_layer,time_interval


def max_min_lat_lon_check(min_lat, max_lat, min_lon, max_lon, latitude, longitude):
    if latitude > max_lat:
        max_lat = float(latitude)
    if latitude < min_lat:
        min_lat = float(latitude)
    if longitude > max_lon:
        max_lon = float(longitude)
    if longitude < min_lon:
        min_lon = float(longitude)
    return min_lat, max_lat, min_lon, max_lon

def create_plotline_arrows(points, m, pol_group_layer, color):
    last_arrow = folium.RegularPolygonMarker(location=[points[len(points) - 1][0], points[len(points) - 1][1]],
                                             fill_color='white', number_of_sides=6,
                                             radius=9).add_to(m)
    last_arrow.add_to(pol_group_layer)
    first_arrow = True
    for i in range(1, len(points)):
        arrows = get_arrows(m, 1, first_arrow, locations=[points[i-1], points[i]], color=color, size=7)
        first_arrow = False
        for arrow in arrows:
            arrow.add_to(pol_group_layer)




def get_arrows(m, n_arrows, first_arrow, locations, color='#68A7EE', size=5):
    '''
    Get a list of correctly placed and rotated
    arrows/markers to be plotted

    Parameters
    locations : list of lists of lat lons that represent the
                start and end of the line.
                eg [[41.1132, -96.1993],[41.3810, -95.8021]]
    arrow_color : default is 'blue'
    size : default is 6
    n_arrows : number of arrows to create.  default is 3
    Return
    list of arrows/markers
    '''

    Point = namedtuple('Point', field_names=['lat', 'lon'])
    p1 = Point(locations[0][0], locations[0][1])
    p2 = Point(locations[1][0], locations[1][1])
    rotation = get_bearing(p1, p2) - 90
    arrows = []
    if first_arrow:
        arrows.append(folium.RegularPolygonMarker(location=[locations[0][0], locations[0][1]],
                                                  fill_color='white', number_of_sides=6,
                                                  radius=9, rotation=rotation).add_to(m))
    else:
        arrows.append(folium.RegularPolygonMarker(location=[locations[0][0],locations[0][1]],
                                                    fill_color=color, number_of_sides=3,
                                                    radius=size, rotation=rotation).add_to(m))
    return arrows


def get_bearing(p1, p2):
    '''
    Returns compass bearing from p1 to p2

    Parameters
    p1 : namedtuple with lat lon
    p2 : namedtuple with lat lon

    Return
    compass bearing of type float

    Notes
    Based on https://gist.github.com/jeromer/2005586
    '''

    long_diff = np.radians(p2.lon - p1.lon)
    lat1 = np.radians(p1.lat)
    lat2 = np.radians(p2.lat)
    x = np.sin(long_diff) * np.cos(lat2)
    y = (np.cos(lat1) * np.sin(lat2)
         - (np.sin(lat1) * np.cos(lat2)
            * np.cos(long_diff)))
    bearing = np.degrees(np.arctan2(x, y))
    if bearing < 0:
        return bearing + 360
    return bearing

def get_aggregate_query_data(query, variable):
    try:
        query_data = execute_query_method(query)
    except ProgrammingError:
        raise ValueError('The requested visualisation cannot be executed for the chosen query.')
    data = query_data[0]['results']
    result_headers = query_data[0]['headers']

    variable_index = 0
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] == variable:
            variable_index = idx


    value = round(data[0][variable_index], 3)
    unit = result_headers['columns'][variable_index]['unit']
    var_title = result_headers['columns'][variable_index]['title']
    return value, unit, var_title


def get_aggregate_value(request):
    try:
        query_pk, df, notebook_id = get_data_parameters(request, '')

        variable = str(request.GET.get('variable', ''))
        agg_function = str(request.GET.get('agg_function', 'AVG'))
        if not agg_function.lower() in AGGREGATE_VIZ:
            raise ValueError('The given aggregate function is not valid.')
        if query_pk != 0:
            query = load_modify_query_aggregate(query_pk, variable, agg_function)
            value, unit, var_title = get_aggregate_query_data(query, variable)
        else:
            value, unit, var_list, var_title = get_chart_dataframe_data(request, notebook_id, df, '', [variable], False)
    except ValueError as e:
        return render(request, 'error_page.html', {'message': e.message})

    return render(request, 'visualizer/aggregate_value.html', {'value': value, 'unit': unit, 'agg_func':agg_function, 'var_title': var_title})

def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

def agg_func_selector(agg_func,data,bins,y_var_index,x_var_index):
    final_data=[]
    try:
        if (agg_func=='avg'):
            it1=iter(bins)
            sum=0
            bin = it1.next()
            count=0
            for d in data:
                # print("data:"+str(d[x_var_index])+" is in "+ str(bin)+"?")
                if(frange(bin,d[x_var_index])):
                    # print("Yes")
                    sum=sum+d[y_var_index]
                    count=count+1
                else:
                    # print ("NEXT BUCKET!!!!!!!!!!!!")
                    avg=sum/count
                    final_data.append(avg)
                    sum=0
                    avg=0
                    bin = it1.next()
                    # print ("First Element Added.")
                    sum = d[y_var_index]
                    count = 1
            # print ("Last bucket completed.")
            avg = sum / count
            final_data.append(avg)
            return final_data

        elif(agg_func=='sum'):
            it1 = iter(bins)
            sum = 0
            bin = it1.next()
            for d in data:
                # print("data:" + str(d[x_var_index]) + " is in " + str(bin) + "?")
                if (frange(bin, d[x_var_index])):
                    # print("Yes")
                    sum = sum + d[y_var_index]
                else:
                    # print ("NEXT BUCKET!!!!!!!!!!!!")
                    final_data.append(sum)
                    sum=d[y_var_index]
                    # print ("First Element Added.")
                    bin = it1.next()
            # print ("Last bucket completed.")
            final_data.append(sum)
            return final_data

        elif (agg_func=='min'):
            it1 = iter(bins)
            bin = it1.next()
            mymin = float(max(data, key=lambda x: x[y_var_index])[y_var_index])
            for d in data:
                if (frange(bin, d[x_var_index])):
                    if(d[y_var_index]<mymin):
                        mymin=d[y_var_index]
                else:
                    final_data.append(mymin)
                    mymin = float(max(data, key=lambda x: x[y_var_index])[y_var_index])
                    if (d[y_var_index] < mymin):
                        mymin = d[y_var_index]
                    bin = it1.next()
            final_data.append(mymin)
            return final_data

        elif (agg_func=='max'):
            it1 = iter(bins)
            bin = it1.next()
            mymax = float(min(data, key=lambda x: x[y_var_index])[y_var_index])
            for d in data:
                if (frange(bin, d[x_var_index])):
                    if (d[y_var_index] > mymax):
                        mymax = d[y_var_index]
                else:
                    final_data.append(mymax)
                    mymax = float(min(data, key=lambda x: x[y_var_index])[y_var_index])
                    if (d[y_var_index] > mymax):
                        mymax = d[y_var_index]
                    bin = it1.next()
            final_data.append(mymax)
            return final_data

    except:
        return final_data


def frange(dist,numb):
    start=dist[0]
    end=dist[1]
    if ((numb<end) and (numb>=start)):
        return True
    else:
        return False


def convert_to_hex(rgba_color) :
    red = int(rgba_color[0]*255)
    green = int(rgba_color[1]*255)
    blue = int(rgba_color[2]*255)
    return '0x{r:02x}{g:02x}{b:02x}'.format(r=red,g=green,b=blue)


def color_choice(value,map,value_level):
    count=0
    for el in value_level:
        if (value<el[1] and value>=el[0]):
            return map[count]
        count=count+1
    return map[len(map)-1]


def map_script(htmlmappath):
    map_html = open(htmlmappath, 'r').read()
    soup = BeautifulSoup(map_html, 'html.parser')
    map_id = soup.find("div", {"class": "folium-map"}).get('id')
    js_all = soup.findAll('script')
    if len(js_all) > 5:
        js_all = [js.prettify() for js in js_all[5:]]

    core_script = js_all[-1]
    # core_script.replace(map_id, used_map_id)
    useful_part = \
    core_script.split("console.log('entered fullscreen');")[1].split("});", 1)[1].strip().split("</script>")[0]
    js_all[-1] = "<script>" + useful_part + "</script>"


# def test_request_include(request):
#     return render(request, 'visualizer/test_request_include.html', {})
#
#
# def test_request(request):
#     return render(request, 'visualizer/test_request.html', {})
#
#
# def get_map_simple(request):
#     return render(request, 'visualizer/map_viz.html', {})


# class MapIndex(APIView):
#     def get(self, request):
#         form = MapForm()
#         return render(request, 'visualizer/map_index.html', {'form': form})
#
#     def post(self, request):
#         form = MapForm(request.POST)
#         if form.is_valid():
#             tiles = request.data["tiles"]
#             if tiles == "marker clusters":
#                 return map_viz_folium(request)
#             else:
#                 return map_heatmap(request)
#
# class MapAPI(APIView):
#     def get(self, request):
#
#         tiles = request.GET.get("tiles", "marker clusters")
#         if tiles == "marker clusters":
#             return map_viz_folium(request)
#         else:
#             return get_map_heatmap(request)
#
# def map_viz(request):
#     return render(request, 'visualizer/map_viz.html', {})


def map_viz_folium(request):
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 30
    min_zoom = 2,

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   min_zoom=min_zoom,
                   max_bounds=True,
                   tiles=tiles_str+token_str,
                   attr=attr_str)

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True).add_to(m)

    marker_cluster = plugins.MarkerCluster(name="Markers", popups=False).add_to(m)

    if request.method == "POST":

        form = MapForm(request.POST)
        if form.is_valid():
            data = request.data
            line = request.POST.get("line", 'no')
            markersum = data["markers"]
            ship = data["ship"]
            mindate = str(request.POST.get("min_date", '2000-01-01 00:00:00'))
            maxdate = str(request.POST.get("max_date", '2017-12-31 23:59:59'))
        else:
            markersum = 50
            line = 'no'
            ship = "all"
            mindate = 2000
            maxdate = 2017

    else:
        line = request.GET.get("line", 'no')
        markersum = int(request.GET.get("markers", 50))
        ship = request.GET.get("ship", "all")
        mindate = str(request.GET.get("min_date", '2000-01-01 00:00:00'))
        maxdate = str(request.GET.get("max_date", '2017-12-31 23:59:59'))

    query_pk = int(str(request.GET.get('query', '')))

    data = get_data(query_pk, markersum, ship, mindate, maxdate)
    # var_index = data['var']
    ship_index = data['ship']
    time_index = data['time']
    lat_index = data['lat']
    lon_index = data['lon']
    data = data['data']

    course = []
    currboat = data[0][ship_index]
    # import pdb;
    # pdb.set_trace()
    for index in range(0, len(data)):
        d = data[index]
        lat = float(d[lat_index])
        lon = float(d[lon_index])
        ship = int(d[ship_index])
        date = str(d[time_index])

        url = 'https://cdn4.iconfinder.com/data/icons/geo-points-1/154/{}'.format
        icon_image = url('geo-location-gps-sea-location-boat-ship-512.png')
        icon = CustomIcon(
            icon_image,
            icon_size=(40, 40),
            icon_anchor=(20, 20),
        )
        message = '<b>Ship</b>: ' + ship.__str__() + "<br><b>At :</b> [" + lat.__str__() + " , " + lon.__str__() + "] <br><b>On :</b> " + date
        folium.Marker(
            location=[lat, lon],
            icon=icon,
            popup=message
        ).add_to(marker_cluster)

        if line != 'no':
            if ship == currboat:
                course.append((np.array([lat, lon]) * np.array([1, 1])).tolist())
            if ship != currboat or index == len(data)-1:
                boat_line = folium.PolyLine(
                    locations=course,
                    weight=1,
                    color='blue'
                ).add_to(m)
                attr = "{'font-weight': 'normal', 'font-size': '18', 'fill': 'white', 'letter-spacing': '80'}"
                plugins.PolyLineTextPath(
                    boat_line,
                    '\u21D2',
                    repeat=True,
                    offset=5,
                    attributes=attr,
                ).add_to(m)

                if ship != currboat:
                    course = (np.array([lat, lon]) * np.array([1, 1])).tolist()
                    currboat = ship

    m.save('templates/map.html')
    map_html = open('templates/map.html', 'r').read()
    soup = BeautifulSoup(map_html, 'html.parser')
    map_id = soup.find("div", {"class": "folium-map"}).get('id')
    # print map_id
    js_all = soup.findAll('script')
    # print(js_all)
    if len(js_all) > 5:
        js_all = [js.prettify() for js in js_all[5:]]
    # print(js_all)
    css_all = soup.findAll('link')
    if len(css_all) > 3:
        css_all = [css.prettify() for css in css_all[3:]]
    # print js
    # os.remove('templates/map.html')
    return render(request, 'visualizer/map_viz_folium.html', {'map_id': map_id, 'js_all': js_all, 'css_all': css_all})


def valid_entry(entry, ship, minyear, maxyear):
    entryship = entry[2]
    entrydate = entry[3]
    year = entrydate.split('-')
    year = int(year[0])

    if ship != "all":
        ship = int(ship)
        if entryship != ship:
            return False
    if year < minyear or year > maxyear:
        return False
    return True


def transpose(date):
    date_time = date
    pattern = '%Y-%m-%d %H:%M:%S'
    epoch = int(time.mktime(time.strptime(date_time, pattern)))*1000
    return epoch


def createjson(lonlat,time,status,color):
    geo = "{'type': 'Feature', 'geometry':{'type': 'Point','coordinates':" + str(lonlat) + ",}, 'properties': { 'times':" + str(time) + ",'status':'" + str(status) + "','style':{'icon':'circle','iconstyle':{'fillColor':'"+str(color)+"','radius':5},}}}"

    return geo




def execute_query_method(q):
    result = q.execute()
    return result

def chart_min_period_finder(min_period):
    if min_period == 'date_trunc_minute':
        return 'mm'
    elif min_period == 'date_trunc_hour':
        return 'hh'
    elif min_period == 'date_trunc_day':
        return 'DD'
    elif min_period == 'date_trunc_month':
        return 'MM'
    elif min_period == 'date_trunc_year':
        return 'YYYY'
    else:
        return 'ss'

def get_pie_chart(request):
    type = 'pieChart'
    chart = pieChart(name=type, color_category='category20c', height=450, width=450)
    xdata = ["Orange", "Banana", "Pear", "Kiwi", "Apple", "Strawberry", "Pineapple"]
    ydata = [3, 4, 0, 1, 5, 7, 3]
    extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
    chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
    chart.buildcontent()
    html = chart.htmlcontent
    return render(request, 'visualizer/piechart.html', {'html': html})


def get_line_chart(request):
    try:
        # Gather the arguments
        x_var = str(request.GET.get('x_var', ''))
        y_var = str(request.GET.get('y_var', ''))
        query = str(request.GET.get('query', ''))

        # Perform a query and get data
        headers, data = get_test_data(query, request.user)
        print data[:100]
        # Find the columns of the selected variables and the rest dimensions
        other_dims = list()
        for idx, col in enumerate(headers['columns']):
            if str(col['name']) == x_var:
                x_var_col = idx
            elif str(col['name']) == y_var:
                y_var_col = idx
            else:
                other_dims.append(idx)
        print x_var_col
        print y_var_col
        print other_dims
        # Find the first values for each of the rest dimensions
        other_dims_first_vals = list()
        for d in other_dims:
            other_dims_first_vals.append(str(data[0][d]))
        print other_dims_first_vals
        # Select only data with the same (first) value on any other dimensions except lat/lon
        data = [(str(d[x_var_col]), float(d[y_var_col])) for d in data if filter_data(d, other_dims, other_dims_first_vals) == 0]
        print data[:100]

        xdata = []
        ydata = []
        for x, y in sorted(data):
            xdata.append(time.mktime(datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timetuple()) * 1000)
            ydata.append(y)
        print ydata
        print xdata

        type = "lineChart"
        chart = lineChart(name=type, x_is_date=True,
                          x_axis_format="%Y-%m-%d %H:%M:%S", y_axis_format=".3f",
                          width=1000, height=500,
                          show_legend=True)

        extra_serie = {"tooltip": {"y_start": "Dummy ", "y_end": " Dummy"},
                       "date_format": "%Y-%m-%d %H:%M:%S"}
        chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
        chart.buildcontent()
        html = chart.htmlcontent
        return render(request, 'visualizer/piechart.html', {'html': html})
    except HttpResponseNotFound:
        return HttpResponseNotFound
    except Exception:
        return HttpResponseNotFound


def get_table_zep(request):
    query = int(str(request.GET.get('query', '')))
    raw_query = Query.objects.get(pk=query).raw_query
    # print raw_query

    notebook_id = create_zep_note(name='bdo_test')
    query_paragraph_id = create_zep__query_paragraph(notebook_id, title='query_paragraph', raw_query=raw_query)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=query_paragraph_id)
    reg_table_paragraph_id = create_zep_reg_table_paragraph(notebook_id=notebook_id, title='sort_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=reg_table_paragraph_id)
    viz_paragraph_id = create_zep_viz_paragraph(notebook_id=notebook_id, title='viz_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=viz_paragraph_id)

    return redirect("http://localhost:8080/#/notebook/"+str(notebook_id)+"/paragraph/"+str(viz_paragraph_id)+"?asIframe")


def get_line_chart_zep(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = Query.objects.get(pk=query_pk)
    raw_query = query.raw_query
    # print raw_query
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))

    notebook_id = create_zep_note(name='bdo_test')
    query_paragraph_id = create_zep__query_paragraph(notebook_id, title='query_paragraph', raw_query=raw_query)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=query_paragraph_id)
    sort_paragraph_id = create_zep_sort_paragraph(notebook_id=notebook_id, title='sort_paragraph', sort_col=x_var)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=sort_paragraph_id)
    reg_table_paragraph_id = create_zep_reg_table_paragraph(notebook_id=notebook_id, title='sort_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=reg_table_paragraph_id)
    viz_paragraph_id = create_zep_viz_paragraph(notebook_id=notebook_id, title='viz_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=viz_paragraph_id)

    set_zep_paragraph_line_chart(notebook_id=notebook_id, paragraph_id=viz_paragraph_id, query_doc=query.document, y_vars=y_var, x_var=x_var)
    # drop_all_paragraph_id = create_zep_drop_all_paragraph(notebook_id=notebook_id, title='')
    # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=drop_all_paragraph_id)

    # restart_zep_interpreter(interpreter_id='')

    return redirect("http://localhost:8080/#/notebook/"+str(notebook_id)+"/paragraph/"+str(viz_paragraph_id)+"?asIframe")


def get_bar_chart_zep(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = Query.objects.get(pk=query_pk)
    raw_query = query.raw_query
    # print raw_query
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))

    notebook_id = create_zep_note(name='bdo_test')
    query_paragraph_id = create_zep__query_paragraph(notebook_id, title='query_paragraph', raw_query=raw_query)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=query_paragraph_id)
    sort_paragraph_id = create_zep_sort_paragraph(notebook_id=notebook_id, title='sort_paragraph', sort_col=x_var)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=sort_paragraph_id)
    reg_table_paragraph_id = create_zep_reg_table_paragraph(notebook_id=notebook_id, title='sort_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=reg_table_paragraph_id)
    viz_paragraph_id = create_zep_viz_paragraph(notebook_id=notebook_id, title='viz_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=viz_paragraph_id)

    set_zep_paragraph_bar_chart(notebook_id=notebook_id, paragraph_id=viz_paragraph_id, query_doc=query.document, y_vars=y_var, x_var=x_var)
    # drop_all_paragraph_id = create_zep_drop_all_paragraph(notebook_id=notebook_id, title='')
    # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=drop_all_paragraph_id)

    # restart_zep_interpreter(interpreter_id='')

    return redirect("http://localhost:8080/#/notebook/"+str(notebook_id)+"/paragraph/"+str(viz_paragraph_id)+"?asIframe")


def get_area_chart_zep(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = Query.objects.get(pk=query_pk)
    raw_query = query.raw_query
    # print raw_query
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))

    notebook_id = create_zep_note(name='bdo_test')
    query_paragraph_id = create_zep__query_paragraph(notebook_id, title='query_paragraph', raw_query=raw_query)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=query_paragraph_id)
    sort_paragraph_id = create_zep_sort_paragraph(notebook_id=notebook_id, title='sort_paragraph', sort_col=x_var)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=sort_paragraph_id)
    reg_table_paragraph_id = create_zep_reg_table_paragraph(notebook_id=notebook_id, title='sort_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=reg_table_paragraph_id)
    viz_paragraph_id = create_zep_viz_paragraph(notebook_id=notebook_id, title='viz_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=viz_paragraph_id)

    set_zep_paragraph_area_chart(notebook_id=notebook_id, paragraph_id=viz_paragraph_id, query_doc=query.document, y_vars=y_var, x_var=x_var)
    # drop_all_paragraph_id = create_zep_drop_all_paragraph(notebook_id=notebook_id, title='')
    # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=drop_all_paragraph_id)

    # restart_zep_interpreter(interpreter_id='')

    return redirect("http://localhost:8080/#/notebook/" + str(notebook_id) + "/paragraph/" + str(viz_paragraph_id) + "?asIframe")


def get_scatter_chart_zep(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = Query.objects.get(pk=query_pk)
    raw_query = query.raw_query
    # print raw_query
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))

    notebook_id = create_zep_note(name='bdo_test')
    query_paragraph_id = create_zep__query_paragraph(notebook_id, title='query_paragraph', raw_query=raw_query)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=query_paragraph_id)
    sort_paragraph_id = create_zep_sort_paragraph(notebook_id=notebook_id, title='sort_paragraph', sort_col=x_var)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=sort_paragraph_id)
    reg_table_paragraph_id = create_zep_reg_table_paragraph(notebook_id=notebook_id, title='sort_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=reg_table_paragraph_id)
    viz_paragraph_id = create_zep_viz_paragraph(notebook_id=notebook_id, title='viz_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=viz_paragraph_id)

    set_zep_paragraph_scatter_chart(notebook_id=notebook_id, paragraph_id=viz_paragraph_id, query_doc=query.document, y_vars=y_var, x_var=x_var)
    # drop_all_paragraph_id = create_zep_drop_all_paragraph(notebook_id=notebook_id, title='')
    # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=drop_all_paragraph_id)

    # restart_zep_interpreter(interpreter_id='')

    return redirect("http://localhost:8080/#/notebook/" + str(notebook_id) + "/paragraph/" + str(viz_paragraph_id) + "?asIframe")


def get_pie_chart_zep(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = Query.objects.get(pk=query_pk)
    raw_query = query.raw_query
    # print raw_query
    key_var = str(request.GET.get('key_var', ''))
    value_var = str(request.GET.get('value_var', ''))

    notebook_id = create_zep_note(name='bdo_test')
    query_paragraph_id = create_zep__query_paragraph(notebook_id, title='query_paragraph', raw_query=raw_query)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=query_paragraph_id)
    sort_paragraph_id = create_zep_sort_paragraph(notebook_id=notebook_id, title='sort_paragraph', sort_col=key_var)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=sort_paragraph_id)
    reg_table_paragraph_id = create_zep_reg_table_paragraph(notebook_id=notebook_id, title='sort_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=reg_table_paragraph_id)
    viz_paragraph_id = create_zep_viz_paragraph(notebook_id=notebook_id, title='viz_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=viz_paragraph_id)

    set_zep_paragraph_pie_chart(notebook_id=notebook_id, paragraph_id=viz_paragraph_id, query_doc=query.document, value_vars=value_var, key_var=key_var)
    # drop_all_paragraph_id = create_zep_drop_all_paragraph(notebook_id=notebook_id, title='')
    # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=drop_all_paragraph_id)

    # restart_zep_interpreter(interpreter_id='')

    return redirect("http://localhost:8080/#/notebook/"+str(notebook_id)+"/paragraph/"+str(viz_paragraph_id)+"?asIframe")

def test_request_zep(request):
    query = 6
    raw_query = Query.objects.get(pk=query).raw_query
    print raw_query

    notebook_id = create_zep_note(name='bdo_test')
    query_paragraph_id = create_zep__query_paragraph(notebook_id, title='query_paragraph', raw_query=raw_query)
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=query_paragraph_id)
    viz_paragraph_id = create_zep_viz_paragraph(notebook_id=notebook_id, title='viz_paragraph')
    run_zep_paragraph(notebook_id=notebook_id, paragraph_id=viz_paragraph_id)

    # response = requests.delete("http://localhost:8080/api/notebook/"+str(notebook_id))
    return render(request, 'visualizer/table_zep.html', {'notebook_id': notebook_id, 'paragraph_id': viz_paragraph_id})


def get_presto_cursor():
    presto_credentials = settings.DATABASES['UBITECH_PRESTO']
    conn = prestodb.dbapi.connect(
        host=presto_credentials['HOST'],
        port=presto_credentials['PORT'],
        user=presto_credentials['USER'],
        catalog=presto_credentials['CATALOG'],
        schema=presto_credentials['SCHEMA'],
    )
    cursor = conn.cursor()
    return cursor


def map_viz_folium_heatmap(request):
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 13
    min_zoom = 2

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   min_zoom=min_zoom,
                   max_bounds=True,
                   tiles=tiles_str + token_str,
                   attr=attr_str)

    np.random.seed(3141592)
    initial_data = (
        np.random.normal(size=(100, 2)) * np.array([[1, 1]]) +
        np.array([[48, 5]])
    )
    move_data = np.random.normal(size=(100, 2)) * 0.01
    data = [(initial_data + move_data * i).tolist() for i in range(100)]

    # hm = plugins.HeatMapWithTime(data)
    # hm.add_to(m)

    time_index = [
        (datetime.now() + k * timedelta(1)).strftime('%Y-%m-%d') for
        k in range(len(data))
    ]
    hm = plugins.HeatMapWithTime(
        data,
        index=time_index,
        radius=0.5,
        scale_radius=True,
        auto_play=True,
        max_opacity=0.3
    )

    hm.add_to(m)

    m.save('templates/map.html')
    map_html = open('templates/map.html', 'r').read()
    soup = BeautifulSoup(map_html, 'html.parser')
    map_id = soup.find("div", {"class": "folium-map"}).get('id')
    # print map_id
    js_all = soup.findAll('script')
    # print(js_all)
    if len(js_all) > 5:
        js_all = [js.prettify() for js in js_all[5:]]
    # print(js_all)
    css_all = soup.findAll('link')
    if len(css_all) > 3:
        css_all = [css.prettify() for css in css_all[3:]]
    # print js
    # os.remove('templates/map.html')
    return render(request, 'visualizer/map_viz_folium.html',
                  {'map_id': map_id, 'js_all': js_all, 'css_all': css_all})




        # def make_map(bbox):
#     fig, ax = plt.subplots(figsize=(8, 6))
#     # ax.set_extent(bbox)
#     ax.coastlines(resolution='50m')
#     return fig, ax