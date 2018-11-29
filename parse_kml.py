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
            coordinates = coords.split('\n')
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
        coordinates = coords.split('\n')
        coord_map = build_coord_map(coordinates)

    return coord_map


def build_coord_map(coordinates):
    coord_map = {}
    coor_list = []
    for c in coordinates:
        coor_map = {}
        longitude, latitude, altitude = c.strip().split(',')
        coor_map['longitude'] = float(longitude)
        coor_map['latitude'] = float(latitude)
        # coor_map['altitude'] = float(altitude)
        coor_list.append(coor_map)
    coord_map['coordinates'] = coor_list
    return coord_map


# print(parse('Natura2000_AEG3.kml'))
