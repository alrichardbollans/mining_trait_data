#Download global global geotiff in Homolosine projection
#https://git.wur.nl/isric/soilgrids/soilgrids.notebooks/-/blob/master/markdown/webdav_from_bash.md
sg_url="/vsicurl?max_retry=3&retry_delay=1&list_dir=no&url=https://files.isric.org/soilgrids/latest/data"

gdal_translate \
    -co "TILED=YES" -co "COMPRESS=DEFLATE" -co "PREDICTOR=2" -co "BIGTIFF=YES" \
    $sg_url"/soc/soc_0-5cm_mean.vrt" \
    "soc_0-5cm_meanHomolosinebash.tif"
