from __future__ import unicode_literals
# -*- coding: utf-8 -*-
# import matplotlib
import requests
from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup

from datetime import datetime, timedelta
import time
import os
from nvd3 import pieChart, lineChart
import psycopg2
import re

import matplotlib.pyplot as plt

from django.db import connection

from matplotlib.figure import Figure
from matplotlib import use
from PIL import Image, ImageChops
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
            line = request.POST.get("line", False)
            markersum = data["markers"]
            ship = data["ship"]
            minyear = request.POST.get("min_year", 2000)
            maxyear = request.POST.get("max_year", 2017)
        else:
            markersum = 50
            line = False
            ship = "all"
            minyear = 2000
            maxyear = 2017

    else:
        line = request.GET.get("line", 'no')
        markersum = int(request.GET.get("markers", 50))
        ship = request.GET.get("ship", "all")
        minyear = int(request.POST.get("min_year", 2000))
        maxyear = int(request.POST.get("max_year", 2017))

    data = get_data(markersum, ship, minyear, maxyear)


    for index in range(0, len(data)):
        d = data[index]
        lat = d[0]
        lon = d[1]
        id = d[2]
        date = d[3]
        #import pdb;pdb.set_trace()

        url = 'https://cdn4.iconfinder.com/data/icons/geo-points-1/154/{}'.format
        icon_image = url('geo-location-gps-sea-location-boat-ship-512.png')
        icon = CustomIcon(
            icon_image,
            icon_size=(40, 40),
            icon_anchor=(20, 20),
        )
        message = '<b>Ship</b>: ' + id.__str__() + "<br><b>At :</b> [" + lat.__str__() + " , " + lon.__str__() + "] <br><b>On :</b> " + date
        folium.Marker(
            location=[lat, lon],
            icon=icon,
            popup=message
        ).add_to(marker_cluster)

    if line != 'no':

        course = []
        currboat = data[0][2]
        for index in range(0, len(data)-1):
            d = data[index]
            if d[2] != currboat:
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
                course = []
                currboat = d[2]
            else:
                course.append((np.array([float(d[0]), float(d[1])]) * np.array([1, 1])).tolist())

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
        minyear = int(request.POST.get("min_year", 2000))
        maxyear = int(request.POST.get("max_year", 2017))

    data = get_data(markersum, ship, minyear, maxyear)

    course = []
    times = []
    dates = []
    speeds = []
    colours = []
    currboat = data[0][2]
    datas = []

    for index in range(0, len(data) - 1):
        d = data[index]

        if valid_entry(d, ship, minyear, maxyear):
            lat = d[0]
            lon = d[1]
            date = d[3]
            cship = d[2]
            speed = d[4]
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

    if request.method == "GET":
        markersum = int(request.GET.get("markers", 500))
        ship = request.GET.get("ship", "all")
        minyear = int(request.POST.get("min_year", 2000))
        maxyear = int(request.POST.get("max_year", 2017))

    #import pdb;pdb.set_trace()

    data = get_data(markersum, ship, minyear, maxyear)

    jsonobj = []
    currboat = data[0][2]
    for index in range(0, len(data)-1):
        d = data[index]

        if valid_entry(d, currboat, minyear, maxyear):
            lat = d[0]
            lon = d[1]
            date = d[3]
            ship = d[2]
            speed = d[4]
            colour = 'blue'
            if speed > 75.0:
                colour = 'red'
            jsonobj.append({'ship': ship, 'lat': lat, 'lon': lon, 'date': date, 'colour': colour, 'speed': speed})
    jsonobj = json.dumps(jsonobj)


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
    return render(request, 'visualizer/map_wjs.html', {'map_id': map_id, 'js_all': js_all, 'css_all': css_all, 'data': jsonobj})

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
            minyear = request.POST.get("min_year", 2000)
            maxyear = request.POST.get("max_year", 2017)
        else:
            markersum = 50
            ship = "all"
            minyear = 2000
            maxyear = 2017

    else:
        markersum = int(request.GET.get("markers", 5000))
        ship = request.GET.get("ship", "all")
        minyear = int(request.POST.get("min_year", 2000))
        maxyear = int(request.POST.get("max_year", 2017))

    data = get_data(markersum, ship, minyear, maxyear)
    heat = []
    for d in data:
        heat.append((np.array([float(d[0]), float(d[1])]) * np.array([1, 1])).tolist())

    HeatMap(heat,
            name="Heat Map").add_to(m)


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

        q = Query.objects.get(pk=int(query))
        q = Query(document=q.document)
        doc = q.document
        # if 'orderings' not in doc.keys():
        #     doc['orderings'] = []
        doc['orderings'] = []
        doc['limit'] = []
        var_query_id = variable[:variable.find('_')]

        print doc
        for f in doc['from']:
            for s in f['select']:
                if s['name'] == variable:
                    s['aggregate'] = 'avg'
                    s['exclude'] = False
                elif str(s['name']).find('latitude') >= 0 and str(s['name']).find(var_query_id) >= 0:
                    s['groupBy'] = True
                    s['aggregate'] = 'round'
                    s['exclude'] = False
                    doc['orderings'].append({'name': str(s['name']), 'type': 'ASC'})
                elif str(s['name']).find('longitude') >= 0 and str(s['name']).find(var_query_id) >= 0:
                    s['groupBy'] = True
                    s['aggregate'] = 'round'
                    s['exclude'] = False
                    doc['orderings'].insert(0, {'name': str(s['name']), 'type': 'ASC'})
                else:
                    s['exclude'] = True
                    s['groupBy'] = False

        print doc
        q.document = doc
        raw_query = q.raw_query
        print raw_query
        #select_clause = re.findall(r"SELECT.*?\nFROM", raw_query)[0]
        #names = re.findall(r"round\((.*?)\)", select_clause)
        names = re.findall(r"round\((.*?)\)", raw_query)
        for name in names:
            raw_query = re.sub(r"round\((" + name + ")\)", "round(" + name + ", 1)", raw_query)


        # Create a leaflet map using folium
        m = create_folium_map(location=[0,0], zoom_start=3, max_zoom=10)

        try:
            connection = psycopg2.connect("dbname='bdo_platform' user='postgres' host='localhost' password='13131313'")
        except:
            print "I am unable to connect to the database"
        cursor = connection.cursor()
        cursor.execute(raw_query)
        data = cursor.fetchall()
        print data[:3]

        var_index = lat_index = lon_index = 0
        result_headers = q.execute(only_headers=True)[0]['headers']
        print result_headers
        for idx, c in enumerate(result_headers['columns']):
            if c['name'] == variable:
                var_index = idx
            elif str(c['name']).find('latitude') >= 0:
                lat_index = idx
            elif str(c['name']).find('longitude') >= 0:
                lon_index = idx

        print var_index, lat_index, lon_index

        # cursor = connection.cursor()
        # cursor.execute(
        #     """ SELECT  round(min(lat_2), 1) AS min_lat,
        #                 round(max(lat_2), 1) AS max_lat,
        #                 round(min(lon_3), 1) AS min_lon,
        #                 round(max(lon_3), 1) AS max_lon,
        #                 min(value)           AS min_val,
        #                 max(value)           AS max_val
        #         FROM   seabed_temp_1;""")
        # min_lat, max_lat, min_lon, max_lon, min_val, max_val = map(float, cursor.fetchall()[0])
        # print min_lat, max_lat, min_lon, max_lon, min_val, max_val

        # TODO: try to create the query above
        min_lat = float(min(data, key=lambda x: x[lat_index])[lat_index])
        max_lat = float(max(data, key=lambda x: x[lat_index])[lat_index])
        min_lon = float(min(data, key=lambda x: x[lon_index])[lon_index])
        max_lon = float(max(data, key=lambda x: x[lon_index])[lon_index])
        min_val = float(min(data, key=lambda x: x[var_index])[var_index])
        max_val = float(max(data, key=lambda x: x[var_index])[var_index])
        print min_lat, max_lat, min_lon, max_lon, min_val, max_val

        lats_bins = np.arange(min_lat, max_lat + 0.00001, 0.1)
        # print lats_bins
        lons_bins = np.arange(min_lon, max_lon + 0.00001, 0.1)
        # print lons_bins
        Lats, Lons = np.meshgrid(lats_bins, lons_bins)
        #print Lats
        #print Lons

        # Create grid data needed for the contour plot
        #final_data = create_grid_data(lats_bins, lons_bins, data)

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
        print final_data[:3]


        # # Perform a query and get data
        # headers, data = get_test_data(query, request.user)
        # other_dims = list()
        # for idx, col in enumerate(headers['columns']):
        #     if col['isVariable'] == True:
        #         if str(col['name']) == variable:
        #             print 'found'
        #             var_col = idx
        #     else:
        #         if str(col['name']).find('latitude') != -1:
        #             lat_col = idx
        #         elif str(col['name']).find('longitude') != -1:
        #             lon_col = idx
        #         else:
        #             other_dims.append(idx)
        # other_dims_first_vals = list()
        # for d in other_dims:
        #     other_dims_first_vals.append(str(data[0][d]))
        #
        # print other_dims
        # print other_dims_first_vals
        # var_col = 0
        # # Select only data with the same (first) value on any other dimensions except lat/lon
        # data = [(float(d[lat_col]), float(d[lon_col]), float(d[var_col])) for d in data if filter_data(d, other_dims, other_dims_first_vals) == 0]
        # print data
        # # Aggregate data into bins
        # lats = np.array(sorted(list(set([float(item[0]) for item in data]))))
        # lats_bins = create_bins(lats, step)
        # lons = np.array(sorted(list(set([float(item[1]) for item in data]))))
        # lons_bins = create_bins(lons, step)
        #
        # # create meshgrids of the 2 dimensions neede for the contour plot
        # Lats, Lons = np.meshgrid(lats_bins, lons_bins)
        #
        # # Create grid data needed for the contour plot
        # final_data = create_grid_data(lats_bins, lons_bins, data)
        #
        # print Lats
        # print Lons
        # print final_data
        #
        # # Set the intervals for each contour
        # min_val = min([float(item[2]) for item in data])
        # max_val = max([float(item[2]) for item in data])
        levels = np.linspace(start=min_val, stop=max_val, num=n_contours)
        print 'level ok'


        # Create a contour plot plot from grid (lat, lon) data
        use('Agg')
        fig = Figure()
        ax = fig.add_subplot(111)
        plt.contourf(Lons, Lats, final_data, levels=levels, cmap=plt.cm.coolwarm)
        plt.axis('off')
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        plt.draw()
        plt.savefig('map.png', bbox_inches=extent, transparent=True, pad_inches=0)

        fig = None
        ax = None
        fig = Figure()
        ax = fig.add_subplot(111)
        fig = None
        ax = None

        # read in png file to numpy array
        data_img = Image.open("map.png")
        data = trim(data_img)
        data_img.close()
        #data = imrotate(data, 180)

        # Overlay the image
        contour_layer = plugins.ImageOverlay(data, zindex=1, opacity=0.8, mercator_project=True, bounds=[[lats_bins.min(), lons_bins.min()], [lats_bins.max(), lons_bins.max()]])
        contour_layer.layer_name = 'Contour'
        m.add_child(contour_layer)

        # TODO: add other dimensions' names and values used for the contour along with colorbar

        # Overlay an extra coastline field (to be removed
        folium.GeoJson(open('ne_50m_land.geojson').read(),
                       style_function=lambda feature: {'fillColor': '#002a70', 'color': 'black', 'weight': 3})\
            .add_to(m)\
            .layer_name='Coastline'


        # Add layer contorl
        folium.LayerControl().add_to(m)

        # Create the map visualization and render it
        m.save('templates/map.html')
        f = open('templates/map.html', 'r')
        map_html = f.read()
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
        f.close()
        os.remove('map.png')
        os.remove('templates/map.html')
        return render(request, 'visualizer/map_viz_folium.html', {'map_id': map_id, 'js_all': js_all, 'css_all': css_all})
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
    query_pk = int(str(request.GET.get('query', '')))
    query = Query.objects.get(pk=query_pk)
    query = Query(document=query.document)
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))

    doc = query.document
    for f in doc['from']:
        for s in f['select']:
            if s['name'] == y_var:
                s['aggregate'] = 'avg'
                s['exclude'] = False
            elif s['name'] == x_var:
                s['groupBy'] = True
                s['exclude'] = False
            else:
                s['exclude'] = True
    doc['orderings'] = [{'name': x_var, 'type': 'ASC'}]
    query.document = doc
    raw_query = query.raw_query
    print doc
    print raw_query

    #result = query.execute()
    #result_data = result['results']
    #result_headers = result['headers']

    """
    try:
        connection = psycopg2.connect("dbname='bdo_platform' user='postgres' host='localhost' password='13131313'")
    except:
        print "I am unable to connect to the database"
    """

    cursor = connection.cursor()
    result_data = cursor.execute(raw_query)

    cursor = connection.cursor()
    cursor.execute(raw_query)
    result_data = cursor.fetchall()
    result_headers = query.execute(only_headers=True)[0]['headers']

    y_var_index = x_var_index = 0
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] == y_var:
            y_var_index = idx
        elif c['name'] == x_var:
            x_var_index = idx

    json_data = []
    for d in result_data:
        json_data.append({y_var: d[y_var_index], x_var: str(d[x_var_index])})



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

    doc = query.document

    if 'time' in x_var:
        isDate = 'true'
    else:
        isDate = 'false'

    return render(request, 'visualizer/line_chart_am.html', {'data': json_data, 'value_col': y_var, 'category_col': x_var, 'isDate': isDate})


