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

from query_designer.models import Query
import matplotlib.pyplot as plt
import geojsoncontour
import json
from scipy.ndimage import imread
from math import floor, ceil
from matplotlib.mlab import griddata



def get_test_data():
    q = Query.objects.get(pk=6)
    return q.execute()['results']


def map_viz(request):
    return render(request, 'visualizer/map_viz.html', {})


def create_grid_data(lats, lons, data_dict):
    # print "Lats"
    # print lats
    # print "Lons"
    # print lons
    result = list()
    for lon in lons:
        row = list()
        for lat in lats:
            try:
                row.append(data_dict[str(lat)+'-'+str(lon)])
            except KeyError:
                row.append(None)
        result.append(row)
    return result


def create_grid_data2(lats, lons, data):

    grid = list()
    grid_count = list()
    for i in range(0, len(lons)):
        grid_row = list()
        grid_count_row = list()
        for j in range(0, len(lats)):
            grid_row.append(None)
            grid_count_row.append(0)
        grid.append(grid_row)
        grid_count.append(grid_count_row)

    for item in data:
        j = 0
        for l in lats:
            if item[0] < l:
                j += 1
        i = 0
        for l in lons:
            if item[1] < l:
                i += 1

        if grid[i][j] is None:
            grid[i][j] = item[2]
            grid_count[i][j] = 1
        else:
            grid[i][j] += item[2]
            grid_count[i][j] += 1

    for i in range(0, len(lons)):
        for j in range(0, len(lats)):
            if grid_count[i][j] > 0:
                grid[i][j] /= grid_count[i][j]

    print grid
    print grid_count
    return grid


def map_viz_folium(request):
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 13

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   tiles=tiles_str+token_str,
                   attr=attr_str)

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True).add_to(m)

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
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 13

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   tiles=tiles_str+token_str,
                   attr=attr_str)

    # folium.TileLayer('openstreetmap').add_to(m)

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True).add_to(m)

    data = get_test_data()
    n_contours = 20
    min_val = min([float(item[0]) for item in data])
    max_val = max([float(item[0]) for item in data])
    levels = np.linspace(start=min_val, stop=max_val, num=n_contours)

    # data = [(np.array([float(d[3]), float(d[4]), float(d[0])]) * np.array([1, 1, 1])).tolist() for d in data]
    # data = [(float(d[3]), float(d[4]), float(d[0])) for d in data]
    data_temp = [(float(d[3]), float(d[4]), float(d[0]), str(d[1]), float(d[2])) for d in data]
    time_selected = data_temp[0][3]
    depth_selected = data_temp[0][4]
    data = list()
    for d in data_temp:
        if time_selected == d[3] and depth_selected == d[4]:
            data.append((d[0], d[1], d[2]))

    # data_dict = dict()
    # for d in data:
    #     key = str(float(d[3])) + '-' + str(float(d[4]))
    #     data_dict[key] = float(d[0])

    step = 0.1

    lats = np.array(sorted(list(set([float(item[0]) for item in data]))))
    lats_bins = np.arange(floor(lats.min()*100)/100, ceil(lats.max()*100)/100+0.00001, step)
    print lats
    print lats_bins

    lons = np.array(sorted(list(set([float(item[1]) for item in data]))))
    lons_bins = np.arange(floor(lons.min()*100)/100, ceil(lons.max()*100)/100+0.00001, step)
    print lons
    print lons_bins

    Lats, Lons = np.meshgrid(lats_bins, lons_bins)
    final_data = create_grid_data2(lats_bins, lons_bins, data)
    # print "final data:"
    # print final_data

    # Create a contour plot plot from grid (lat, lon) data
    fig = plt.figure(frameon=False)
    ax = fig.add_subplot(111)
    # contour = ax.contourf(Lons, Lats, final_data, levels=levels, cmap=plt.cm.Reds)
    plt.contourf(Lons, Lats, final_data, levels=levels, cmap=plt.cm.coolwarm)
    plt.axis('off')

    # plt.show(contour)
    # fig.subplots_adjust(bottom=0)
    # fig.subplots_adjust(top=0.1)
    # fig.subplots_adjust(right=0.1)
    # fig.subplots_adjust(left=0)
    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    plt.savefig('map.png', bbox_inches=extent, transparent=True, pad_inches=0)
    # plt.show()

    # read in png file to numpy array
    # data = imread('map.png')
    data = Image.open("map.png")
    data = trim(data)
    data = imrotate(data, 180)

    # Overlay the image
    # m.add_child(plugins.ImageOverlay(data, opacity=0.8, bounds=[[lats_bins.min()-0.5, lons_bins.min()-0.4], [lats_bins.max(), lons_bins.max()+0.5]]))
    m.add_child(plugins.ImageOverlay(data, zindex=1, opacity=0.8, bounds=[[lats_bins.min(), lons_bins.min()], [lats_bins.max(), lons_bins.max()]]))
    folium.GeoJson(open('ne_50m_land.geojson').read(), style_function=lambda feature: {'fillColor': 'none', 'color': '#AEEE00', 'weight': 2}).add_to(m)

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


