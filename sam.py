import leafmap
from samgeo import SamGeo, tms_to_geotiff, get_basemaps
import matplotlib.pyplot as plt

# Define the center coordinates
sam = (22.579320627819012, 77.64324672112707)

# Create a Leafmap map centered on `sam` with zoom level 19
m = leafmap.Map(center=sam, zoom=19)

# Add a satellite basemap
m.add_basemap("SATELLITE")

# Display the map
m.to_html(outfile="mymap.html", title="My Leafmap")
if m.user_roi_bounds() is not None:
    bbox = m.user_roi_bounds()
else:
    bbox = [22.713943, 76.027757, 22.813943, 76.127757]

tms_to_geotiff(output="satellite.tif", bbox=bbox, zoom=20, source="Satellite", overwrite=True)

image = Image.open("/content/satellite.tif")
plt.figure(figsize=(10, 10))
plt.imshow(image)
plt.axis('off')