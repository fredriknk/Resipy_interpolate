# This is a sample Python scrip

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import axes3d
import matplotlib
import rasterio
import rasterio.plot
import utm

# matplotlib.use('TkAgg')

def make_string(df_):
    outstring = ""
    outstring += "topo\n4\n%i\n" % len(df_)
    outstring += df_[["X","Y","Z"]].to_string(header=False)
    outstring += "\ntopo\n0\n0\n0\n0\n"
    return outstring

def open_raster(filename="./geotiffs/data/dtm1_33_123_113.tif"):
    filename = "geotiffs/data/dtm1_33_125_115.tif"
    tiff = rasterio.open(filename)
    rasterio.plot.show(tiff, title=filename)

make_topo_files = True

if __name__ == '__main__':
    """UTM 32 to UTM33 converter"""
    filename = "geotiffs/data/dtm1_33_125_115.tif"
    tiff = rasterio.open(filename)
    band1 = tiff.read(1)
    excel_filename = "KORRIGERT_GPS_MH.xlsx"#"GPS_ERT.xlsx"
    xls = pd.ExcelFile(excel_filename)
    i = 2
    # fig = plt.figure()
    # ax = plt.axes(projection="3d")
    i = 1
    df_app = pd.DataFrame()
    for sheet in xls.sheet_names[:]:
        print(sheet)
        df = pd.read_excel(xls,sheet)
        df.index = df["Elektrode nr "]


        df = df.reindex(range(1, df.index.max()+1)).interpolate(method='linear')
        # df["Elektrode nr "] = df["Elektrode nr "] - 1

        # df = df.iloc[0]
        latlon = utm.to_latlon(easting=df["X"], northing=df["Y"], zone_letter="N", zone_number=32)
        utm33 = utm.from_latlon(latitude = latlon[0], longitude =  latlon[1],force_zone_number=33,force_zone_letter="N")
        x,y = tiff.index(utm33[0], utm33[1])
        df["Z"] = band1[x,y]

        # df["Elektrode nr "] = df["Elektrode nr "] - 1
        df["Elektrode nr "] = (df["Elektrode nr "]).astype("int")
        df.index = df["Elektrode nr "]

        if make_topo_files == True:
            stringtopo = make_string(df)
            df[["X", "Y", "Z"]].to_csv("./topofiles/topo" + sheet + ".csv")

        df['label'] = df["Elektrode nr "].apply(lambda x: f"{i:n} {x:n}")
        i+=1

        df.index = df['label']


        df_app = df_app.append(df)
    xls.close()
    df_app.index = df_app['label']
    df_app["buried"] = 0
    df_app["x"] = df_app["X"]
    df_app["y"] = df_app["Y"]
    df_app["z"] = df_app["Z"]
    df_app[["x", "y", "z","buried"]].to_csv("./topofiles/electrodes3d.csv")
