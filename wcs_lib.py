from owslib.wcs import WebCoverageService
import rasterio
import rasterio.features
import rasterio.warp
import rasterio.plot
import matplotlib.pyplot as plt
from owslib.wms import WebMapService
from PIL import Image
import utm
import os


def get_wcs_contents(wcs_url):
    """
    Given a WCS URL, returns a list of its available coverages.
    """
    wcs = WebCoverageService(wcs_url, version='1.0.0')
    return list(wcs.contents)


def get_coverage_bounding_boxes(wcs_url, coverage_id):
    """
    Given a WCS URL and a coverage ID, returns the bounding boxes for that coverage.
    """
    wcs = WebCoverageService(wcs_url, version='1.0.0')
    return wcs[coverage_id].boundingboxes


def download_coverage_data(bbox, output_file=None, wcs_url='https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25832',
                           coverage_id='dtm_25832', resx=1, resy=1, output_crs='EPSG:25832', format_out='GeoTIFF'):
    """
    Given a WCS URL, a coverage ID, a set of coordinates, and output file path, downloads coverage data and saves it to disk.
    """
    wcs = WebCoverageService(wcs_url, version='1.0.0')

    # Set the bounding box for the coverage request

    # Get the coverage data
    data = wcs.getCoverage(identifier=coverage_id, bbox=bbox, format=format_out, resx=resx, resy=resy, crs=output_crs)

    # Write the data to disk
    if output_file != None:
        with open(output_file, 'wb') as f:
            f.write(data.read())

    return data.read()

def get_map_image(bbox, output_file,
                  resolution_map = 1,
                  layer_name='ortofoto',
                  link='https://wms.geonorge.no/skwms1/wms.nib?service=WMS&request=GetCapabilities',
                  size=None,
                  format='image/png'
                  ):
    # Connect to the WMS service
    layer_name = layer_name
    wms = WebMapService(link)

    # Define the bounding box and image size
    if size == None:
        size = (int(bbox[2] - bbox[0])/resolution_map,int(bbox[3] - bbox[1])/resolution_map)  # (width, height)

    # Get the map image
    img = wms.getmap(layers=[layer_name], srs='EPSG:25832', bbox=bbox, size=size, format=format, transparent=True)
    image = Image.open(img)
    image.save("geodata/tmpfile.png")
    dataset = rasterio.open("geodata/tmpfile.png")
    bands = [1, 2, 3]
    data = dataset.read(bands)
    transform = rasterio.transform.from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], data.shape[1], data.shape[2])
    crs = {'init': 'EPSG:25832'}

    with rasterio.open(output_file, 'w', driver='GTiff',
                       width=data.shape[1], height=data.shape[2],
                       count=3, dtype=data.dtype, nodata=0,
                       transform=transform, crs=crs) as dst:
        dst.write(data, indexes=bands)


def get_data(bbox, resolution_map=1,resolution_dtm=1,png=True, DTM=True):
    output_name = f"geodata/{bbox[0]}-{bbox[1]}-{bbox[2]}-{bbox[3]}".replace(".", "_")

    output_file_png = f"{output_name}-Res_{resolution_map}_WMS.tif"
    if not os.path.exists(output_file_png):
        print(f"Downloading MAP data from bounding box {bbox}")
        get_map_image(bbox, output_file_png,resolution_map)
    else:
        print(f"Data exists in: {output_file_png}")

    map_tiff = rasterio.open(output_file_png)
    # Display the image
    if png:
        print(f"show map: {output_file_png}")
        rasterio.plot.show(map_tiff)

    output_file_geotif = f"{output_name}-Res_{resolution_dtm}_WCS.tif"
    # Download the coverage data and save it to disk

    if not os.path.exists(output_file_geotif):
        print(f"Downloading DTM data from bounding box {bbox}")
        download_coverage_data(bbox, output_file_geotif,resx=resolution_dtm,resy=resolution_dtm)
    else:
        print(f"Data exists in: {output_file_geotif}")

    dtm_tiff = rasterio.open(output_file_geotif)

    # Plot the downloaded raster data
    if DTM:
        print(f"Plotting DTM data from: {output_file_geotif}")
        rasterio.plot.show(dtm_tiff)
    return map_tiff, dtm_tiff



def test_wcs():
    x = 593019.072
    y = 6616003.47
    width = 1024
    height = 1024

    bbox = (x, y, x + width, y + height)
    map_tiff,dtm_tiff = get_data(bbox)