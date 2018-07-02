from __future__ import unicode_literals, division
# -*- coding: utf-8 -*-
import pdb
from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.db import connection, connections
from rest_framework.views import APIView
from forms import MapForm

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import namedtuple
import os, re, time
from nvd3 import pieChart, lineChart
import psycopg2

from matplotlib import use

from django.template.loader import render_to_string

from service_builder.models import ServiceInstance
from service_builder.views import updateServiceInstanceVisualizations

use('Agg')
from matplotlib.figure import Figure
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import pylab as pl


from query_designer.models import TempQuery
from visualizer.models import Visualization
from aggregator.models import *

from utils import *
from tests import *

from folium import CustomIcon
from folium.plugins import HeatMap, MarkerCluster

FOLIUM_COLORS = ['red', 'blue', 'gray', 'darkred', 'lightred', 'orange', 'beige', 'green', 'darkgreen', 'lightgreen', 'darkblue',
                 'lightblue', 'purple', 'darkpurple', 'pink', 'cadetblue', 'lightgray']



def map_visualizer(request):

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

    js_list = []
    old_map_id_list = []
    extra_js = ""
    layer_count = int(request.GET.get("layer_count", 0))

    for count in range(0, layer_count):
        layer_id = request.GET.get("viz_id"+str(count))
        # Plotline
        if (layer_id == str(18)):
            print ('Plotline')
            cached_file = str(request.GET.get('cached_file_id' + str(count), ''))
            marker_limit = request.GET.get("m_limit"+str(count),200)
            print marker_limit
            query = int(str(request.GET.get('query'+str(count), '0')))
            df = str(request.GET.get('df'+str(count), ''))
            print df
            notebook_id = str(request.GET.get('notebook_id'+str(count), ''))
            color = str(request.GET.get('color'+str(count), 'blue'))
            print color
            order_var = str(request.GET.get('order_var'+str(count), ''))
            print order_var
            ship_id = str(request.GET.get('ship_id'+str(count), ''))
            lat_col = str(request.GET.get('lat_col'+str(count), 'latitude'))
            print lat_col
            lon_col = str(request.GET.get('lon_col'+str(count), 'longitude'))
            print lon_col
            # map_id = str(request.GET.get('map_id'+str(count), ''))
            m, extra_js = map_plotline(marker_limit, query, df, notebook_id, color, order_var, ship_id, lat_col, lon_col, m, request, cached_file)
        # Contours
        elif (layer_id == str(4)):
            print ('Contours')
            # Gather the arguments
            cached_file = str(request.GET.get('cached_file_id'+str(count), ''))
            n_contours = int(request.GET.get('n_contours'+str(count), 20))
            step = float(request.GET.get('step'+str(count), 0.1))
            variable = str(request.GET.get('feat_1'+str(count), ''))
            query = str(request.GET.get('query'+str(count), ''))
            agg_function = str(request.GET.get('agg_func'+str(count), 'avg'))
            m, extra_js, old_map_id = map_viz_folium_contour(n_contours, step, variable, query, agg_function, m, cached_file)
            old_map_id_list.append(old_map_id)
        # Map Course
        elif (layer_id == str(15)):
            print ('Markers')
            cached_file = str(request.GET.get('cached_file_id' + str(count), ''))
            marker_limit = int(request.GET.get('m_limit'+str(count), '100'))
            print marker_limit
            query = int(str(request.GET.get('query'+str(count), '0')))

            df = str(request.GET.get('df'+str(count), ''))
            print df
            notebook_id = str(request.GET.get('notebook_id'+str(count), ''))

            order_var = str(request.GET.get('order_var'+str(count), ''))
            print order_var
            variable = str(request.GET.get('col_var'+str(count), ''))
            print variable
            agg_function = str(request.GET.get('agg_func'+str(count), 'avg'))

            lat_col = str(request.GET.get('lat_col'+str(count), 'latitude'))
            print lat_col
            lon_col = str(request.GET.get('lon_col'+str(count), 'longitude'))
            print lon_col

            color_col = str(request.GET.get('color_col'+str(count), ''))
            m, extra_js = map_course(marker_limit, query, df, notebook_id, order_var, variable, agg_function, lat_col, lon_col,color_col, m, request, cached_file)
        # Heatmap
        elif (layer_id == str(19)):
            print ('Heatmap')
            cached_file = str(request.GET.get('cached_file_id' + str(count), ''))
            query = int(str(request.GET.get('query'+str(count), '0')))
            df = str(request.GET.get('df'+str(count), ''))
            print df
            notebook_id = str(request.GET.get('notebook_id'+str(count), ''))

            heat_col = str(request.GET.get('heat_col'+str(count), 'frequency'))
            print heat_col
            lat_col = str(request.GET.get('lat_col'+str(count), 'latitude'))
            print lat_col
            lon_col = str(request.GET.get('lon_col'+str(count), 'longitude'))
            print lon_col
            m, extra_js = map_heatmap(query, df, notebook_id, lat_col, lon_col,heat_col, m, cached_file)

        if (extra_js!=""):
            js_list.append(extra_js)


    folium.LayerControl().add_to(m)
    m.save('templates/map1.html')
    map_html = open('templates/map1.html', 'r').read()
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
    html1 = render_to_string('visualizer/map_wjs.html',
                             {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'data': ''})
    # print(html1)
    return HttpResponse(html1)



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
                   tiles=tiles_str+token_str,
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
    return render(request, 'visualizer/map_viz_folium.html', {'map_id': map_id, 'js_all': js_all, 'css_all': css_all})



