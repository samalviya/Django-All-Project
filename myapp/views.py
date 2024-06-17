from django.shortcuts import render,redirect 
from .utils import find_smallest_number, find_largest_number, calculate_sum
import os
import xml.dom.minidom
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from .kml_script import parse_coordinates1, parse_kml1,merge_segments, create_boundary_kml, create_kml, parse_coordinates, create_kmal, buffer_and_create_polygons, format_kml_coordinates
import csv
from .forms import GeoTIFFForm,KMLUploadForm
from samgeo import tms_to_geotiff
from PIL import Image
import io
import base64
from django.conf import settings
import folium


def home(request):
    return render(request, 'home.html')

def smallest_number_view(request):
    output_data = None
    if request.method == 'POST':
        input_data = request.POST.get('input_data')
        try:
            numbers = list(map(int, input_data.split(',')))
            output_data = find_smallest_number(numbers)
        except ValueError:
            output_data = 'Invalid input. Please enter a comma-separated list of numbers.'
    return render(request, 'smallest_number.html', {'output_data': output_data})

def largest_number_view(request):
    output_data = None
    if request.method == 'POST':
        input_data = request.POST.get('input_data')
        try:
            numbers = list(map(int, input_data.split(',')))
            output_data = find_largest_number(numbers)
        except ValueError:
            output_data = 'Invalid input. Please enter a comma-separated list of numbers.'
    return render(request, 'largest_number.html', {'output_data': output_data})

def sum_view(request):
    output_data = None
    if request.method == 'POST':
        input_data = request.POST.get('input_data')
        try:
            numbers = list(map(int, input_data.split(',')))
            output_data = calculate_sum(numbers)
        except ValueError:
            output_data = 'Invalid input. Please enter a comma-separated list of numbers.'
    return render(request, 'sum.html', {'output_data': output_data})

def kml_view(request):
    result = None
    if request.method == 'POST':
        coordinates_str = request.POST.get('coordinates_str')
        try:
            segments = parse_coordinates1(coordinates_str)
            output_file = 'output.kml'
            create_kmal(segments, output_file)

            tree = ET.parse(output_file)
            root = tree.getroot()

            segments = []
            for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
                name = placemark.find('{http://www.opengis.net/kml/2.2}name').text
                coordinates = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.strip()
                parsed_coords = parse_coordinates(coordinates)
                segments.append((name, parsed_coords))

            create_kml(segments, output_file)

            doc = xml.dom.minidom.parse(output_file)
            coordinates_elements = doc.getElementsByTagName('coordinates')
            if not coordinates_elements:
                print("No coordinates found in the KML file.")
            
            coordinates_text = coordinates_elements[0].firstChild.nodeValue.strip()
            coords_list = coordinates_text.split()
            start_coords = coords_list[0]
            end_coords = coords_list[-1]

            if start_coords == end_coords:
                print("Polygon")
                coordinates = parse_kml1(output_file)
                create_boundary_kml(coordinates, output_file)
            else:
                print("LineString")
                buffer_and_create_polygons(output_file)

            with open(output_file, 'r') as kml_file:
                kml_data = kml_file.read()

            result = format_kml_coordinates(output_file)
       

        except Exception as e:
            result = f"An error occurred: {str(e)}"
            


    return render(request, 'kml.html', {'result': result})

def download_kml(request):
    kml_file_path = 'output.kml'
    if os.path.exists(kml_file_path):
        with open(kml_file_path, 'rb') as kml_file:
            response = HttpResponse(kml_file.read(), content_type='application/vnd.google-earth.kml+xml')
            response['Content-Disposition'] = 'attachment; filename="output.kml"'
            return response
    else:
        return HttpResponse("File not found", status=404)


