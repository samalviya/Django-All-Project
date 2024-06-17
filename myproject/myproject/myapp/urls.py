from django.urls import path
from .views import home,process_csv_view, geotiff_view, smallest_number_view, largest_number_view, sum_view, kml_view, download_kml

urlpatterns = [
    path('', home, name='home'),
    path('smallest_number/', smallest_number_view, name='smallest_number'),
    path('largest_number/', largest_number_view, name='largest_number'),
    path('sum/', sum_view, name='sum'),
    path('kml/', kml_view, name='kml'),
    path('download_kml/', download_kml, name='download_kml'),
    path('process-csv/', process_csv_view, name='process_csv'),
    path('generate-geotiff/', geotiff_view, name='generate_geotiff'),
]