def map_course_time(request):
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

    if request.method == "GET":
        markersum = int(request.GET.get("markers", 50))
        ship = request.GET.get("ship", "all")
        mindate = str(request.GET.get("min_date", '2000-01-01 00:00:00'))
        maxdate = str(request.GET.get("max_date", '2017-12-31 23:59:59'))

        query_pk = int(str(request.GET.get('query', '')))


    data = get_data(query_pk, markersum, ship, mindate, maxdate)

    var_index = data['var']
    ship_index = data['ship']
    time_index = data['time']
    lat_index = data['lat']
    lon_index = data['lon']
    data = data['data']

    course = []
    times = []
    dates = []
    speeds = []
    colours = []
    currboat = int(data[0][ship_index])
    datas = []

    for index in range(0, len(data) - 1):
        d = data[index]

        lat = float(d[lat_index])
        lon = float(d[lon_index])
        date = str(d[time_index])
        cship = int(d[ship_index])
        speed = float(d[var_index])
        colour = 'blue'
        if speed > 75.0:
            colour = 'red'

        if cship != currboat:
            geo = createjson(course, times, dates, currboat, speeds, colours)
            datas.append(geo)
            currboat = cship
            colours = []
            course = []
            times = []
            dates = []
            speeds = []

        colours.append(colour)
        course.append([lon, lat])
        times.append(transpose(date))
        dates.append(date)
        speeds.append(speed)

    geo = createjson(course, times, dates, currboat, speeds, colours)
    datas.append(geo)
    datas = json.dumps(datas)

    #import pdb;pdb.set_trace()

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
    return render(request, 'visualizer/map_time.html',
                  {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'data': datas})


def map_course(marker_limit, query, df, notebook_id, order_var, variable, agg_function, lat_col, lon_col, color_col, m, request,cached_file):
    dic = {}
    if not os.path.isfile('visualizer/static/visualizer/temp/' + cached_file):
        if query != 0:
            q = AbstractQuery.objects.get(pk=int(query))
            q = TempQuery(document=q.document)
            doc = q.document

            doc['orderings'] = doc['orderings'].append({'name': order_var, 'type': 'ASC'})
            if marker_limit > 0:
                doc['limit'] = marker_limit

            for f in doc['from']:
                for s in f['select']:
                    if s['name'] == variable:
                        s['exclude'] = False
                    elif str(s['name']) == order_var:
                        s['exclude'] = False
                    elif str(s['name']) == color_col:
                        s['exclude'] = False
                    elif str(s['name']).find(lat_col) >= 0:
                        s['exclude'] = False
                    elif str(s['name']).find(lon_col) >= 0:
                        s['exclude'] = False
                    else:
                        s['exclude'] = True

            q.document = doc
            query_data = q.execute()
            data = query_data[0]['results']
            result_headers = query_data[0]['headers']


            print result_headers
            lat_index = lon_index = order_var_index = var_index = color_index = -1
            for idx, caa in enumerate(result_headers['columns']):
                if caa['name'] == variable:
                    var_index = idx
                elif str(caa['name']) == order_var:
                    order_var_index = idx
                elif str(caa['name']).find(lat_col) >= 0:
                    lat_index = idx
                elif str(caa['name']).find(lon_col) >= 0:
                    lon_index = idx
                elif str(caa['name']) == color_col:
                    color_index = idx

            list_data = []
            for d in data:
                item = [float(d[lat_index]), float(d[lon_index]), d[var_index]]
                list_data.append(item)
            print list_data
            data = list_data
            lat_index = 0
            lon_index = 1
            var_index = 2
        else:
            print ("json-case")
            service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')[0] #GET LAST
            livy = service_exec.service.through_livy
            session_id = service_exec.livy_session
            exec_id = service_exec.id
            updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
            if order_var != "":
                if not livy:
                    toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df)
                else:
                    json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df)

            else:
                if not livy:
                    toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=order_var)
                else:
                    json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df, order_by=order_var)

            if not livy:
                run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
                json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
                delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
                # print json_data

            data = []
            lat_index = 0
            lon_index = 1
            order_var_index = 2
            var_index = 3
            color_index = 4
            for s in json_data:
                row = [float(s[lat_col]), float(s[lon_col])]
                if order_var != '':
                    row.append(str(s[order_var]))
                else:
                    row.append('')
                if variable != '':
                    row.append(str(s[variable]))
                else:
                    row.append('')
                if color_col != '':
                    row.append(s[color_col])
                else:
                    row.append('')
                data.append(row)

            print data[:4]

        dic['data'] = data
        dic['color_index'] = color_index
        dic['lat_index'] = lat_index
        dic['lon_index'] = lon_index
        dic['var_index'] = var_index

        with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
            json.dump(dic, f)

    else:

        print "MARKERS DATA IS CACHED"
        with open('visualizer/static/visualizer/temp/' + cached_file) as f:
            cached_data = json.load(f)
        data = cached_data['data']
        color_index = cached_data['color_index']
        lat_index = cached_data['lat_index']
        lon_index = cached_data['lon_index']
        var_index = cached_data['var_index']
        # data_grid = [[j.encode('ascii') for j in i] for i in data_grid]

    pol_group_layer = folium.map.FeatureGroup(name='Markers - Layer: ' + str(variable)+' / Query ID: ' + str(query), overlay=True,
                                              control=True).add_to(m)

    color_dict = dict()
    color_cnt = 0

    print "Map course top 10 points"
    print data[:10]

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
                    color_dict[d[color_index]] = FOLIUM_COLORS[len(FOLIUM_COLORS)-1]
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

        folium.Marker(
            location=[d[lat_index],d[lon_index]],
            popup=str(variable)+": "+str(d[var_index])+"<br>Latitude: "+str(d[lat_index])+"<br>Longitude: "+str(d[lon_index]),
            icon=folium.Icon(color=marker_color),
            # radius=2,

        ).add_to(pol_group_layer)

    max_lat = float(max_lat)
    min_lat = float(min_lat)
    max_lon = float(max_lon)
    min_lon = float(min_lon)

    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
    ret_html = ""
    return m, ret_html



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


