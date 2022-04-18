import os

# FOr installation see https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html
from osgeo import gdal
import pandas as pd
from pkg_resources import resource_filename

_inputs_path = resource_filename(__name__, 'inputs')

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')

_output_path = resource_filename(__name__, 'outputs')
if not os.path.isdir(_inputs_path):
    os.mkdir(_inputs_path)
if not os.path.isdir(_temp_outputs_path):
    os.mkdir(_temp_outputs_path)
if not os.path.isdir(_output_path):
    os.mkdir(_output_path)


# def get_maps(raster_file: str):
#     from owslib.wcs import WebCoverageService
#
#     wcs = WebCoverageService('http://maps.isric.org/mapserv?map=/map/phh2o.map',
#                              version='2.0.1')
#     cov_id = 'phh2o_0-5cm_mean'
#     ph_0_5 = wcs.contents[cov_id]
#     subsets = [('X', -1784000, -1140000), ('Y', 1356000, 1863000)]
#     crs = "http://www.opengis.net/def/crs/EPSG/0/152160"
#     response = wcs.getCoverage(
#         identifier=[cov_id],
#         crs=crs,
#         subsets=subsets,
#         resx=250, resy=250,
#         format=ph_0_5.supportedFormats[0])
#     with open(raster_file, 'wb') as file:
#         file.write(response.read())
#
#
# def plot_raster(raster_file: str):
#     import rasterio
#     ph = rasterio.open(raster_file, driver="GTiff")
#     from rasterio import plot
#     plot.show(ph, title='Mean pH between 0 and 5 cm deep in Senegal', cmap='gist_ncar')
#     pass


def download_soilgrid_global_homolosine(soilgrid_file: str, output_file: str):
    # Following https://git.wur.nl/isric/soilgrids/soilgrids.notebooks/-/blob/master/markdown/webdav_from_Python.md
    # e.g. soilgrid_file = 'nitrogen/nitrogen_0-5cm_mean.vrt'
    kwargs = {'format': 'GTiff', 'creationOptions': ["TILED=YES", "COMPRESS=DEFLATE", "PREDICTOR=2", "BIGTIFF=YES"]}

    ds = gdal.Translate(output_file,
                        '/vsicurl?max_retry=3&retry_delay=1&list_dir=no&url=https://files.isric.org/soilgrids/latest/data/' + soilgrid_file,
                        **kwargs)
    del ds


def convert_homolosine_to_latlong(homol_file: str, output_file: str):
    ds = gdal.Warp(output_file,
                   homol_file,
                   dstSRS='EPSG:4326')
    del ds


def main():
    # download_soilgrid_global_homolosine('nitrogen/nitrogen_0-5cm_mean.vrt', '/home/atp/Downloads/rasters/nitrogen_0-5cm_mean(Homolosine).tif')
    # convert_homolosine_to_latlong('/home/atp/Downloads/rasters/nitrogen_0-5cm_mean(Homolosine).tif',
    #                               '/home/atp/Downloads/rasters/nitrogen_0-5cm_mean.tif')
    # print('done nitrogen')
    # convert_homolosine_to_latlong('/home/atp/Downloads/rasters/phh2o_0-5cm_mean(Homolosine).tif',
    #                               '/home/atp/Downloads/rasters/phh2o_0-5cm_mean.tif')

    download_soilgrid_global_homolosine('soc/soc_0-5cm_mean.vrt', '/home/atp/Downloads/rasters/soc_0-5cm_mean(Homolosine).tif')
    print('Downloaded')
    # convert_homolosine_to_latlong('/home/atp/Downloads/rasters/soc_0-5cm_mean(Homolosine).tif',
    #                               '/home/atp/Downloads/rasters/soc_0-5cm_mean.tif')


if __name__ == '__main__':
    main()