def make_map(bbox):
    fig, ax = plt.subplots(figsize=(8, 6))
    # ax.set_extent(bbox)
    ax.coastlines(resolution='50m')
    return fig, ax


def trim(img):
    border = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, border)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        img = img.crop(bbox)
    return np.array(img)


def map_viz_folium_colormesh(request):
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 13

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   tiles=tiles_str+token_str,
                   attr=attr_str)

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True).add_to(m)

    data = get_test_data()
    n_contours = 20
    min_val = min([float(item[0]) for item in data])
    max_val = max([float(item[0]) for item in data])
    levels = np.linspace(start=min_val, stop=max_val, num=n_contours)

    # data = [(np.array([float(d[3]), float(d[4]), float(d[0])]) * np.array([1, 1, 1])).tolist() for d in data]
    data_temp = [(float(d[3]), float(d[4]), float(d[0]), str(d[1]), float(d[2])) for d in data]
    time_selected = data_temp[0][3]
    depth_selected = data_temp[0][4]
    data = list()
    for d in data_temp:
        if time_selected == d[3] and depth_selected == d[4]:
            data.append((d[0], d[1], d[2]))

    lats = np.array(sorted(list(set([float(item[0]) for item in data]))))
    lons = np.array(sorted(list(set([float(item[1]) for item in data]))))

    bbox = [lats.min(), lats.max(), lons.min(), lons.max()]

    level = 10  # 10 meters temperature.
    # data = np.ma.masked_invalid(merc['temp'][level, ...])

    fig, ax = make_map(bbox=bbox)
    cs = ax.pcolormesh(lats, lons, data, cmap=cm.avhrr)
    fig.savefig('GS.png', transparent=True)

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


def map_viz_folium_colormap(request):
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'
    location = [0, 0]
    zoom_start = 2
    max_zoom = 15

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   tiles=tiles_str+token_str,
                   attr=attr_str)

    data = get_test_data()
    # print data
    # data = [(np.array([float(d[3]), float(d[4]), float(d[0])]) * np.array([1, 1, 1])).tolist() for d in data]
    data_dict = dict()
    for d in data:
        key = str(float(d[3])) + '-' + str(float(d[4]))
        data_dict[key] = float(d[0])

    lats = np.array(sorted(list(set([float(item[3]) for item in data]))))
    lons = np.array(sorted(list(set([float(item[4]) for item in data]))))
    Lats, Lons = np.meshgrid(lats, lons)
    final_data = create_grid_data(lats, lons, data_dict)

    max_lat = max(lats)
    min_lat = min(lats)
    max_lon = max(lons)
    min_lon = min(lons)
    max_val = max([float(item[0]) for item in data])
    min_val = min([float(item[0]) for item in data])

    geo_json_data_feat = list()
    for j in range(0, int((max_lat-min_lat)/0.5)):
        for i in range(0, int((max_lon-min_lon)/0.5)):
            box = dict()
            box['type'] = "Feature"
            box['id'] = str(i)+str(j)
            box['properties'] = {"name": str(i)+str(j)}
            box['geometry'] = {"type": "Polygon",
                               "coordinates": [[[min_lon+i*0.5, min_lat+j*0.5],
                                                [min_lon+(i+1)*0.5, min_lat+j*0.5],
                                                [min_lon+(i+1)*0.5, min_lat+(j+1)*0.5],
                                                [min_lon+i*0.5, min_lat+(j+1)*0.5],
                                                [min_lon+i*0.5, min_lat+j*0.5]]]
                               }
            geo_json_data_feat.append(box)

    data_dict_temp = dict()
    for feat in geo_json_data_feat:
        data_dict_temp[str(feat['id'])] = dict()
        data_dict_temp[str(feat['id'])]['value'] = 0
        data_dict_temp[str(feat['id'])]['count'] = 0

    data_dict = data_dict_temp

    # data_dict = dict()
    # for key, value in data_dict_temp.iteritems():
    #     if value['count'] > 0:
    #         data_dict[key] = value['value']/value['count']
    #     else:
    #         geo_json_data_feat.remove((item for item in geo_json_data_feat if item["id"] == key).next())

    geo_json_data = {"type": "FeatureCollection", "features": geo_json_data_feat}
    linear = cm.linear.YlOrRd.scale(min_val, max_val)
    folium.GeoJson(
        geo_json_data,
        style_function=lambda feature: {
            'fillColor': linear(data_dict[feature['id']]),
            'fillOpacity': 0.5,
            'weight': 1,
            'opacity': 0.5
        }
    ).add_to(m)
    # lats = [float(item[3]) for item in data]
    # lons = [float(item[4]) for item in data]
    # mag = [float(item[0]) for item in data]

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
