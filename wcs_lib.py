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
import xml.etree.ElementTree as ET
import requests


def get_wcs_contents(wcs_url="https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25832?service=wcs&request=getcapabilities"):
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


def process_image_response(response):
    try:
        # Assuming response.content contains the byte stream or XML error
        if response.content.startswith(b'<?xml'):
            # Parse the XML content
            root = ET.fromstring(response.content)
            namespace = {'ogc': 'http://www.opengis.net/ogc'}

            # Extract error code and message
            exception = root.find('ogc:ServiceException', namespace)
            if exception is not None:
                error_code = exception.attrib.get('code', 'UnknownCode')
                error_message = exception.text.strip() if exception.text else 'UnknownError'

                # Raise an exception with the extracted information
                raise Exception(f"Error {error_code}: {error_message}")

        # If it's not an XML error, return the byte stream
        return response.content
    except ET.ParseError:
        raise Exception("Failed to parse the error response")

def download_coverage_data(bbox, output_file='downloaded_geotiff.tif',
                           wcs_url="https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25832?",
                           coverage_id='nhm_dtm_topo_25832_skyggerelieff', resx=10, resy=10,
                           output_crs='EPSG:25832', format_out='GeoTIFF'):
    """
    Download coverage data from a WCS service and save it to a GeoTIFF file.

    :param bbox: Bounding box for the area of interest, format: (xmin,ymin,xmax,ymax).
    :param output_file: The file path where the GeoTIFF will be saved.
    :param wcs_url: Base URL of the WCS service.
    :param coverage_id: nhm_dtm_topo_25832_skyggerelieff or nhm_dtm_topo_25832
    :param resx: Resolution in x-direction.
    :param resy: Resolution in y-direction.
    :param output_crs: Coordinate reference system for the output.
    :param format_out: Format of the output file.
    """

    bbox = ','.join(map(str, bbox))  # Convert the bbox to a comma-separated string
    print(f"Downloading coverage data for bbox: {bbox}...")
    # Construct the full WCS request URL
    get_coverage_url = (f"{wcs_url}SERVICE=WCS&VERSION=1.0.0&REQUEST=GetCoverage&"
                        f"COVERAGE={coverage_id}&CRS={output_crs}&BBOX={bbox}&"
                        f"RESX={resx}&RESY={resy}&FORMAT={format_out}")

    # Make the request
    response = requests.get(get_coverage_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Write the response content to a file
        process_image_response(response)
        with open(output_file, "wb") as file:
            file.write(response.content)
        print("GeoTIFF downloaded successfully.")
    else:
        print("Failed to download GeoTIFF:", response.status_code)

def get_map_image(bbox, output_file,
                  resolution_map =0.5,
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
    x = 593019.1
    y = 6616003
    width = 1024
    height = 1024

    bbox = (x, y, x + width, y + height)

    map_tiff,dtm_tiff = get_data(bbox)

def test_orto():
    x = 593019.072
    y = 6616003.47
    width = 10
    height = 10

    bbox = (x, y, x + width, y + height)
    get_map_image(bbox,"geodata/test.png",resolution_map=0.2)

if __name__ == '__main__':
    test_wcs()