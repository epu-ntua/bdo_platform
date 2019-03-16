import json

from shapely.geometry import Polygon
from shapely.geometry import Point


def calculate(data_filename, red_points_filename):
    kml_filepath = 'visualizer/static/visualizer/files/kml2.json'
    data_file = 'visualizer/static/visualizer/files/'+ data_filename
    with open(data_file) as json_data:
        data = json.load(json_data)
    with open(kml_filepath) as json_kml_data:
        kml_data = json.load(json_kml_data)
    min_lat, max_lat, min_lon, max_lon = find_min_max_lat_lon(data)
    filtered_kml_data = filter_out_of_range_areas(kml_data, min_lat, max_lat, min_lon, max_lon)
    polygons = get_polygons_in_range(filtered_kml_data)
    build_red_points_file(data, polygons, red_points_filename)


def find_min_max_lat_lon(data):
    if len(data) > 0:
        min_lat = max_lat = data[0]['Lat']
        min_lon = max_lon = data[0]['Lon']
        for d in data:
            if d['Lat'] < min_lat:
                min_lat = d['Lat']
            elif d['Lat'] > max_lat:
                max_lat = d['Lat']
            if d['Lon'] < min_lon:
                min_lon = d['Lon']
            elif d['Lon'] > max_lon:
                max_lon = d['Lon']
        return min_lat, max_lat, min_lon, max_lon
    else:
        return -90, 90, -180, 180


def filter_out_of_range_areas(kml_data, min_lat, max_lat, min_lon, max_lon):
    polygons = []
    for kd in kml_data['placemarks']:
        for po in kd['polygons']:
            po_min_lat = float(po['outer_boundary']['min_lat'])
            po_max_lat = float(po['outer_boundary']['max_lat'])
            po_min_lon = float(po['outer_boundary']['min_lon'])
            po_max_lon = float(po['outer_boundary']['max_lon'])

            if min_lat > po_max_lat or max_lat < po_min_lat or min_lon > po_max_lon or max_lon < po_min_lon:
                continue
            polygons.append(po)
    return polygons


def get_polygons_in_range(filtered_kml_data):
    polygons = []
    for point in filtered_kml_data:
        polygon = {}
        outer_p = []
        o = point['outer_boundary']
        for c in o['coordinates']:
            outer_p.append((c['latitude'], c['longitude']))
        inner_polygons = []
        for i in point['inner_boundaries']:
            inner_p = []
            for c in i['coordinates']:
                inner_p.append((c['latitude'], c['longitude']))
            inner_polygons.append(inner_p)
        polygon['outer'] = outer_p
        polygon['inners'] = inner_polygons
        polygons.append(polygon)
    return polygons


def build_red_points_file(data, polygons, red_points_filename):
    file = open('visualizer\\static\\visualizer\\files\\'+red_points_filename, 'w')
    for p in data:
        is_inner = False
        for pol in polygons:
            inner_pols = pol['inners']
            if is_inner:
                break
            for in_pol in inner_pols:
                shapely_pol = Polygon(in_pol)
                if is_inner:
                    break
                if shapely_pol.contains(Point(p['Lat'], p['Lon'])):
                    is_inner = True

            outer_pol = pol['outer']
            shapely_pol = Polygon(outer_pol)
            if shapely_pol.contains(Point(p['Lat'], p['Lon'])):
                file.write(str(p['Lat']) + ', ' + str(p['Lon']) + '\n')
                break
    file.close()

# calculate()