def map_plotline(marker_limit, query, df, notebook_id, color, order_var, ship_id, lat_col, lon_col, m, request, cached_file):

    # import pdb
    # pdb.set_trace()
    dict = {}
    if not os.path.isfile('visualizer/static/visualizer/temp/' + cached_file):

        if query != 0:
            q = AbstractQuery.objects.get(pk=int(query))
            q = TempQuery(document=q.document)
            doc = q.document

            doc['orderings'] = [{'name': order_var, 'type': 'ASC'}]

            # if doc['limit'] > marker_limit:
            doc['limit'] = marker_limit
            # print(doc)

            for f in doc['from']:
                for s in f['select']:
                    if s['name'] == order_var:
                        s['exclude'] = False
                    elif str(s['name']).find('latitude') >= 0:
                        s['exclude'] = False
                    elif str(s['name']).find('longitude') >= 0:
                        s['exclude'] = False
                    else:
                        s['exclude'] = True

            q.document = doc

            query_data = q.execute()
            data = query_data[0]['results']
            result_headers = query_data[0]['headers']

            lat_index = lon_index = -1
            order_var_index = -1
            var_index = -1
            for idx, c in enumerate(result_headers['columns']):
                if c['name'] == order_var:
                    order_var_index = idx
                elif str(c['name']).find('latitude') >= 0:
                    lat_index = idx
                elif str(c['name']).find('longitude') >= 0:
                    lon_index = idx

            # points = [[float(s[lat_index]), float(s[lon_index])] for s in data]
            points=[]
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
            print(points[:5])

        else:
            print ("json-case")

            livy = False
            service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')
            if len(service_exec) > 0:
                service_exec = service_exec[0]  # GET LAST
                session_id = service_exec.livy_session
                exec_id = service_exec.id
                updateServiceInstanceVisualizations(exec_id, request.build_absolute_uri())
                livy = service_exec.service.through_livy
            if livy:
                json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df, order_by=order_var, order_type='ASC')
            else:
                toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=order_var, order_type='ASC')
                run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
                json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
                delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            # print json_data

            # points = [[float(s[lat_col]), float(s[lon_col])] for s in json_data]

            points = []
            min_lat = 90
            max_lat = -90
            min_lon = 180
            max_lon = -180

            for s in json_data:
                points.append([float(s[lat_col]), float(s[lon_col])])
                if s[lat_col] > max_lat:
                    max_lat = s[lat_col]
                if s[lat_col] < min_lat:
                    min_lat = s[lat_col]
                if s[lon_col] > max_lon:
                    max_lon = s[lon_col]
                if s[lon_col] < min_lon:
                    min_lon = s[lon_col]

            max_lat = float(max_lat)
            min_lat = float(min_lat)
            max_lon = float(max_lon)
            min_lon = float(min_lon)
            print(points[:5])

        dict['min_lat'] = min_lat
        dict['max_lat'] = max_lat
        dict['min_lon'] = min_lon
        dict['max_lon'] = max_lon

        dict['points'] = points
        # print dict

        with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
            json.dump(dict, f)


    else:
        print('PLOTLINE DATA IS CACHED!!!')
        with open('visualizer/static/visualizer/temp/' + cached_file) as f:
            cached_data = json.load(f)
        min_lat = cached_data['min_lat']
        max_lat = cached_data['max_lat']
        min_lon = cached_data['min_lon']
        max_lon = cached_data['max_lon']

        points = cached_data['points']
        # data_grid = [[j.encode('ascii') for j in i] for i in data_grid]


    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])

    pol_group_layer = folium.map.FeatureGroup(name='Plotline - Layer / Ship ID: ' + str(ship_id)+' / Query ID: '+str(query), overlay=True,
                                              control=True).add_to(m)
    folium.PolyLine(points,
                    color=color,
                    weight=3,
                    opacity=0.9,
                    ).add_to(pol_group_layer)

    # Arrows are created
    for i in range (1,len(points)):
        arrows = get_arrows(m, 1, locations=[points[i-1], points[i]])
        for arrow in arrows:
            arrow.add_to(pol_group_layer)


    ret_html = ""
    return m, ret_html



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
                elif str(s['name']).find('latitude') >= 0:
                    s['exclude'] = False
                elif str(s['name']).find('longitude') >= 0:
                    s['exclude'] = False
                # elif s['name'] == var:
                #     s['exclude'] = False
                else:
                    s['exclude'] = True


        # print doc
        q.document = doc

        query_data = q.execute()
        data = query_data[0]['results']
        result_headers = query_data[0]['headers']
        print(result_headers)

        var_index = order_index = lon_index = lat_index = -1

        for idx, c in enumerate(result_headers['columns']):
            # if c['name'] == var:
            #     var_index = idx
            if str(c['name']).find('latitude') >= 0:
                lat_index = idx
            elif str(c['name']).find('longitude') >= 0:
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
        tdelta = datetime.strptime(data[1][order_var], FMT) - datetime.strptime(data[0][order_var], FMT)
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


