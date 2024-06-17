from django.urls import path
from .views import home,process_csv_view,map_display, download_map,geotiff_view, smallest_number_view, largest_number_view, sum_view, kml_view, download_kml,upload_kml
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import map_display
urlpatterns = [
    path('', home, name='home'),
    path('smallest_number/', smallest_number_view, name='smallest_number'),
    path('largest_number/', largest_number_view, name='largest_number'),
    path('sum/', sum_view, name='sum'),
    path('kml/', kml_view, name='kml'),
    path('download_kml/', download_kml, name='download_kml'),
    path('process-csv/', process_csv_view, name='process_csv'),
    path('generate-geotiff/', geotiff_view, name='generate_geotiff'),
    path('upload/', upload_kml, name='upload_kml'),
    path('map_display/', map_display, name='map_display'),
    path('download/<str:file_name>/', download_map, name='download_map'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)