from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from __future__ import division

from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup

from datetime import datetime, timedelta
import os
from nvd3 import pieChart, lineChart
import psycopg2
import re

from django.db import connection

from matplotlib import use

from query_designer.models import TempQuery

use('Agg')

import pylab as pl
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from utils import *
from visualizer.models import Visualization
import time

from django.utils.safestring import SafeString


def test_request_include(request):
    return render(request, 'visualizer/test_request_include.html', {})


def test_request(request):
    return render(request, 'visualizer/test_request.html', {})


def get_map_simple(request):
    return render(request, 'visualizer/map_viz.html', {})

from folium import CustomIcon
from folium.plugins import HeatMap
from folium.plugins import MarkerCluster

from rest_framework.views import APIView


from tests import *
from forms import MapForm

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

def createjson(course,times,dates,ship,speeds,colours):
    geo = {
        "type": "Feature",
        "geometry": {
            "type": "MultiPoint",
            "coordinates": course,
        },
        "properties": {
            "time": times,
            "date": dates,
            "ship": ship,
            "speed": speeds,
            "colour": colours,
        }
    }
    return geo

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



def map_course(request):
    marker_limit = int(request.GET.get('m_limit', '100'))
    query = str(request.GET.get('query', ''))
    order_var = str(request.GET.get('order_var', ''))
    variable = str(request.GET.get('col_var', ''))
    agg_function = str(request.GET.get('agg_func', 'avg'))

    q = AbstractQuery.objects.get(pk=int(query))
    # q = Query(document=q.document)
    q = TempQuery(document=q.document)
    doc = q.document

    var_query_id = variable[:variable.find('_')]
    doc['orderings'] = [{'name': order_var, 'type': 'ASC'}]
    # doc['orderings']=[]
    doc['limit'] = marker_limit

    for f in doc['from']:
        for s in f['select']:
            if s['name'] == variable:
                s['aggregate'] = agg_function
                s['exclude'] = False
            elif s['name'] == order_var:
                s['groupBy'] = True
                s['exclude'] = False
            elif str(s['name']).find('lat') >= 0 and str(s['name']).find(var_query_id) >= 0:
                s['groupBy'] = True
                s['aggregate'] = 'round'
                s['exclude'] = False
                doc['orderings'].append({'name': str(s['name']), 'type': 'ASC'})
            elif str(s['name']).find('lon') >= 0 and str(s['name']).find(var_query_id) >= 0:
                s['groupBy'] = True
                s['aggregate'] = 'round'
                s['exclude'] = False
                doc['orderings'].insert(0, {'name': str(s['name']), 'type': 'ASC'})
            else:
                s['exclude'] = True

    q.document = doc
    # raw_query = q.raw_query
    #
    # names = re.findall(r"round\((.*?)\)", raw_query)
    # for name in names:
    #     raw_query = re.sub(r"round\((" + name + ")\)", "round(" + name + ", 1)", raw_query)


    query_data = q.execute()
    data = query_data[0]['results']
    result_headers = query_data[0]['headers']


    lat_index = lon_index = -1
    order_var_index = -1
    var_index = -1
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] == variable:
            var_index = idx
        elif c['name'] == order_var:
            order_var_index = idx
        elif str(c['name']).find('lat') >= 0:
            lat_index = idx
        elif str(c['name']).find('lon') >= 0:
            lon_index = idx

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
                   tiles=tiles_str + token_str,
                   attr=attr_str,
                   )

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True).add_to(m)

    marker_cluster = MarkerCluster(
        name="Markers: "+ str(variable),
        control=True
    ).add_to(m)


    for d in data:
        folium.Marker(
            location=[d[lat_index],d[lon_index]],
            popup="Value: "+str(d[var_index])+"<br>Time: "+str(d[order_var_index])+"<br>Latitude: "+str(d[lat_index])+"<br>Longitude: "+str(d[lon_index]),
            icon=folium.Icon(color='green', icon='remove-sign'),

        ).add_to(marker_cluster)


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
    return render(request, 'visualizer/map_wjs.html',
                  {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'data': ''})