# def map_heatmap(request):
#     tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
#     token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
#     attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
#                '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
#                'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
#     location = [0, 0]
#     zoom_start = 2
#     max_zoom = 15
#     min_zoom = 2
#
#     m = folium.Map(location=location,
#                    zoom_start=zoom_start,
#                    max_zoom=max_zoom,
#                    min_zoom=min_zoom,
#                    max_bounds=True,
#                    tiles=tiles_str + token_str,
#                    attr=attr_str)
#
#     if request.method == "POST":
#
#         form = MapForm(request.POST)
#         if form.is_valid():
#             data = request.data
#             markersum = data["markers"]
#             ship = data["ship"]
#             mindate = request.POST.get("min_date", 2000)
#             maxdate = request.POST.get("max_date", 2017)
#         else:
#             markersum = 50
#             ship = "all"
#             mindate = 2000
#             maxdate = 2017
#
#     else:
#         markersum = int(request.GET.get("markers", 5000))
#         ship = request.GET.get("ship", "all")
#         mindate = int(request.POST.get("min_date", 2000))
#         maxdate = int(request.POST.get("max_date", 2017))
#
#     query_pk = int(str(request.GET.get('query', '')))
#     data = get_data(query_pk, markersum, ship, mindate, maxdate)
#     heat = []
#
#     lat_index = data['lat']
#     lon_index = data['lon']
#     data = data['data']
#
#     for d in data:
#         heat.append((np.array([float(d[lat_index]), float(d[lon_index])]) * np.array([1, 1])).tolist())
#
#     HeatMap(heat, name="Heat Map").add_to(m)
#
#
#     folium.LayerControl().add_to(m)
#
#
#     m.save('templates/map.html')
#     map_html = open('templates/map.html', 'r').read()
#     soup = BeautifulSoup(map_html, 'html.parser')
#     map_id = soup.find("div", {"class": "folium-map"}).get('id')
#     # print map_id
#     js_all = soup.findAll('script')
#     # print(js_all)
#     if len(js_all) > 5:
#         js_all = [js.prettify() for js in js_all[5:]]
#     # print(js_all)
#     css_all = soup.findAll('link')
#     if len(css_all) > 3:
#         css_all = [css.prettify() for css in css_all[3:]]
#     # print js
#     # os.remove('templates/map.html')
#     return render(request, 'visualizer/map_viz_folium.html', {'map_id': map_id, 'js_all': js_all, 'css_all': css_all})



def map_heatmap(query, df, notebook_id, lat_col, lon_col,heat_col, m, cached_file):
    dict = {}

    if not os.path.isfile('visualizer/static/visualizer/temp/' + cached_file):
        if query != 0:
            q = AbstractQuery.objects.get(pk=int(query))
            q = TempQuery(document=q.document)
            doc = q.document

            doc['orderings'] = []
            doc['limit'] = []


            for f in doc['from']:
                for s in f['select']:
                    if str(s['name']).find('latitude') >= 0:
                        s['exclude'] = False
                    elif str(s['name']).find('longitude') >= 0:
                        s['exclude'] = False
                    elif s['name'] == heat_col:
                        s['exclude'] = False
                    else:
                        s['exclude'] = True

            q.document = doc

            lat_index = lon_index = var_index = -1
            result = q.execute()[0]
            result_data = result['results']
            result_headers = result['headers']

            print result_headers
            for idx, c in enumerate(result_headers['columns']):
                if str(c['name']).find('lat') >= 0:
                    lat_index = idx
                elif str(c['name']).find('lon') >= 0:
                    lon_index = idx
                elif c['name'] == heat_col:
                    var_index = idx

            data = result_data
        else:
            print ("json-case")
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df)
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            # print json_data

            data = []
            lat_index = 0
            lon_index = 1
            var_index = 2

            for s in json_data:
                row = [float(s[lat_col]), float(s[lon_col]), float(s[heat_col])]
                data.append(row)

        min_lat = 90
        max_lat = -90
        min_lon = 180
        max_lon = -180
        heat = []

        if (heat_col == 'frequency'):
            for d in data:
                heat.append((np.array([float(d[lat_index]), float(d[lon_index])]) * np.array([1, 1])).tolist())
                if d[lat_index] > max_lat:
                    max_lat = d[lat_index]
                if d[lat_index] < min_lat:
                    min_lat = d[lat_index]
                if d[lon_index] > max_lon:
                    max_lon = d[lon_index]
                if d[lon_index] < min_lon:
                    min_lon = d[lon_index]
        else:
            maximum = -1000000
            for d in data:
                if d[var_index] > maximum:
                    maximum = d[var_index]
            for d in data:
                heat.append((np.array([float(d[lat_index]), float(d[lon_index]),float(d[var_index])/maximum])).tolist())
                if d[lat_index] > max_lat:
                    max_lat = d[lat_index]
                if d[lat_index] < min_lat:
                    min_lat = d[lat_index]
                if d[lon_index] > max_lon:
                    max_lon = d[lon_index]
                if d[lon_index] < min_lon:
                    min_lon = d[lon_index]
        max_lat = float(max_lat)
        min_lat = float(min_lat)
        max_lon = float(max_lon)
        min_lon = float(min_lon)

        dict['min_lat'] = min_lat
        dict['max_lat'] = max_lat
        dict['min_lon'] = min_lon
        dict['max_lon'] = max_lon
        dict['heat'] = heat

        with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
            json.dump(dict, f)


    else:
        print ('HEATMAP DATA IS CACHED')
        with open('visualizer/static/visualizer/temp/' + cached_file) as f:
            cached_data = json.load(f)
        min_lat = cached_data['min_lat']
        max_lat = cached_data['max_lat']
        min_lon = cached_data['min_lon']
        max_lon = cached_data['max_lon']

        heat = cached_data['heat']
        # heat = [[j.encode('ascii') for j in i] for i in heat]

    # check out
    HeatMap(heat, name="Heat Map - Layer / Query ID: "+str(query)).add_to(m)


    m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])

    ret_html = ""
    return m , ret_html






