from query_designer.models import Query
import numpy as np
from math import floor, ceil
import folium.plugins as plugins
import folium
from PIL import Image, ImageChops
import numpy as np


def fig2data(fig):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll(buf, 3, axis=2)
    return buf


def fig2img ( fig ):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data ( fig )
    w, h, d = buf.shape
    return Image.fromstring( "RGBA", ( w ,h ), buf.tostring( ) )


def get_test_data(query_id):
    q = Query.objects.get(pk=query_id)
    result_json = q.execute()
    return result_json['headers'], result_json['results']


def filter_data(d, other_dims, other_dims_first_vals):
    for dim, val in zip(other_dims, other_dims_first_vals):
        if str(d[dim]) != val:
            return 1
    return 0


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
                   attr=attr_str,
                   control_scale=True)

    # folium.TileLayer('openstreetmap').add_to(m)

    plugins.Fullscreen(
        position='topright',
        title='Expand',
        title_cancel='Exit',
        force_separate_button=True).add_to(m)
    return m
