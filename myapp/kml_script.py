import xml.etree.ElementTree as ET
from shapely.geometry import LineString
from shapely.geometry import Polygon
from lxml import etree
import xml.dom.minidom
import re


def parse_coordinates1(coords_str):
    coords = [list(map(float, coord.strip().split())) for coord in coords_str.strip().split(';') if coord.strip()]
    segments = []
    for i in range(len(coords) - 1):
        segments.append([(coords[i][1], coords[i][0]), (coords[i + 1][1], coords[i + 1][0])])
    return segments

def create_kmal(segments, output_filename):
    with open(output_filename, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')
        for i, segment in enumerate(segments):
            if i % 2 == 0:
                f.write(f'<Placemark>\n<name>Segment {i+1}</name>\n<LineString>\n<coordinates>\n')
                f.write(f'{segment[0][0]},{segment[0][1]},0\n')
                f.write(f'{segment[1][0]},{segment[1][1]},0\n')
                f.write('</coordinates>\n</LineString>\n</Placemark>\n')
        f.write('</Document>\n</kml>\n')

def parse_coordinates(coordinates):
    return [tuple(map(float, coord.split(','))) for coord in coordinates.strip().split()]

def merge_segments(segments):
    merged_segments = []
    used = set()
    def find_segment_with_common_point(point):
        for i, (_, coords) in enumerate(segments):
            if i not in used and (point in coords):
                return i
        return None
    for i, (name, coords) in enumerate(segments):
        if i in used:
            continue
        current_coords = coords[:]
        used.add(i)
        while True:
            start_point = current_coords[0]
            end_point = current_coords[-1]
            found = False
            for point in [start_point, end_point]:
                segment_index = find_segment_with_common_point(point)
                if segment_index is not None:
                    other_name, other_coords = segments[segment_index]
                    used.add(segment_index)
                    if point == start_point:
                        if other_coords[0] == point:
                            current_coords = other_coords[::-1] + current_coords[1:]
                        else:
                            current_coords = other_coords + current_coords[1:]
                    else:
                        if other_coords[-1] == point:
                            current_coords = current_coords[:-1] + other_coords[::-1]
                        else:
                            current_coords = current_coords[:-1] + other_coords
                    found = True
                    break
            if not found:
                break
        merged_segments.append(('Merged Segment', current_coords))
    return merged_segments

def create_kml(segments, output_filename):
    merged_segments = merge_segments(segments)
    with open(output_filename, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')
        for name, coords in merged_segments:
                f.write(f'<Placemark>\n<name>Rectangle {name}</name>\n<LinearRing>\n<coordinates>\n')
                f.write('\n'.join([f"{lon},{lat},0" for lon, lat, alt in coords]))
                f.write('\n</coordinates>\n</LinearRing>\n</Placemark>\n')
        f.write('</Document>\n</kml>')

def buffer_and_create_polygons(kml_filename):
    tree = etree.parse(kml_filename)
    root = tree.getroot()
    line_strings = []
    for placemark in root.findall(".//{http://www.opengis.net/kml/2.2}Placemark"):
        coordinates = placemark.find(".//{http://www.opengis.net/kml/2.2}coordinates").text.strip()
        coords_list = [tuple(map(float, coord.split(',')[:2])) for coord in coordinates.split()]
        line_strings.append(LineString(coords_list))
    buffer_distance = 0.000015
    rectangular_polygons = [line_string.buffer(buffer_distance, join_style='mitre',  cap_style='square') for line_string in line_strings]
    with open('output.kml', 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')
        for i, polygon in enumerate(rectangular_polygons):
            f.write(f'<Placemark>\n<name>Rectangle {i}</name>\n<Style>\n<LineStyle>\n<color>ff0000ff</color>\n<width>3</width>\n</LineStyle>\n<PolyStyle>\n<color>40ffffff</color>\n<fill>0</fill>\n</PolyStyle>\n</Style>\n<Polygon>\n<outerBoundaryIs>\n<LinearRing>\n<coordinates>\n')
            f.write('\n'.join([f'{point[0]},{point[1]},0' for point in polygon.exterior.coords]))
            f.write('\n</coordinates>\n</LinearRing>\n</outerBoundaryIs>\n</Polygon>\n</Placemark>\n')
        f.write('</Document>\n</kml>')

def parse_kml1(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}
    coordinates = []
    for placemark in root.findall('.//kml:Placemark', namespaces):
        for linestring in placemark.findall('.//kml:coordinates', namespaces):
            coords_text = linestring.text.strip()
            for coord in coords_text.split():
                lon, lat, _ = map(float, coord.split(','))
                coordinates.append((lon, lat))
    return coordinates

def create_boundary_kml(coords, output_file):
    line = Polygon(coords)
    outer_polygon = line.buffer(0.000015,join_style='mitre',  cap_style='square')
    inner_polygon = line.buffer(-0.000015,join_style='mitre',  cap_style='square')
    with open(output_file, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')
        f.write('<Placemark>\n<name>Resized Polygon</name>\n<Polygon>\n<outerBoundaryIs>\n<LinearRing>\n<coordinates>\n')
        f.write('\n'.join(f"{coord[0]},{coord[1]},0" for coord in outer_polygon.exterior.coords))
        f.write('\n</coordinates>\n</LinearRing>\n</outerBoundaryIs>\n<innerBoundaryIs>\n<LinearRing>\n<coordinates>\n')
        f.write('\n'.join(f"{coord[0]},{coord[1]},0" for coord in inner_polygon.exterior.coords))
        f.write('\n</coordinates>\n</LinearRing>\n</innerBoundaryIs>\n</Polygon>\n<Style>\n<LineStyle>\n<color>ff0000ff</color>\n<width>2</width>\n</LineStyle>\n<PolyStyle>\n<fill>0</fill>\n</PolyStyle>\n</Style>\n</Placemark>\n</Document>\n</kml>\n')

def format_kml_coordinates(file_path):
    with open(file_path, "r") as file:
        kml_data = file.read()
    coordinates = re.findall(r'<coordinates>(.*?)</coordinates>', kml_data, re.DOTALL)
    formatted_coordinates = ""
    for coordinate_set in coordinates:
        individual_coordinates = coordinate_set.strip().split('\n')
        for coordinate in individual_coordinates:
            lon, lat, _ = coordinate.strip().split(',')
            formatted_coordinates += f"{lat},{lon};"
        formatted_coordinates += "00.00000,00.00000;"
    formatted_coordinates = formatted_coordinates[:-19]
    return formatted_coordinates