def map_viz_folium_contour(n_contours, step, variable, query, agg_function, m, cached_file):
    try:
        print('ENTERING CONTOURS')

        # Gather the arguments
        round_num = 0

        if step == 1:
            round_num = 0
        elif step == 0.1:
            round_num = 1
        elif step == 0.01:
            round_num = 2
        elif step == 0.001:
            round_num = 3

        dict = {}



        if not os.path.isfile('visualizer/static/visualizer/temp/'+cached_file):
            q = AbstractQuery.objects.get(pk=int(query))
            q = TempQuery(document=q.document)
            doc = q.document

            doc['orderings'] = []
            doc['limit'] = []
            var_query_id = variable[:variable.find('_')]

            # print doc
            for f in doc['from']:
                for s in f['select']:
                    if s['name'] == variable:
                        s['aggregate'] = agg_function
                        s['exclude'] = False
                    elif str(s['name']).find('latitude') >= 0 and str(s['name']).find(var_query_id) >= 0:
                        s['groupBy'] = True
                        s['aggregate'] = 'round' + str(round_num)
                        s['exclude'] = False
                        doc['orderings'].append({'name': str(s['name']), 'type': 'ASC'})
                    elif str(s['name']).find('longitude') >= 0 and str(s['name']).find(var_query_id) >= 0:
                        s['groupBy'] = True
                        s['aggregate'] = 'round' + str(round_num)
                        s['exclude'] = False
                        doc['orderings'].insert(0, {'name': str(s['name']), 'type': 'ASC'})
                    else:
                        s['exclude'] = True
                        s['groupBy'] = False


            var_index = lat_index = lon_index = -1
            result = q.execute()[0]
            result_data = result['results']
            result_headers = result['headers']

            # print result_headers
            for idx, c in enumerate(result_headers['columns']):
                if c['name'] == variable:
                    var_index = idx
                elif str(c['name']).find('lat') >= 0:
                    lat_index = idx
                elif str(c['name']).find('lon') >= 0:
                    lon_index = idx

            data = result_data

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
                if row[var_index] < min_val:
                    min_val = row[var_index]

            max_lat = float(max_lat)
            min_lat = float(min_lat)
            max_lon = float(max_lon)
            min_lon = float(min_lon)



            # print min_lat, max_lat, min_lon, max_lon, min_val, max_val

            lats_bins = np.arange(min_lat, max_lat + 0.00001, step)
            # print lats_bins[:3]
            lons_bins = np.arange(min_lon, max_lon + 0.00001, step)
            # print lons_bins[:3]
            Lats, Lons = np.meshgrid(lats_bins, lons_bins)

            # print Lats[:3]
            # print Lons[:3]

            # Create grid data needed for the contour plot
            # final_data = create_grid_data(lats_bins, lons_bins, data)

            final_data = []
            it = iter(data)
            try:
                val = map(float, next(it))
            except:
                val = [-300, -300, -300]

            for lon in lons_bins:
                row = list()
                for lat in lats_bins:
                    row.append(None)
                final_data.append(row)
            for d in data:
                lon_pos = int((d[lon_index] - min_lon)/step)
                lat_pos = int((d[lat_index] - min_lat) / step)
                final_data[lon_pos][lat_pos] = d[var_index]


            levels = np.linspace(start=min_val, stop=max_val, num=n_contours)
            print 'level ok'
            # Create contour image to lay over the map

            fig = Figure()
            ax = fig.add_subplot(111)
            plt.contourf(Lons, Lats, final_data, levels=levels, cmap=plt.cm.coolwarm)
            plt.axis('off')
            # print 'contour made'
            extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            plt.draw()
            # print 'contour draw'
            # plt.show()
            ts = str(time.time()).replace(".", "")
            mappath = 'visualizer/static/visualizer/img/temp/' + ts + 'map.png'
            # print 'mappath'
            plt.savefig(mappath, bbox_inches=extent, transparent=True, frameon=False, pad_inches=0)
            # print 'saved'
            plt.clf()
            plt.close()
            fig = None
            ax = None

            # Create legend for the contour map
            a = np.array([[min_val, max_val]])
            pl.figure(figsize=(2.8, 0.4))
            img = pl.imshow(a, cmap=plt.cm.coolwarm)
            pl.gca().set_visible(False)
            cax = pl.axes([0.1, 0.2, 0.8, 0.6])
            cbar = pl.colorbar(orientation="horizontal", cax=cax)
            cbar.ax.tick_params(labelsize=11, colors="#ffffff")
            ts = str(time.time()).replace(".", "")
            legpath = 'visualizer/static/visualizer/img/temp/' + ts + 'colorbar.png'
            pl.savefig(legpath, transparent=True, bbox_inches='tight')
            legpath = legpath.split("static/", 1)[1]
            pl.clf()
            pl.close()

            # Create data grid for javascript pop-up
            data_grid = []
            for nlist in final_data:
                nlist = map(str, nlist)
                data_grid.append(nlist)

            lats_bins_min = lats_bins.min()
            lons_bins_min = lons_bins.min()
            lats_bins_max = lats_bins.max()
            lons_bins_max = lons_bins.max()

            # pdb.set_trace()

            dict['min_lat'] = min_lat
            dict['max_lat'] = max_lat
            dict['min_lon'] = min_lon
            dict['max_lon'] = max_lon
            dict['lats_bins_min'] = lats_bins_min
            dict['lons_bins_min'] = lons_bins_min
            dict['lats_bins_max'] = lats_bins_max
            dict['lons_bins_max'] = lons_bins_max

            dict['image_path'] = mappath
            dict['leg_path'] = legpath
            dict['data_grid'] = data_grid
            # print dict

            with open('visualizer/static/visualizer/temp/' + cached_file, 'w') as f:
                json.dump(dict, f)

        else:
            # pdb.set_trace()
            print ('CONTOURS DATA IS CACHED!!!')
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

        # pdb.set_trace()
        m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
        # read in png file to numpy array
        data_img = Image.open(mappath)
        data = trim(data_img)
        data_img.close()

        # Overlay the image
        contour_layer = plugins.ImageOverlay(data, zindex=1, opacity=0.8, mercator_project=True,
                                                          bounds=[[lats_bins_min, lons_bins_min], [lats_bins_max, lons_bins_max]])
        contour_layer.layer_name = 'Contours On Map - Layer / Query Name: '+str(query)
        m.add_child(contour_layer)

        # Overlay an extra coastline field (to be removed
        folium.GeoJson(open('ne_50m_land.geojson').read(),
                       style_function=lambda feature: {'fillColor': '#002a70', 'color': 'black', 'weight': 3}) \
            .add_to(m) \
            .layer_name = 'Coastline - Layer'


        # Parse the HTML to pass to template through the render
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
        # os.remove(mappath)
        # os.remove('templates/map.html')


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

        return m, ret_html, map_id

    except HttpResponseNotFound:
        return HttpResponseNotFound
    except Exception:
        print Exception.message.capitalize()
        return HttpResponseNotFound


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
                elif str(s['name']).find('latitude') >= 0:
                    s['exclude'] = False
                elif str(s['name']).find('longitude') >= 0:
                    s['exclude'] = False
                elif s['name'] == heat_col:
                    s['exclude'] = False
                else:
                    s['exclude'] = True

        q.document = doc

        lat_index = lon_index = var_index = 0
        result = q.execute()[0]
        result_data = result['results']
        result_headers = result['headers']

        print result_headers
        for idx, c in enumerate(result_headers['columns']):
            if str(c['name']).find('lat') >= 0:
                lat_index = idx
            elif str(c['name']).find('lon') >= 0:
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


    print data_list
    print time_list
    # initial_data = (
    #     np.random.normal(size=(100, 2)) * np.array([[1, 1]]) +
    #     np.array([[48, 5]])
    # )
    # move_data = np.random.normal(size=(100, 2)) * 0.01
    # data = [(initial_data + move_data * i).tolist() for i in range(100)]

    # hm = plugins.HeatMapWithTime(data)
    # hm.add_to(m)
    #
    # time_index = [
    #     (datetime.now() + k * timedelta(1)).strftime('%Y-%m-%d') for
    #     k in range(len(data))
    # ]
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
    # y_var = str(request.GET.get('y_var', ''))
    bins = int(str(request.GET.get('bins', '5')))
    agg_function = str(request.GET.get('agg_func', 'avg'))

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

        raw_query = "with drb_stats as (select min({0}) as min, max({0}) as max from {1} {3}), " \
                    "histogram as (select width_bucket({0}, min, max, {2}) as bucket, " \
                    "numrange (min({0}::NUMERIC), max({0}::NUMERIC), '[]') as range, " \
                    "count(*) as freq from {1}, drb_stats {3} " \
                    "group by bucket " \
                    "order by bucket) " \
                    "select range, freq " \
                    "from histogram; ".format(table_col, from_table, bins, where_clause)
        # print raw_query
        cursor.execute(raw_query)
        data = cursor.fetchall()
        json_data = []
        for d in data:
            json_data.append({"startValues": '['+str(float(d[0].lower)) + ',' + str(float(d[0].upper)) + ']', "counts": str(d[1])})
        y_var = 'counts'
        x_var = 'startValues'
        # print data
        json_data = convert_unicode_json(json_data)
        # print json_data
    else:
        bins += 1

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
            scala_histogram_paragraph_id = create_zep_scala_histogram_paragraph(notebook_id=notebook_id, title='', df_name=df, hist_col='power',num_of_bins=bins)
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=scala_histogram_paragraph_id, livy_session_id=session_id, mode='livy')
            json_data = create_livy_scala_toJSON_paragraph(session_id=session_id, df_name=df)

            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=tempView_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=scala_histogram_paragraph_id)
        else:
            tempView_paragraph_id = create_zep_tempView_paragraph(notebook_id=notebook_id, title='', df_name=df)
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=tempView_paragraph_id, livy_session_id=0, mode='zeppelin')
            scala_histogram_paragraph_id = create_zep_scala_histogram_paragraph(notebook_id=notebook_id, title='', df_name=df, hist_col='power', num_of_bins=bins)
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
        # print json_data
        y_var = 'counts'
        x_var = 'startValues'

    return render(request, 'visualizer/histogram_simple_am.html', {'data': convert_unicode_json(json_data), 'value_col': y_var, 'category_col': x_var})


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
        # raw_query = query.raw_query
        # print doc
        # print raw_query


        query_data = query.execute()

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
    legpath = 'visualizer/static/visualizer/img/temp/' + ts + 'h2dcolorbar.png'
    pl.savefig(legpath, transparent=True, bbox_inches='tight')
    legpath = legpath.split("static/", 1)[1]
    pl.clf()
    pl.close()

    return render(request, 'visualizer/histogram_2d_am.html',
                  {'data': json_data, 'value_col': y_var, 'category_col': x_var, 'bin_count': bins,
                   'bin_x': bin_x_contr, 'bin_y': bin_y_contr, 'legend_id': legpath})


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


