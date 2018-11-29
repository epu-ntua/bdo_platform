import json

from pykml import parser
from os import path

def parse(file_path):
    kml_file = path.join(file_path)

    with open(kml_file) as f:
        document = parser.parse(f).getroot()

    return parse_doc(document)


def parse_doc(doc):
    placemark_list = []
    placemark_map = {}
    for p in doc.Document.Placemark:
        polygon_map = build_polygon_map(p)
        placemark_list.append(polygon_map)
    placemark_map['placemarks'] = placemark_list
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
        outer_boundary_map = build_outer_boundary_list(p)
        inner_boundary_map = build_inner_boundary_map(p)
        if (inner_boundary_map is not None):
            polygon_list.append((outer_boundary_map, inner_boundary_map))
        else:
            polygon_list.append([outer_boundary_map])
    return polygon_list


def build_inner_boundary_map(p):
    inner_boundary = extract_inner_boundaries(p)
    if inner_boundary is None:
        return None
    inner_boundary_map = {}

    coords = extract_coordinates(inner_boundary)
    if coords != '':
        coordinates = coords.split('\n')
        coord_map = build_coord_map(coordinates)
        inner_boundary_map['inner_boundary'] = coord_map
    return inner_boundary_map


def build_outer_boundary_list(p):
    outer_boundary = extract_outer_boundaries(p)
    if outer_boundary is None:
        return None
    outer_boundary_map = {}
    coords = extract_coordinates(outer_boundary)
    if coords != '':
        coordinates = coords.split('\n')
        coord_map = build_coord_map(coordinates)
        outer_boundary_map['outer_boundary'] = coord_map
    return outer_boundary_map


def build_coord_map(coordinates):
    coord_map = {}
    coor_list = []
    for c in coordinates:
        coor_map = {}
        longitude, latitude, altitude = c.strip().split(',')
        coor_map['longitude'] = float(longitude)
        coor_map['latitude'] = float(latitude)
        coor_map['altitude'] = float(altitude)
        coor_list.append(coor_map)
    coord_map['coordinates'] = coor_list
    return coord_map


# print(parse('Natura2000_AEG3.kml'))