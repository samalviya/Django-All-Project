from samgeo import tms_to_geotiff

bbox = [75.87039459422876,22.72440827407615,75.8712162352702,22.72387051478303]
output="satellite.tif"
zoom=20
tms_to_geotiff(output, bbox, zoom, source="Satellite", overwrite=True)