def get_line_chart_am(request):
    query_pk = int(str(request.GET.get('query', '0')))

    df = str(request.GET.get('df', ''))
    notebook_id = str(request.GET.get('notebook_id', ''))

    x_var = str(request.GET.get('x_var', ''))
    y_var = request.GET.getlist('y_var[]')

    y_var_list = y_var
    agg_function = str(request.GET.get('agg_func', 'avg'))

    if query_pk != 0:
        query = AbstractQuery.objects.get(pk=query_pk)
        query = TempQuery(document=query.document)
        doc = query.document

        for f in doc['from']:
            for s in f['select']:
                if s['name'] in y_var_list:
                    s['aggregate'] = agg_function
                    s['exclude'] = False
                elif s['name'] == x_var:
                    s['groupBy'] = True
                    s['exclude'] = False
                else:
                    s['exclude'] = True
        doc['orderings'] = [{'name': x_var, 'type': 'ASC'}]
        query.document = doc
        # raw_query = query.raw_query
        # print doc


        query_data = query.execute()
        data = query_data[0]['results']
        result_headers = query_data[0]['headers']

        x_var_index = 0
        y_var_index = []
        y_var_indlist = []
        y_m_unit=[]
        y_title_list=[]
        for idx, c in enumerate(result_headers['columns']):
            if c['name'] in y_var_list:
                y_var_index.insert(len(y_var_index), idx)
                y_var_indlist.insert(len(y_var_indlist), c['name'])
                y_m_unit.insert(len(y_m_unit),c['unit'].encode('ascii'))
                y_title_list.insert(len(y_title_list),c['title'].encode('ascii'))
            elif c['name'] == x_var:
                x_var_index = idx
        # print y_m_unit
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
        print json_data[:3]

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
            json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df, order_by=x_var, order_type='ASC')
        else:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=x_var, order_type='ASC')
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
            json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        print json_data[:3]
        y_m_unit = []
        y_title_list = []
        for x in y_var_list:
            # TODO: use proper names
            y_title_list.insert(0, str(x))
            y_m_unit.insert(0, str('unknown unit'))

    #notebook_id = create_zep_note(name='bdo_test')
    # query_paragraph_id = create_zep__query_paragraph(notebook_id, title='query_paragraph', raw_query=raw_query)
    # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=query_paragraph_id)
    # # sort_paragraph_id = create_zep_sort_paragraph(notebook_id=notebook_id, title='sort_paragraph', sort_col=x_var)
    # # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=sort_paragraph_id)
    # # reg_table_paragraph_id = create_zep_reg_table_paragraph(notebook_id=notebook_id, title='sort_paragraph')
    # # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=reg_table_paragraph_id)
    # toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='toJSON_paragraph')
    # run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
    # json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
    # # json_data = '{ "data":' + json_data + '}'

    #session_id = create_livy_session(kind='pyspark')
    #query_statement_id = create_livy_query_statement(session_id=session_id, raw_query=raw_query)
    #json_data = create_livy_toJSON_paragraph(session_id=session_id)['text/plain']
    #print json_data

    #json_data = json_data.replace("u'{", "{")
    #json_data = json_data.replace("}'", "}")
    #json_data = json_data.replace("+03:00", "")
    #
    # print str(json_data)
    # print json.loads(str(json_data))
    #

    if 'time' in x_var:
        isDate = 'true'
    else:
        isDate = 'false'

    return render(request, 'visualizer/line_chart_am.html',
                  {'data': json_data, 'value_col': y_var_list, 'm_units':y_m_unit, 'title_col':y_title_list, 'category_col': x_var, 'isDate': isDate})