def get_pie_chart_am(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = Query.objects.get(pk=query_pk)
    query = Query(document=query.document)
    key_var = str(request.GET.get('key_var', ''))
    value_var = str(request.GET.get('value_var', ''))

    doc = query.document
    print doc
    for f in doc['from']:
        for s in f['select']:
            if s['name'] == value_var:
                s['aggregate'] = 'avg'
                s['exclude'] = False
            elif s['name'] == key_var:
                s['groupBy'] = True
                s['exclude'] = False
            else:
                s['exclude'] = True
    print doc

    doc['orderings'] = [{'name': key_var, 'type': 'ASC'}]
    query.document = doc
    raw_query = query.raw_query
    print doc
    print raw_query

    #result_data = query.execute()['results']
    #print result_data

    try:
        connection = psycopg2.connect("dbname='bdo_platform' user='postgres' host='localhost' password='13131313'")
    except:
        print "I am unable to connect to the database"
    cursor = connection.cursor()
    cursor.execute(raw_query)
    result_data = cursor.fetchall()
    result_headers = query.execute(only_headers=True)[0]['headers']

    value_var_index = key_var_index = 0
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] == value_var:
            value_var_index = idx
        elif c['name'] == key_var:
            key_var_index = idx

    json_data = []
    for d in result_data:
        json_data.append({value_var: d[0], key_var: str(d[1])})

    return render(request, 'visualizer/pie_chart_am.html', {'data': json_data, 'value_var': value_var, 'key_var': key_var})