def process_csv_view(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            return HttpResponse('File is not CSV type')

        # Ensure to open the CSV file in text mode and handle BOM
        csv_data = csv.DictReader(csv_file.read().decode('utf-8-sig').splitlines())
        
        rows = list(csv_data)
        for row in rows:
            plot_id = row["Plot Id"]
            coordinates_str = row["Final Polygon of farm"]

            segments = parse_coordinates1(coordinates_str)
            output_filename = f"{plot_id}.kml"
            create_kmal(segments, output_filename)

            tree = ET.parse(output_filename)
            root = tree.getroot()

            segments = []
            for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
                name = placemark.find('{http://www.opengis.net/kml/2.2}name').text
                coordinates = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.strip()
                parsed_coords = parse_coordinates(coordinates)
                segments.append((name, parsed_coords))

            merged_segments = merge_segments(segments)
            create_kml(merged_segments, output_filename)

            doc = xml.dom.minidom.parse(output_filename)
            coordinates_elements = doc.getElementsByTagName('coordinates')
            if not coordinates_elements:
                print(f"No coordinates found in the KML file for plot {plot_id}.")

            coordinates_text = coordinates_elements[0].firstChild.nodeValue.strip()
            coords_list = coordinates_text.split()
            start_coords = coords_list[0]
            end_coords = coords_list[-1]

            if start_coords == end_coords:
                print(f"Polygon for plot {plot_id}")
                coordinates = parse_kml1(output_filename)
                create_boundary_kml(coordinates, output_filename)
            else:
                print(f"LineString for plot {plot_id}")
                buffer_and_create_polygons(output_filename)

            formatted_coordinates = format_kml_coordinates(output_filename)
            row["Formatted Coordinates"] = formatted_coordinates

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="processed_data.csv"'

        # Write to the response CSV file
        fieldnames = csv_data.fieldnames + ["Formatted Coordinates"]
        csv_writer = csv.DictWriter(response, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(rows)

        return response

    return render(request, 'kml.html')

# views.py
def geotiff_view(request):
    if request.method == 'POST':
        form = GeoTIFFForm(request.POST)
        if form.is_valid():
            bbox = list(map(float, form.cleaned_data['bbox'].split(',')))
            zoom = form.cleaned_data['zoom']
            output = "satellite.tif"
            tms_to_geotiff(output, bbox, zoom, source="Satellite", overwrite=True)

            # Convert GeoTIFF to PNG for visualization
            with Image.open(output) as img:
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return render(request, 'geotiff_form.html', {
                'form': form,
                'image': img_base64,
                'output': output
            })
    elif request.method == 'GET' and 'download' in request.GET:
        output = "satellite.tif"
        with open(output, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/tiff')
            response['Content-Disposition'] = 'attachment; filename="satellite.tif"'
            return response
    else:
        form = GeoTIFFForm()
    return render(request, 'geotiff_form.html', {'form': form})



def convert_kml_to_html(kml_file, output_folder):
    latitudes = []
    longitudes = []

    # Initialize the folium map
    m = folium.Map(location=[0, 0], zoom_start=13,
                   tiles='http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                   attr='Google Satellite', name='Satellite',
                   max_native_zoom=20, max_zoom=20)

    # Parse KML file
    tree = ET.parse(kml_file)
    root = tree.getroot()

    features = []
    for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        geometry_element = placemark.find('.//{http://www.opengis.net/kml/2.2}Polygon') or placemark.find('.//{http://www.opengis.net/kml/2.2}LineString')
        if geometry_element is not None:
            coordinates = geometry_element.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.strip()
            coordinates = [list(map(float, coord.split(','))) for coord in coordinates.split()]

            description_element = placemark.find('.//{http://www.opengis.net/kml/2.2}description')
            description_text = description_element.text.strip() if description_element is not None else ''

            lats = [coord[1] for coord in coordinates]
            lons = [coord[0] for coord in coordinates]
            avg_lat = sum(lats) / len(lats)
            avg_lon = sum(lons) / len(lons)

            latitudes.append(avg_lat)
            longitudes.append(avg_lon)

            # Create a GeoJSON feature with a red border
            feature = {
                "type": "Feature",
                "properties": {
                    "description": description_text,
                    "color": "red"  # Change the border color to red
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                }
            }
            features.append(feature)

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    folium.GeoJson(
        geojson_data,
        style_function=lambda x: {"color": x["properties"]["color"]},  # Set border color
        tooltip=folium.GeoJsonTooltip(fields=['description'], labels=False) if any(feature["properties"].get("description") for feature in features) else None
    ).add_to(m)

    if latitudes and longitudes:
        map_center = [sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)]
        m.location = map_center
        
    folium.TileLayer(tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', attr='OpenStreetMap', name='OSM', max_native_zoom=20, max_zoom=20).add_to(m)
    folium.TileLayer(tiles='http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Normal', name='Normal', max_native_zoom=20, max_zoom=20).add_to(m)
    folium.TileLayer(tiles='http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid', name='Hybrid', max_native_zoom=20, max_zoom=20).add_to(m)

    folium.LayerControl().add_to(m)
    # Save the map
    map_file = os.path.join(output_folder, "plot_map.html")
    m.save(map_file)

    return map_file

def upload_kml(request):
    if request.method == 'POST':
        form = KMLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            kml_file = request.FILES['file']
            output_folder = os.path.join(settings.MEDIA_ROOT, 'kml_maps')
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            map_file = convert_kml_to_html(kml_file, output_folder)

            # Provide the map file for download
            download_url = f'/download/{os.path.basename(map_file)}'
            return redirect(f'/map_display/?map_url={settings.MEDIA_URL}kml_maps/{os.path.basename(map_file)}&download_url={download_url}')
    else:
        form = KMLUploadForm()

    return render(request, 'upload.html', {'form': form})

def map_display(request):
    map_url = request.GET.get('map_url')
    download_url = request.GET.get('download_url')
    return render(request, 'map_display.html', {'map_url': map_url, 'download_url': download_url})

def download_map(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, 'kml_maps', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/html')
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else:
        return HttpResponse("File not found")