def get_pie_chart_am(request):
    query_pk = int(str(request.GET.get('query', '0')))

    df = str(request.GET.get('df', ''))
    notebook_id = str(request.GET.get('notebook_id', ''))

    key_var = str(request.GET.get('key_var', ''))
    value_var = str(request.GET.get('value_var', ''))
    agg_func = str(request.GET.get('agg_func', 'avg'))

    if query_pk != 0:
        query = AbstractQuery.objects.get(pk=query_pk)
        query = TempQuery(document=query.document)
        doc = query.document
        print doc
        for f in doc['from']:
            for s in f['select']:
                if s['name'] == value_var:
                    s['aggregate'] = agg_func
                    s['exclude'] = False
                elif s['name'] == key_var:
                    s['groupBy'] = True
                    s['exclude'] = False
                else:
                    s['exclude'] = True
        print doc

        doc['orderings'] = [{'name': key_var, 'type': 'ASC'}]
        query.document = doc
        # raw_query = query.raw_query
        # print doc


        query_data = query.execute()
        data = query_data[0]['results']
        result_headers = query_data[0]['headers']

        value_var_index = key_var_index = 0
        for idx, c in enumerate(result_headers['columns']):
            if c['name'] == value_var:
                value_var_index = idx
            elif c['name'] == key_var:
                key_var_index = idx

        json_data = []
        for d in data:
            json_data.append({value_var: d[0], key_var: str(d[1])})

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
            json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df, order_by=key_var, order_type='ASC')
        else:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=key_var, order_type='ASC')
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
            json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        print json_data

    return render(request, 'visualizer/pie_chart_am.html', {'data': json_data, 'value_var': value_var, 'key_var': key_var})


