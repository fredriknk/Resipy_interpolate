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
    outstring += df_[["X", "Y", "Z"]].to_string(header=False)
    outstring += "\ntopo\n0\n0\n0\n0\n"
    return outstring


def open_raster(filename="./geotiffs/data/dtm1_33_123_113.tif"):
    filename = "geodata/data/dtm1_33_125_115.tif"
    tiff = rasterio.open(filename)
    rasterio.plot.show(tiff, title=filename)


def show_line(df, ax):
    ax.plot(df["X"].values, df["Y"].values, df["Z"].values, label=sheet)


def poput_plot():
    matplotlib.use('TkAgg')


if __name__ == '__main__':

    make_topo_files = True
    make_3d_topo_file = True

    excel_filename = "GPS_punkt_Slettebakken.xlsx"
    xls = pd.ExcelFile(excel_filename)
    xls.sheet_names[:1]
    for sheet in xls.sheet_names[:]:
        print(sheet)
        df = pd.read_excel(xls, sheet)

        if df.iloc[0]["Type"] == "declatlon":
            xy = utm.from_latlon(latitude=df.Y, longitude=df.X, force_zone_number=32, force_zone_letter="N")
            df.X = xy[0]
            df.Y = xy[1]

        if df.iloc[0]["Type"] == "utm33":
            latlon = utm.to_latlon(easting=df["X"], northing=df["Y"], zone_letter="N", zone_number=32)
            xy = utm.from_latlon(latitude=latlon[0], longitude=latlon[1], force_zone_number=33, force_zone_letter="N")
            df.X = xy[0]
            df.Y = xy[1]
        sc = 0.1
        X_max = df.X.max()
        X_min = df.X.min()
        Y_max = df.Y.max()
        Y_min = df.Y.min()

        framex = 20
        framey = 20

        bbox = (int(X_min - framex), int(Y_min - framey), int(X_max + framex), int(Y_max + framey))
        print(f"Area is {int(X_max + framex)-int(X_min - framex)}m in X, {int(Y_max + framey)- int(Y_min - framey)} m in Y, does this sound reasonable? Y/N")

        map_tiff, dtm_tiff = wcs_lib.get_data(bbox,resolution_map=0.2,png=False,DTM=False)
        dtm_tiff_band1 = dtm_tiff.read(1)

        fig, ax = plt.subplots(1, figsize=(12, 15))
        rasterio.plot.show((map_tiff,1), cmap='gray',alpha=0.9, ax=ax)
        rasterio.plot.show(dtm_tiff, contour=True,alpha=0.4, ax=ax)
        i=0
        for fn in df["File"].unique()[:]:
            df_ = df[df["File"] == fn]
            df_["Elektrode_"] =  df_["Elektrode"]+ 96 * i
            df_.index = df_["Elektrode_"]
            df_ = df_.reindex(range(df_.index.min(), df_.index.max() + 1)).interpolate(method='linear')
            df_[["dX", "dY"]] = df_[["X", "Y"]].diff().fillna(0)
            df_["X_"] = df_.apply(lambda x: m.sqrt(x['dX'] ** 2 + x['dY'] ** 2), axis=1).cumsum()
            df_["Z"] = dtm_tiff_band1[dtm_tiff.index(df_.X,df_.Y)]
            df_.fillna(method="ffill",inplace=True)
            ax.plot(df_.X.values,df_.Y.values,label=fn)

            if make_topo_files == True:
                stringtopo = make_string(df_)
                df_[["Elektrode", "X_", "Z"]].to_csv("./topofiles/topo" + fn + ".csv", header=["label", "X", "Z"],
                                                       index=False)

            if make_3d_topo_file == True:
                stringtopo = make_string(df_)
                df_[["Elektrode", "X", "Y", "Z"]].to_csv("./topofiles/topo3d" + fn + ".csv",
                                                           header=["label", "X", "Y", "Z"], index=False)
                if i ==0:
                    df_[["Elektrode_", "X", "Y", "Z"]].to_csv("./topofiles/topo3d_ALL.csv", header=["label", "X", "Y", "Z"],index=False)
                else:
                    df_[["Elektrode_", "X", "Y", "Z"]].to_csv("./topofiles/topo3d_ALL.csv", index=False, mode = 'a',header=False)
            i += 1
        ax.legend()
        fig.show()


def old_fun():
    make_3d_topo_file = True
    make_topo_files = True
    make_3d_topo_files = False

    poput_plot()

    filename_tiff = "geodata/data/dtm1_33_124_113.tif"  # MADS
    # filename_tiff = "geotiffs/data/dtm1_33_125_115.tif"#MALIN

    tiff = rasterio.open(filename_tiff)
    print(tiff.bounds)
    band1 = tiff.read(1)
    # excel_filename = "GPS_ert_mads.xlsx"
    excel_filename = "GPS_undervisning.xlsx"  # "GPS_ERT.xlsx"
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

        df = df.reindex(range(1, df.index.max() + 1)).interpolate(method='linear')

        latlon = utm.to_latlon(easting=df["X"], northing=df["Y"], zone_letter="N", zone_number=32)
        utm33 = utm.from_latlon(latitude=latlon[0], longitude=latlon[1], force_zone_number=33, force_zone_letter="N")
        x, y = tiff.index(utm33[0], utm33[1])
        df["Z"] = band1[x, y]

        # df["Elektrode nr "] = df["Elektrode nr "] - 1
        df["Elektrode nr"] = (df["Elektrode nr"]).astype("int")
        df.index = df["Elektrode nr"]
        df[["dX", "dY"]] = df[["X", "Y"]].diff().fillna(0)
        df["X_"] = df.apply(lambda x: m.sqrt(x['dX'] ** 2 + x['dY'] ** 2), axis=1).cumsum()

        show_line(df, ax)

        if make_topo_files == True:
            stringtopo = make_string(df)
            df[["Elektrode nr", "X_", "Z"]].to_csv("./topofiles/topo" + sheet + ".csv", header=["label", "X", "Z"],
                                                   index=False)

        if make_3d_topo_file == True:
            stringtopo = make_string(df)
            df[["Elektrode nr", "X", "Y", "Z"]].to_csv("./topofiles/topo3d" + sheet + ".csv",
                                                       header=["label", "X", "Y", "Z"], index=False)
        df['label'] = df["Elektrode nr"].apply(lambda x: f"{i:n} {x:n}")
        i += 1

        df.index = df['label']

        df_app = pd.concat([df_app, df])

    xls.close()

    df_app.index = df_app['label']
    df_app["buried"] = 0
    df_app["x"] = df_app["X"]
    df_app["y"] = df_app["Y"]
    df_app["z"] = df_app["Z"]
    if make_3d_topo_files == True:
        df_app[["x", "y", "z", "buried"]].to_csv("./topofiles/electrodes3d.csv")
    plt.show()