def map_plotline(request):
    marker_limit = int(request.GET.get('m_limit', '100'))
    query = str(request.GET.get('query', ''))
    order_var = str(request.GET.get('order_var', ''))
    variable = str(request.GET.get('col_var', ''))
    agg_function = str(request.GET.get('agg_func', 'avg'))

    q = AbstractQuery.objects.get(pk=int(query))
    q = TempQuery(document=q.document)
    doc = q.document

    var_query_id = variable[:variable.find('_')]
    doc['orderings'] = [{'name': order_var, 'type': 'ASC'}]
    # doc['orderings']=[]
    doc['limit'] = marker_limit

    for f in doc['from']:
        for s in f['select']:
            if s['name'] == variable:
                s['aggregate'] = agg_function
                s['exclude'] = False
            elif s['name'] == order_var:
                s['groupBy'] = True
                s['exclude'] = False
            elif str(s['name']).find('lat') >= 0 and str(s['name']).find(var_query_id) >= 0:
                s['groupBy'] = True
                s['aggregate'] = 'round'
                s['exclude'] = False
                doc['orderings'].append({'name': str(s['name']), 'type': 'ASC'})
            elif str(s['name']).find('lon') >= 0 and str(s['name']).find(var_query_id) >= 0:
                s['groupBy'] = True
                s['aggregate'] = 'round'
                s['exclude'] = False
                doc['orderings'].insert(0, {'name': str(s['name']), 'type': 'ASC'})
            else:
                s['exclude'] = True

    q.document = doc
    # raw_query = q.raw_query
    #
    # names = re.findall(r"round\((.*?)\)", raw_query)
    # for name in names:
    #     raw_query = re.sub(r"round\((" + name + ")\)", "round(" + name + ", 1)", raw_query)

    query_data = q.execute()
    data = query_data[0]['results']
    result_headers = query_data[0]['headers']

    lat_index = lon_index = -1
    order_var_index = -1
    var_index = -1
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] == variable:
            var_index = idx
        elif c['name'] == order_var:
            order_var_index = idx
        elif str(c['name']).find('lat') >= 0:
            lat_index = idx
        elif str(c['name']).find('lon') >= 0:
            lon_index = idx

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
                   tiles=tiles_str + token_str,
                   attr=attr_str)

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True).add_to(m)

    points = []
    for d in data:
        points.append([float(d[lat_index]), float(d[lon_index])])

    pol_group_layer = folium.map.FeatureGroup(name='Plotline: ' + str(variable), overlay=True, show=True,
                                              control=True).add_to(m)
    folium.PolyLine(points,
                    color='green',
                    weight=3,
                    opacity=0.9,
                    ).add_to(pol_group_layer)

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
    return render(request, 'visualizer/map_plotline.html',
                  {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'data': ''})


def map_heatmap(request):
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 15
    min_zoom = 2

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   min_zoom=min_zoom,
                   max_bounds=True,
                   tiles=tiles_str + token_str,
                   attr=attr_str)

    if request.method == "POST":

        form = MapForm(request.POST)
        if form.is_valid():
            data = request.data
            markersum = data["markers"]
            ship = data["ship"]
            mindate = request.POST.get("min_date", 2000)
            maxdate = request.POST.get("max_date", 2017)
        else:
            markersum = 50
            ship = "all"
            mindate = 2000
            maxdate = 2017

    else:
        markersum = int(request.GET.get("markers", 5000))
        ship = request.GET.get("ship", "all")
        mindate = int(request.POST.get("min_date", 2000))
        maxdate = int(request.POST.get("max_date", 2017))

    query_pk = int(str(request.GET.get('query', '')))
    data = get_data(query_pk, markersum, ship, mindate, maxdate)
    heat = []

    lat_index = data['lat']
    lon_index = data['lon']
    data = data['data']

    for d in data:
        heat.append((np.array([float(d[lat_index]), float(d[lon_index])]) * np.array([1, 1])).tolist())

    HeatMap(heat, name="Heat Map").add_to(m)


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
    return render(request, 'visualizer/map_viz_folium.html', {'map_id': map_id, 'js_all': js_all, 'css_all': css_all})

