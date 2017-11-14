from query_designer.models import Query
import numpy as np
from math import floor, ceil
import folium.plugins as plugins
import folium
from PIL import Image, ImageChops


def get_test_data():
    q = Query.objects.get(pk=6)
    return q.execute()['results']


def trim(img):
    border = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, border)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        img = img.crop(bbox)
    return np.array(img)


def create_grid_data(lats, lons, data):
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

    # print grid
    # print grid_count
    return grid


# TODO: replace 100 and make it configurable
def create_bins(list, step):
    return np.arange(floor(list.min() * 100) / 100, ceil(list.max() * 100) / 100 + 0.00001, step)


def create_folium_map(location=[0,0], zoom_start=2, max_zoom=13):
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   tiles=tiles_str + token_str,
                   attr=attr_str)

    # folium.TileLayer('openstreetmap').add_to(m)

    plugins.Fullscreen(
        position='topright',
        title='Expand',
        title_cancel='Exit',
        force_separate_button=True).add_to(m)
    return m
