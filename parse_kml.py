import json
import os
from pykml import parser
from os import path
from shapely.geometry import Polygon
from shapely.geometry import Point
import csv
import time
from datetime import datetime

max_lat = -90
max_lon = -180
min_lat = 90
min_lon = 180

def read_file_line_by_line(file_path):
    filepath = file_path
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while cnt<23:
            print("Line {}: {}".format(cnt, line.strip()))
            line = fp.readline()
            cnt += 1
        count2 = 0
        mline = ''
        while count2<200:
            mline = mline+ line[count2]
            count2 = count2 +1
        print mline

def parse(file_path, created_json_path):
    kml_file = path.join(file_path)

    with open(kml_file) as f:
        document = parser.parse(f).getroot()
    new_file = open(created_json_path, "w+")
    new_file.write(parse_doc(document))



def parse_doc(doc):
    placemark_list = []
    placemark_map = {}
    limits = {}
    for p in doc.Document.Folder.Placemark:
        polygon_map = build_polygon_map(p)
        placemark_list.append(polygon_map)
    global max_lat
    global max_lon
    global min_lat
    global min_lon
    placemark_map['placemarks'] = placemark_list
    limits['max_lat'] = max_lat
    limits['max_lon'] = max_lon
    limits['min_lat'] = min_lat
    limits['min_lon'] = min_lon
    placemark_map['limits'] = limits
    return json.dumps(placemark_map)


def build_polygon_map(p):
    polygon_map = {}
    polygons = extract_polygons(p)
    polygon_list = build_polygon_list(polygons)
    polygon_map['polygons'] = polygon_list
    return polygon_map


def extract_polygons(placemark_elem):
    try:
        polygons = placemark_elem.MultiGeometry.Polygon
    except AttributeError:
        return None
    return polygons


def extract_outer_boundaries(polygon):
    try:
        outer_boundaries = polygon.outerBoundaryIs
    except AttributeError:
        return None
    return outer_boundaries


def extract_inner_boundaries(polygon):
    try:
        inner_boundaries = polygon.innerBoundaryIs
    except AttributeError:
        return None
    return inner_boundaries


def extract_coordinates(boundaries):
    try:
        coords = boundaries.LinearRing.coordinates.text.strip()
    except AttributeError:
        return ''
    return coords


def build_polygon_list(polygons):
    polygon_list = []
    for p in polygons:
        polygon_map = {}
        polygon_map['outer_boundary'] = build_outer_boundary_for_map(p)
        polygon_map['inner_boundaries'] = build_inner_boundaries_for_map(p)
        polygon_list.append(polygon_map)

    return polygon_list


def build_inner_boundaries_for_map(p):
    inner_boundaries = extract_inner_boundaries(p)
    inner_boundary_list = []
    if inner_boundaries is None:
        return []

    for i in inner_boundaries:
        coords = extract_coordinates(i)
        if coords != '':
            coordinates = coords.split(' ')
            coord_map = build_coord_map(coordinates)
            inner_boundary_list.append(coord_map)

    return inner_boundary_list


def build_outer_boundary_for_map(p):
    outer_boundary = extract_outer_boundaries(p)
    coords = extract_coordinates(outer_boundary)
    coord_map = {}
    if outer_boundary is None:
        return None

    if coords != '':
        coordinates = coords.split(' ')
        coord_map = build_coord_map(coordinates)

    return coord_map


def build_coord_map(coordinates):
    coord_map = {}
    coor_list = []
    global max_lon
    global max_lat
    global min_lat
    global min_lon
    for c in coordinates:
        coor_map = {}
        longitude, latitude = c.strip().split(',')
        coor_map['longitude'] = float(longitude)
        coor_map['latitude'] = float(latitude)
        if float(latitude) > max_lat:
            max_lat = float(latitude)
        if float(latitude) < min_lat:
            min_lat = float(latitude)
        if float(longitude) > max_lon:
            max_lon = float(longitude)
        if float(longitude) < min_lon:
            min_lon = float(longitude)
        # coor_map['altitude'] = float(altitude)
        coor_list.append(coor_map)
    coord_map['coordinates'] = coor_list
    return coord_map



