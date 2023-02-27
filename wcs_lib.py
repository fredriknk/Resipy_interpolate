from owslib.wcs import WebCoverageService
import rasterio
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
                           coverage_id='dtm_25832', resx=2, resy=2, output_crs='EPSG:25832', format_out='GeoTIFF'):
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


def plot_raster_from_file(file_path):
    """
    Given a file path, plots the raster data using matplotlib.
    """
    with rasterio.open(file_path) as src:
        # Read the raster data as a NumPy array
        raster_data = src.read(1)

        # Get the spatial transform for the raster data
        transform = src.transform

    # Plot the raster data using matplotlib
    plt.imshow(raster_data, cmap='gray')
    plt.show()


def get_map_image(bbox, output_file=None, layer_name='ortofoto',
                  link='https://wms.geonorge.no/skwms1/wms.nib?service=WMS&request=GetCapabilities', size=None,
                  format='image/png'):
    # Connect to the WMS service
    layer_name = layer_name
    wms = WebMapService(link)

    # Define the bounding box and image size
    if size == None:
        size = (bbox[2] - bbox[0], bbox[3] - bbox[1])  # (width, height)

    # Get the map image
    img = wms.getmap(layers=[layer_name], srs='EPSG:25832', bbox=bbox, size=size, format=format, transparent=True)

    # Load the image using Pillow
    image = Image.open(img)

    if output_file != None:
        image.save(output_file)

    # Return the image object
    return image


def test_wcs():
    x = 593019.072
    y = 6616003.47
    width = 1024
    height = 1024

    bbox = (x, y, x + width, y + height)

    output_name = f"geodata/{bbox[0]}-{bbox[1]}-{bbox[2]}-{bbox[3]}".replace(".", "_")
    output_file_geotif = output_name + ".tif"
    # Download the coverage data and save it to disk
    if not os.path.exists(output_file_geotif):
        print(f"Downloading DTM data from bounding box {bbox}")
        download_coverage_data(bbox, output_file_geotif)
    else:
        print(f"Data exists in: {output_file_geotif}")

    # Plot the downloaded raster data
    print(f"Plotting DTM data from: {output_file_geotif}")
    plot_raster_from_file(output_file_geotif)

    output_file_png = output_name + ".png"
    if not os.path.exists(output_file_png):
        print(f"Downloading MAP data from bounding box {bbox}")
        image = get_map_image(bbox, output_file_png)
    else:
        print(f"Data exists in: {output_file_png}")
        image = Image.open(output_file_png)
    # Display the image
    print(f"show map: {output_file_png}")
    image.show()