def map_viz_folium_contour(request):
    try:
        # Gather the arguments
        n_contours = int(request.GET.get('n_contours', 20))
        step = float(request.GET.get('step', 0.1))
        variable = str(request.GET.get('feat_1', ''))
        query = str(request.GET.get('query', ''))
        agg_function = str(request.GET.get('agg_func', 'avg'))

        q = Query.objects.get(pk=int(query))
        q = Query(document=q.document)
        doc = q.document
        # if 'orderings' not in doc.keys():
        #     doc['orderings'] = []
        doc['orderings'] = []
        doc['limit'] = []
        var_query_id = variable[:variable.find('_')]

        # print doc
        for f in doc['from']:
            for s in f['select']:
                if s['name'] == variable:
                    s['aggregate'] = agg_function
                    s['exclude'] = False
                elif str(s['name']).find('lat') >= 0 and str(s['name']).find(var_query_id) >= 0:
                    s['groupBy'] = True
                    s['aggregate'] = 'round'
                    s['exclude'] = False
                    doc['orderings'].append({'name': str(s['name']), 'type': 'ASC'})
                elif str(s['name']).find('lon') >= 0 and str(s['name']).find(var_query_id) >= 0:
                    s['groupBy'] = True
                    s['aggregate'] = 'round'
                    s['exclude'] = False
                    doc['orderings'].insert(0, {'name': str(s['name']), 'type': 'ASC'})
                else:
                    s['exclude'] = True
                    s['groupBy'] = False

        # print doc
        q.document = doc
        raw_query = q.raw_query
        # select_clause = re.findall(r"SELECT.*?\nFROM", raw_query)[0]
        # names = re.findall(r"round\((.*?)\)", select_clause)
        names = re.findall(r"round\((.*?)\)", raw_query)
        for name in names:
            raw_query = re.sub(r"round\((" + name + ")\)", "round(" + name + ", 1)", raw_query)

        # Create a leaflet map using folium
        m = create_folium_map(location=[0, 0], zoom_start=3, max_zoom=10)

        # try:
        #     connection = psycopg2.connect("dbname='bdo_platform' user='postgres' host='localhost' password='sssshmmy'")
        # except:
        #     print "I am unable to connect to the database"
        cursor = connection.cursor()
        cursor.execute(raw_query)
        data = cursor.fetchall()
        # print ("Data:")
        # print data[:3]

        var_index = lat_index = lon_index = 0
        result_headers = q.execute(only_headers=True)[0]['headers']
        # print result_headers
        for idx, c in enumerate(result_headers['columns']):
            if c['name'] == variable:
                var_index = idx
            elif str(c['name']).find('lat') >= 0:
                lat_index = idx
            elif str(c['name']).find('lon') >= 0:
                lon_index = idx

        min_lat = float(min(data, key=lambda x: x[lat_index])[lat_index])
        max_lat = float(max(data, key=lambda x: x[lat_index])[lat_index])
        min_lon = float(min(data, key=lambda x: x[lon_index])[lon_index])
        max_lon = float(max(data, key=lambda x: x[lon_index])[lon_index])
        min_val = float(min(data, key=lambda x: x[var_index])[var_index])
        max_val = float(max(data, key=lambda x: x[var_index])[var_index])
        # print min_lat, max_lat, min_lon, max_lon, min_val, max_val

        lats_bins = np.arange(min_lat, max_lat + 0.00001, 0.1)
        # print lats_bins
        lons_bins = np.arange(min_lon, max_lon + 0.00001, 0.1)
        # print lons_bins
        Lats, Lons = np.meshgrid(lats_bins, lons_bins)
        # print Lats
        # print Lons

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
                if abs(lon - val[lon_index]) < 0.1 and abs(lat - val[lat_index]) < 0.1:
                    row.append(val[var_index])
                    try:
                        val = map(float, next(it))
                    except:
                        val = [-300, -300, -300]
                else:
                    row.append(None)
            final_data.append(row)

        # print final_data[:3]


        levels = np.linspace(start=min_val, stop=max_val, num=n_contours)
        print 'level ok'

        # Create contour image to lay over the map
        fig = Figure()
        ax = fig.add_subplot(111)
        plt.contourf(Lons, Lats, final_data, levels=levels, cmap=plt.cm.coolwarm)
        plt.axis('off')
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        plt.draw()
        ts = str(time.time()).replace(".", "")
        mappath = 'visualizer/static/visualizer/img/temp/' + ts + 'map.png'
        plt.savefig(mappath, bbox_inches=extent, transparent=True, pad_inches=0)
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

        # read in png file to numpy array
        data_img = Image.open(mappath)
        data = trim(data_img)
        data_img.close()

        # Overlay the image
        contour_layer = plugins.ImageOverlay(data, zindex=1, opacity=0.8, mercator_project=True,
                                                          bounds=[[lats_bins.min(), lons_bins.min()], [lats_bins.max(), lons_bins.max()]])
        contour_layer.layer_name = 'Contour'
        m.add_child(contour_layer)

        # Overlay an extra coastline field (to be removed
        folium.GeoJson(open('ne_50m_land.geojson').read(),
                       style_function=lambda feature: {'fillColor': '#002a70', 'color': 'black', 'weight': 3}) \
            .add_to(m) \
            .layer_name = 'Coastline'

        # Add layer contorl
        folium.LayerControl().add_to(m)

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
        os.remove(mappath)
        os.remove('templates/map.html')

        # Create data grid for javascript pop-up
        data_grid = []
        for nlist in final_data:
            nlist = map(str, nlist)
            data_grid.append(nlist)

        return render(request, 'visualizer/map_viz_folium.html',
                      {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'step': step, 'data_grid': data_grid, 'min_lat': min_lat,
                       'max_lat': max_lat, 'min_lon': min_lon, 'max_lon': max_lon, 'agg_function': agg_function, 'legend_id': legpath})
    except HttpResponseNotFound:
        return HttpResponseNotFound
    except Exception:
        return HttpResponseNotFound

