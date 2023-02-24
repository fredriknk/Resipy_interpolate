# This is a sample Python scrip

import pandas as pd
from matplotlib import pyplot as plt
import matplotlib
import rasterio
import rasterio.plot
import utm
import math as m
from owslib.wms import WebMapService
import os
import wcs_lib

def make_string(df_):
    outstring = ""
    outstring += "topo\n4\n%i\n" % len(df_)
    outstring += df_[["X","Y","Z"]].to_string(header=False)
    outstring += "\ntopo\n0\n0\n0\n0\n"
    return outstring

def open_raster(filename="./geotiffs/data/dtm1_33_123_113.tif"):
    filename = "geodata/data/dtm1_33_125_115.tif"
    tiff = rasterio.open(filename)
    rasterio.plot.show(tiff, title=filename)

def download_wms_map(wms_url, layer_name, bbox, output_file):
    # Connect to the WMS server
    wms = WebMapService(wms_url, version='1.3.0')

    # Request the map cutout from the server
    img = wms.getmap(
        layers=[layer_name],
        srs='EPSG:4326',
        bbox=bbox,
        size=(256, 256),
        format='image/png',
        transparent=True
    ).read()

    with open(output_file, 'wb') as f:
        f.write(img)

def plot_geotiff(output_file):
    # Open the GeoTIFF using Rasterio
    with rasterio.open(output_file) as dataset:
        array = dataset.read(1)
        # Plot the raster data using Matplotlib
        plt.imshow(array)
        plt.show()

def show_line(df,ax):
    ax.plot(df["X"].values,df["Y"].values,df["Z"].values,label=sheet)

def poput_plot():
    matplotlib.use('TkAgg')

if __name__ == '__main__':
    # Define the inputs
    wms_url = 'https://wms.geonorge.no/skwms1/wms.hoyde-dom'
    layer_name = 'DOM'
    bbox = (10.73758, 60.22762, 10.74409, 60.23237)  # (minx, miny, maxx, maxy)
    output_file = f"{bbox[0]}-{bbox[1]}-{bbox[2]}-{bbox[3]}".replace(".","_")+".tif"

    # Download the map cutout
    print(f"check if exist:{output_file}")
    if not os.path.exists(output_file):
        print("File doesnt exits, downloading")
        download_wms_map(wms_url, layer_name, bbox, output_file)

    print("Plotting map")
    #plot_geotiff(output_file)
    with rasterio.open(output_file) as dataset:
        array = dataset.read(1)
    print("starting work")


def old_fun():
    make_3d_topo_file = True
    make_topo_files = True
    make_3d_topo_files = False

    poput_plot()

    filename_tiff = "geodata/data/dtm1_33_124_113.tif"  #MADS
    #filename_tiff = "geotiffs/data/dtm1_33_125_115.tif"#MALIN

    tiff = rasterio.open(filename_tiff)
    print(tiff.bounds)
    band1 = tiff.read(1)
    # excel_filename = "GPS_ert_mads.xlsx"
    excel_filename = "GPS_undervisning.xlsx"#"GPS_ERT.xlsx"
    xls = pd.ExcelFile(excel_filename)
    fig = plt.figure()
    # ax = plt.subplots(1,1)
    ax = plt.axes(projection="3d")
    i = 1
    df_app = pd.DataFrame()

    for sheet in xls.sheet_names[:]:
        print(sheet)
        df = pd.read_excel(xls, sheet)
        df.index = df["Elektrode nr"]

        df = df.reindex(range(1, df.index.max()+1)).interpolate(method='linear')

        latlon = utm.to_latlon(easting=df["X"], northing=df["Y"], zone_letter="N", zone_number=32)
        utm33 = utm.from_latlon(latitude = latlon[0], longitude =  latlon[1],force_zone_number=33,force_zone_letter="N")
        x,y = tiff.index(utm33[0], utm33[1])
        df["Z"] = band1[x,y]

        # df["Elektrode nr "] = df["Elektrode nr "] - 1
        df["Elektrode nr"] = (df["Elektrode nr"]).astype("int")
        df.index = df["Elektrode nr"]
        df[["dX","dY"]] = df[["X","Y"]].diff().fillna(0)
        df["X_"] = df.apply(lambda x: m.sqrt(x['dX']**2+ x['dY']**2), axis=1).cumsum()

        show_line(df, ax)

        if make_topo_files == True:
            stringtopo = make_string(df)
            df[["Elektrode nr","X_","Z"]].to_csv("./topofiles/topo" + sheet + ".csv",header=["label","X","Z"],index=False)

        if make_3d_topo_file == True:
            stringtopo = make_string(df)
            df[["Elektrode nr","X","Y","Z"]].to_csv("./topofiles/topo3d" + sheet + ".csv",header=["label","X","Y","Z"],index=False)
        df['label'] = df["Elektrode nr"].apply(lambda x: f"{i:n} {x:n}")
        i+=1

        df.index = df['label']

        df_app = pd.concat([df_app,df])

    xls.close()

    df_app.index = df_app['label']
    df_app["buried"] = 0
    df_app["x"] = df_app["X"]
    df_app["y"] = df_app["Y"]
    df_app["z"] = df_app["Z"]
    if make_3d_topo_files == True:
        df_app[["x", "y", "z","buried"]].to_csv("./topofiles/electrodes3d.csv")
    plt.show()