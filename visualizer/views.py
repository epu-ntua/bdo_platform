from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from PIL import Image, ImageChops
from django.shortcuts import render
from bs4 import BeautifulSoup
import folium
from folium import GeoJson
import folium.plugins as plugins
import numpy as np
import branca.colormap as cm
from datetime import datetime, timedelta
import os

from matplotlib.colors import rgb2hex
from scipy.misc import imrotate

import matplotlib.pyplot as plt
import geojsoncontour
import json
from scipy.ndimage import imread
from math import floor, ceil
from matplotlib.mlab import griddata
from utils import *


def test_request_include(request):
    return render(request, 'visualizer/test_request_include.html', {})


def test_request(request):
    return render(request, 'visualizer/test_request.html', {})


def get_map_simple(request):
    return render(request, 'visualizer/map_viz.html', {})


def get_map_contour(request):
    return render(request, 'visualizer/map_viz.html', {})


def map_viz(request):
    return render(request, 'visualizer/map_viz.html', {})


def map_viz_folium(request):
    m = create_folium_map(location=[0, 0], zoom_start=2, max_zoom=13)

    data = get_test_data()
    n_contours = 40
    min_val = min([float(item[0]) for item in data])
    max_val = max([float(item[0]) for item in data])
    levels = np.linspace(start=min_val, stop=max_val, num=n_contours)

    # data = [(np.array([float(d[3]), float(d[4]), float(d[0])]) * np.array([1, 1, 1])).tolist() for d in data]
    data_dict = dict()
    for d in data:
        key = str(float(d[3])) + '-' + str(float(d[4]))
        data_dict[key] = float(d[0])

    lats = np.array(sorted(list(set([float(item[3]) for item in data]))))
    lons = np.array(sorted(list(set([float(item[4]) for item in data]))))
    Lats, Lons = np.meshgrid(lats, lons)
    final_data = create_grid_data(lats, lons, data_dict)
    # print "final data:"
    # print final_data

    # Create a contour plot plot from grid (lat, lon) data
    figure = plt.figure()
    ax = figure.add_subplot(111)
    contour = ax.contour(Lons, Lats, final_data, levels=levels, cmap=plt.cm.Reds)

    # # Make a colorbar for the ContourSet returned by the contourf call.
    # cbar = plt.colorbar(contour)
    # # Add the contour line levels to the colorbar
    # cbar.add_lines(contour)

    # print 'contour levels'
    # print levels
    # collections = contour.collections
    # for collection in collections:
    #     # paths = collection.get_paths()
    #     # print paths
    #     print 'get_edgecolor'
    #     print rgb2hex(collection.get_edgecolor()[0])

    # Convert matplotlib contour to geojson
    geojsoncontour.contour_to_geojson(
        contour=contour,
        geojson_filepath='out.geojson',
        contour_levels=levels,
        ndigits=3,
    )

    with open('out.geojson') as f:
        lines = json.load(f)
        lines = json.loads(json.dumps(lines).replace('LineString', 'Polygon').replace('[[', '[[[').replace(']]', ']]]'))
    # print lines

    GeoJson(lines,
            style_function=lambda feature: {
                'fillColor': feature['properties']['stroke'],
                'weight': 0,
                'fillOpacity': 0.5,
            }).add_to(m)

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
    # Create a leaflet map using folium
    m = create_folium_map(location=[0,0], zoom_start=2, max_zoom=5)
    # Perform a query and get data
    data = get_test_data()

    # Select only data with the same depth and time
    # TODO: this should be configurable
    data_temp = [(float(d[3]), float(d[4]), float(d[0]), str(d[1]), float(d[2])) for d in data]
    time_selected = data_temp[0][3]
    depth_selected = data_temp[0][4]
    data = list()
    for d in data_temp:
        if time_selected == d[3] and depth_selected == d[4]:
            data.append((d[0], d[1], d[2]))

    # Aggregate data into bins
    step = 0.1
    lats = np.array(sorted(list(set([float(item[0]) for item in data]))))
    lats_bins = create_bins(lats, step)
    lons = np.array(sorted(list(set([float(item[1]) for item in data]))))
    lons_bins = create_bins(lons, step)

    # create meshgrids of the 2 dimensions neede for the contour plot
    Lats, Lons = np.meshgrid(lats_bins, lons_bins)

    # Create grid data needed for the contour plot
    final_data = create_grid_data(lats_bins, lons_bins, data)

    # Set the intervals for each contour
    n_contours = 20
    min_val = min([float(item[2]) for item in data])
    max_val = max([float(item[2]) for item in data])
    levels = np.linspace(start=min_val, stop=max_val, num=n_contours)

    # Create a contour plot plot from grid (lat, lon) data
    fig = plt.figure(frameon=False)
    ax = fig.add_subplot(111)
    plt.contourf(Lons, Lats, final_data, levels=levels, cmap=plt.cm.coolwarm)
    plt.axis('off')
    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    plt.savefig('map.png', bbox_inches=extent, transparent=True, pad_inches=0)

    # read in png file to numpy array
    data = Image.open("map.png")
    data = trim(data)
    data = imrotate(data, 180)

    # Overlay the image
    contour_layer = plugins.ImageOverlay(data, zindex=1, opacity=0.8, bounds=[[lats_bins.min(), lons_bins.min()], [lats_bins.max()-0.09, lons_bins.max()]])
    contour_layer.layer_name = 'Contour'
    m.add_child(contour_layer)
    # Overlay an extra coastline field (to be removed
    folium.GeoJson(open('ne_50m_land.geojson').read(),
                   style_function=lambda feature: {'fillColor': 'none', 'color': '#AEEE00', 'weight': 2})\
        .add_to(m)\
        .layer_name='Coastline'
    # Add layer contorl
    folium.LayerControl().add_to(m)

    # Create the map visualization and render it
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
    max_zoom = 9

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   tiles=tiles_str+token_str,
                   attr=attr_str)



    # np.random.seed(3141592)
    # initial_data = (
    #     np.random.normal(size=(100, 2)) * np.array([[1, 1]]) +
    #     np.array([[48, 5]])
    # )
    # move_data = np.random.normal(size=(100, 2)) * 0.01
    # data = [(initial_data + move_data * i).tolist() for i in range(100)]
    # print data
    data = get_test_data()
    data = [(np.array([float(d[3]), float(d[4]), float(d[0])]) * np.array([1, 1, 1])).tolist() for d in data]
    # lats = [float(item[3]) for item in data]
    # lons = [float(item[4]) for item in data]
    # mag = [float(item[0]) for item in data]
    max_val = max([float(item[0]) for item in data])
    print data
    m.add_child(plugins.HeatMap(data,
                                radius=8,
                                max_val=max_val,
                                max_zoom=max_zoom,
                                min_opacity=0,
                                blur=15))

    feature_group = folium.FeatureGroup("Temperatures")

    for lat, lon, val in data:
        feature_group.add_child(folium.RegularPolygonMarker(location=[lat, lon],
                                                            popup="Lat: "+str(lat)+" Lon: "+str(lon)+"\nValue: "+str(val),
                                                            radius=15,
                                                            opacity=0,
                                                            fill_opacity=0))

    m.add_child(feature_group)

    # hm = plugins.HeatMapWithTime([data])
    # hm.add_to(m)

    # time_index = [
    #     (datetime.now() + k * timedelta(1)).strftime('%Y-%m-%d') for
    #     k in range(len(data))
    # ]
    # hm = plugins.HeatMapWithTime(
    #     data,
    #     index=time_index,
    #     auto_play=True,
    #     max_opacity=0.3
    # )
    #
    # hm.add_to(m)

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