def make_map(bbox):
    fig, ax = plt.subplots(figsize=(8, 6))
    # ax.set_extent(bbox)
    ax.coastlines(resolution='50m')
    return fig, ax

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


def get_histogram_chart_am(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))
    bins = int(str(request.GET.get('bins', '2')))
    agg_function = str(request.GET.get('agg_func', 'avg'))

    doc = query.document

    for f in doc['from']:
        for s in f['select']:
            if s['name'] == y_var:
                s['exclude'] = False
            elif s['name'] == x_var:
                s['exclude'] = False
                s['groupBy'] = True
            else:
                s['exclude'] = True
    print doc
    doc['limit'] = []
    doc['orderings'] = [{'name': x_var, 'type': 'ASC'}]
    query.document = doc
    # raw_query = query.raw_query
    # print doc


    query_data = query.execute()
    data = query_data[0]['results']
    result_headers = query_data[0]['headers']


    x_var_index = -1
    y_var_index=-1
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] == y_var:
            y_var_index=idx
        elif c['name'] == x_var:
            x_var_index = idx

    min_x_var = float(min(data, key=lambda x: x[x_var_index])[x_var_index])
    max_x_var= float(max(data, key=lambda x: x[x_var_index])[x_var_index])

    # min_y_var = float(min(result_data, key=lambda x: x[y_var_index])[y_var_index])
    # max_y_var = float(max(result_data, key=lambda x: x[y_var_index])[y_var_index])
    # print min_y_var
    # print max_y_var
    # print max_x_var

    mybin = np.linspace(start=min_x_var, stop=max_x_var, num=bins+1)
    mybin[len(mybin)-1]=mybin[len(mybin)-1]+0.0001
    # print mybin

    bin_container = []
    iter2=iter(mybin)
    iter2.next()
    for el in mybin:
        try:
            temp = [el,iter2.next()]
        except:
            break
        bin_container.append(temp)

    final_data=agg_func_selector(agg_function, data, bin_container, y_var_index, x_var_index)

    # Create data for graph
    bin_list = [[round(s, 4) for s in xs] for xs in bin_container]

    json_data=[]
    count = 0
    for fd in final_data:
        dict = {}
        newvar = str(y_var).encode('ascii')
        dict.update({newvar : str(fd).encode('ascii')})
        dict.update({x_var : str(bin_list[count])})
        json_data.append(dict)
        count = count + 1
    # print (json_data)

    return render(request, 'visualizer/histogram_simple_am.html', {'data': json_data, 'value_col': y_var, 'category_col': x_var})