def get_column_chart_am(request):
    query_pk = int(str(request.GET.get('query', '0')))

    df = str(request.GET.get('df', ''))
    notebook_id = str(request.GET.get('notebook_id', ''))


    x_var = str(request.GET.get('x_var', ''))
    y_var = request.GET.getlist('y_var[]')
    y_var_list = y_var
    agg_function = str(request.GET.get('agg_func', 'avg'))

    if query_pk != 0:
        query = AbstractQuery.objects.get(pk=query_pk)
        query = TempQuery(document=query.document)

        doc = query.document
        print doc
        for f in doc['from']:
            for s in f['select']:
                if s['name'] in y_var_list:
                    s['aggregate'] = agg_function
                    s['exclude'] = False
                elif s['name'] == x_var:
                    s['groupBy'] = True
                    s['exclude'] = False
                else:
                    s['exclude'] = True
        print doc

        doc['orderings'] = [{'name': x_var, 'type': 'ASC'}]
        query.document = doc
        # raw_query = query.raw_query
        # print doc


        query_data = query.execute()
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
        print (json_data)
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
            json_data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df, order_by=x_var, order_type='ASC')
        else:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=x_var, order_type='ASC')
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
            json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        print json_data
        y_m_unit = []
        y_title_list = []
        for x in y_var_list:
            # TODO: use proper names
            y_title_list.insert(0, str(x))
            y_m_unit.insert(0, str('unknown unit'))


    if 'time' in x_var:
        isDate = 'true'
    else:
        isDate = 'false'
    return render(request, 'visualizer/column_chart_am.html',
                  {'data': json_data, 'value_col': y_var_list, 'm_units':y_m_unit, 'title_col':y_title_list, 'category_col': x_var, 'isDate': isDate})


def get_data_table(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    limit = 50

    query_pk = int(str(request.GET.get('query', '0')))
    page = int(request.GET.get('page', 1))

    df = str(request.GET.get('df', ''))
    notebook_id = str(request.GET.get('notebook_id', ''))

    if query_pk != 0:
        query = AbstractQuery.objects.get(pk=query_pk)

        q = TempQuery(document=query.document)
        # offset = page * limit
        # if query.document['limit'] > offset:
        #     query.document['offset'] = page * limit
        #
        # if query.document['limit'] > limit:
        #     query.document['limit'] = limit

        result = q.execute()[0]
        data = result['results']
        headers = result['headers']['columns']
        isJSON = False

    else:
        livy = False
        service_exec = ServiceInstance.objects.filter(notebook_id=notebook_id).order_by('-id')
        if len(service_exec) > 0:
            service_exec = service_exec[0] #GET LAST
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
        isJSON = True
        print 'table data:'
        print data[:3]

        headers = [key for key in data[0].keys()]

    paginator = Paginator(data, limit)  # Show 25 contacts per page

    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_data = paginator.page(paginator.num_pages)

    return render(request, 'visualizer/data_table.html', {'headers': headers, 'data': page_data, 'query_pk': int(query_pk), 'isJSON': isJSON, 'df': df, 'notebook_id': notebook_id})


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


def get_arrows(m, n_arrows, locations, color='#68A7EE', size=7):
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

    # creating point from our Point named tuple
    p1 = Point(locations[0][0], locations[0][1])
    p2 = Point(locations[1][0], locations[1][1])

    # getting the rotation needed for our marker.
    # Subtracting 90 to account for the marker's orientation
    # of due East(get_bearing returns North)
    rotation = get_bearing(p1, p2) - 90

    arrows = []

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

    # adjusting for compass bearing
    if bearing < 0:
        return bearing + 360
    return bearing


def get_aggregate_value(request):
    query_pk = int(str(request.GET.get('query', '0')))
    variable = str(request.GET.get('variable', ''))
    agg_function = str(request.GET.get('agg_function', ''))

    df = str(request.GET.get('df', ''))
    notebook_id = str(request.GET.get('notebook_id', ''))

    if query_pk != 0:
        query = AbstractQuery.objects.get(pk=query_pk)
        query = TempQuery(document=query.document)
        doc = query.document
        for f in doc['from']:
            for s in f['select']:
                if s['name'] == variable:
                    s['aggregate'] = agg_function
                    s['exclude'] = False
                else:
                    s['exclude'] = True
        query.document = doc

        query_data = query.execute()
        data = query_data[0]['results']
        result_headers = query_data[0]['headers']

        variable_index = 0
        for idx, c in enumerate(result_headers['columns']):
            if c['name'] == variable:
                variable_index = idx

        value = round(data[0][variable_index], 3)
        unit = result_headers['columns'][variable_index]['unit']

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
            data = create_livy_toJSON_paragraph(session_id=session_id, df_name=df)
        else:
            toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df)
            run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id, livy_session_id=0, mode='zeppelin')
            data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
            delete_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        print data[:3]
        value = data
        unit = '?'

        headers = [key for key in data[0].keys()]

    return render(request, 'visualizer/aggregate_value.html', {'value': value, 'unit': unit})


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


def test_request_include(request):
    return render(request, 'visualizer/test_request_include.html', {})


def test_request(request):
    return render(request, 'visualizer/test_request.html', {})


def get_map_simple(request):
    return render(request, 'visualizer/map_viz.html', {})


class MapIndex(APIView):
    def get(self, request):
        form = MapForm()
        return render(request, 'visualizer/map_index.html', {'form': form})

    def post(self, request):
        form = MapForm(request.POST)
        if form.is_valid():
            tiles = request.data["tiles"]
            if tiles == "marker clusters":
                return map_viz_folium(request)
            else:
                return map_heatmap(request)

class MapAPI(APIView):
    def get(self, request):

        tiles = request.GET.get("tiles", "marker clusters")
        if tiles == "marker clusters":
            return map_viz_folium(request)
        else:
            return map_heatmap(request)

def map_viz(request):
    return render(request, 'visualizer/map_viz.html', {})


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


def make_map(bbox):
    fig, ax = plt.subplots(figsize=(8, 6))
    # ax.set_extent(bbox)
    ax.coastlines(resolution='50m')
    return fig, ax