def create_natura_grid(natura_json_directory, natura_grid_directory, multiplier=1000):
    #     multiplier must be set to 1000 (most fitted resolution)
    #     natura_json_directory is the directory where the natura json files are saved
    #     natura_grid_directory is the directory where th natura grid files are saved
    count = 1
    for filename in os.listdir(natura_json_directory):
        if filename.endswith(".json"):
            create_map_grid_zone(natura_json_directory+'/'+str(filename), natura_grid_directory + '/' + str(filename).split('.')[0]+'_grid_', multiplier)
            count = count + 1
            print str(filename) + ' parsed! Grid file created!'
        else:
            pass
    print 'Resolution Used:' + str(multiplier)
    print 'Grid Creation Finished'


def create_map_grid_zone(json_file_path, grid_file_path, multiplier):

    kml_filepath = json_file_path
    with open(kml_filepath) as json_kml_data:
        kml_data = json.load(json_kml_data)
    file = open(grid_file_path, 'w')
    # resolution in the form of a multiplier
    # max,min lat/lons of the area to be separated into a grid
    limits = kml_data['limits']
    max_lat = limits['max_lat']
    min_lat = limits['min_lat']
    max_lon = limits['max_lon']
    min_lon = limits['min_lon']
    lat_dist = max_lat - min_lat
    lon_dist = max_lon - min_lon
    polygons = []
    for kd in kml_data['placemarks']:
        for point in kd['polygons']:
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
            polygon['min_lat'] = point['outer_boundary']['min_lat']
            polygon['max_lat'] = point['outer_boundary']['max_lat']
            polygon['min_lon'] = point['outer_boundary']['min_lon']
            polygon['max_lon'] = point['outer_boundary']['max_lon']
            polygons.append(polygon)
    natura_grid = []
    lat_max = int(lat_dist*multiplier)
    lon_max = int(lon_dist*multiplier)
    for lat in range(0, lat_max):
        natura_grid_row = []
        for lon in range(0, lon_max):
            # clearing irrelevant natura polygons
            cleared_polygons = []
            for po in polygons:
                po_min_lat = float(po['min_lat'])
                po_max_lat = float(po['max_lat'])
                po_min_lon = float(po['min_lon'])
                po_max_lon = float(po['max_lon'])
                checked_point_lat = (float(lat)/multiplier + min_lat)
                checked_point_lon = (float(lon)/multiplier + min_lon)
                if checked_point_lat > po_max_lat or checked_point_lat < po_min_lat or checked_point_lon > po_max_lon or checked_point_lon < po_min_lon:
                    continue
                cleared_polygons.append(po)

            print 'checking point:('+str(float(lat)/multiplier + min_lat)+','+str(float(lon)/multiplier + min_lon)+')'
            is_inner = False
            found_natura = False
            for pol in cleared_polygons:
                inner_pols = pol['inners']
                if is_inner:
                    break
                for in_pol in inner_pols:
                    shapely_pol = Polygon(in_pol)
                    if is_inner:
                        break
                    if shapely_pol.contains(Point((float(lat)/multiplier + min_lat), (float(lon)/multiplier + min_lon))):
                        is_inner = True
                outer_pol = pol['outer']
                shapely_pol = Polygon(outer_pol)
                if shapely_pol.contains(Point((float(lat)/multiplier + min_lat), (float(lon)/multiplier + min_lon))):
                    found_natura = True
                    break
            if found_natura:
                natura_grid_row.append(1)
            else:
                natura_grid_row.append(0)
        natura_grid.append(natura_grid_row)
    file.close()
    dic = {}
    with open(grid_file_path + '.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        [writer.writerow(r) for r in natura_grid]
        csvfile.close()
    with open(grid_file_path + '_info', 'w') as file:
        dic['resolution'] = multiplier
        dic['min_lat'] = min_lat
        dic['min_lon'] = min_lon
        json.dump(dic, file, default=myconverter)


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()