def get_histogram_2d_am(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))
    bins = int(str(request.GET.get('bins', '3')))

    # agg_function = str(request.GET.get('agg_func', 'avg'))

    doc = query.document

    for f in doc['from']:
        for s in f['select']:
            if s['name'] == y_var:
                s['groupBy'] = False
                s['aggregate'] = ''
                s['exclude'] = False
            elif s['name'] == x_var:
                s['groupBy'] = False
                s['exclude'] = False
                s['aggregate'] = ''
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
    y_var = str(request.GET.get('y_var', ''))
    y_var_list = y_var.split(",")
    agg_function = str(request.GET.get('agg_func', 'avg'))

    if query_pk != 0:
        query = AbstractQuery.objects.get(pk=query_pk)
        query = Query(document=query.document)
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
        for idx, c in enumerate(result_headers['columns']):
            if c['name'] in y_var_list:
                y_var_index.insert(len(y_var_index), idx)
                y_var_indlist.insert(len(y_var_indlist), c['name'])
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
        toJSON_paragraph_id = create_zep_toJSON_paragraph(notebook_id=notebook_id, title='', df_name=df, order_by=x_var, order_type='ASC')
        run_zep_paragraph(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        json_data = get_zep_toJSON_paragraph_response(notebook_id=notebook_id, paragraph_id=toJSON_paragraph_id)
        print json_data


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
    #print str(json_data)
    # print json.loads(str(json_data))
    #

    if 'time' in x_var:
        isDate = 'true'
    else:
        isDate = 'false'

    return render(request, 'visualizer/line_chart_am.html',
                  {'data': json_data, 'value_col': y_var_list, 'category_col': x_var, 'isDate': isDate})

def get_pie_chart_am(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    key_var = str(request.GET.get('key_var', ''))
    value_var = str(request.GET.get('value_var', ''))
    agg_func = str(request.GET.get('agg_func', 'avg'))

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

    return render(request, 'visualizer/pie_chart_am.html', {'data': json_data, 'value_var': value_var, 'key_var': key_var})


def get_column_chart_am(request):
    query_pk = int(str(request.GET.get('query', '0')))
    query = AbstractQuery.objects.get(pk=query_pk)
    query = TempQuery(document=query.document)
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))

    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))
    y_var_list = y_var.split(",")
    agg_function = str(request.GET.get('agg_func', 'avg'))

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
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] in y_var_list:
            y_var_index.insert(len(y_var_index), idx)
            y_var_indlist.insert(len(y_var_indlist), c['name'])
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

    if 'time' in x_var:
        isDate = 'true'
    else:
        isDate = 'false'
    return render(request, 'visualizer/column_chart_am.html',
                  {'data': json_data, 'value_col': y_var_list, 'category_col': x_var, 'isDate': isDate})

def get_data_table(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = AbstractQuery.objects.get(pk=query_pk)

    result_data = query.execute()['results']

    # json_data = []
    # for d in result_data:
    #     json_data.append({y_var: d[y_var_index], x_var: str(d[x_var_index])})

    return render(request, 'visualizer/data_table.html', {'data': result_data})


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