def get_column_chart_am(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = Query.objects.get(pk=query_pk)
    query = Query(document=query.document)
    x_var = str(request.GET.get('x_var', ''))
    y_var = str(request.GET.get('y_var', ''))

    doc = query.document
    print doc
    for f in doc['from']:
        for s in f['select']:
            if s['name'] == y_var:
                s['aggregate'] = 'avg'
                s['exclude'] = False
            elif s['name'] == x_var:
                s['groupBy'] = True
                s['exclude'] = False
            else:
                s['exclude'] = True
    print doc

    doc['orderings'] = [{'name': x_var, 'type': 'ASC'}]
    query.document = doc
    raw_query = query.raw_query
    print doc
    print raw_query

    try:
        connection = psycopg2.connect("dbname='bdo_platform' user='postgres' host='localhost' password='13131313'")
    except:
        print "I am unable to connect to the database"
    cursor = connection.cursor()
    cursor.execute(raw_query)
    result_data = cursor.fetchall()
    result_headers = query.execute(only_headers=True)[0]['headers']

    y_var_index = x_var_index = 0
    for idx, c in enumerate(result_headers['columns']):
        if c['name'] == y_var:
            y_var_index = idx
        elif c['name'] == x_var:
            x_var_index = idx

    json_data = []
    for d in result_data:
        json_data.append({y_var: d[y_var_index], x_var: str(d[x_var_index])})


    if 'time' in x_var:
        isDate = 'true'
    else:
        isDate = 'false'
    return render(request, 'visualizer/column_chart_am.html', {'data': json_data, 'value_col': y_var, 'category_col': x_var, 'isDate': isDate})


def get_data_table(request):
    query_pk = int(str(request.GET.get('query', '')))
    query = Query.objects.get(pk=query_pk)

    result_data = query.execute()['results']

    # json_data = []
    # for d in result_data:
    #     json_data.append({y_var: d[y_var_index], x_var: str(d[x_var_index])})

    return render(request, 'visualizer/data_table.html', {'data': result_data})
