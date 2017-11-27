from __future__ import unicode_literals
# -*- coding: utf-8 -*-

from django.shortcuts import render
from bs4 import BeautifulSoup
import folium
import folium.plugins as plugins
import numpy as np
from datetime import datetime, timedelta
import os

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
        line = request.GET.get("line", False)
        markersum = int(request.GET.get("markers", 50))
        ship = request.GET.get("ship", "all")
        minyear = int(request.POST.get("min_year", 2000))
        maxyear = int(request.POST.get("max_year", 2017))

    data = get_test_data(markersum, ship, minyear, maxyear)

    #length = len(result) - 1
    #data = []
    #for index in range(0, length):
        #d = result[index]
        #data.append((np.array([float(d[3]), float(d[4]), int(d[1])]) * np.array([1, 1, 1])).tolist())
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

    if line:

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

    #

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

    data = get_test_data(markersum, ship, minyear, maxyear)
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
