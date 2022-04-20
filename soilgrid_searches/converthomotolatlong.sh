#!/usr/bin/env bash

gdalwarp -t_srs EPSG:4326 "soc_0-5cm_meanHomolosine.tif" 'soc_0-5cm_mean.tif'
