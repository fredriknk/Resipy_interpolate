from resipy import Project
import numpy as np
import pandas as pd
import time
import matplotlib
import math
import pyvista as pv
import gemgis as gg
import rasterio

import os

if os.environ.get('DISPLAY', '') == '':
    print('No display found. Using non-interactive Agg backend.')
    matplotlib.use('Agg')
else:
    matplotlib.use("Qt5Agg")

import matplotlib.pyplot as plt

def floatRgb(mag, cmin, cmax):
    """ Return a tuple of floats between 0 and 1 for R, G, and B. """
    # Normalize to 0-1
    try: x = float(mag-cmin)/(cmax-cmin)
    except ZeroDivisionError: x = 0.5 # cmax == cmin
    blue  = min((max((4*(0.75-x), 0.)), 1.))
    red   = min((max((4*(x-0.25), 0.)), 1.))
    green = min((max((4*math.fabs(x-0.5)-1., 0.)), 1.))
    return red, green, blue

def rgb(mag, cmin, cmax):
    """ Return a tuple of integers, as used in AWT/Java plots. """
    red, green, blue = floatRgb(mag, cmin, cmax)
    return int(red*255), int(green*255), int(blue*255)

def strRgb(mag, cmin, cmax):
    """ Return a hex string, as used in Tk plots. """
    return "#%02x%02x%02x" % rgb(mag, cmin, cmax)



def get_file_name(project_folder, extension='.resipy'):
    # Correct the use of the extension in the filter
    files = [f for f in os.listdir(project_folder) if f.endswith(extension)]

    # Check if no files are found
    if not files:
        print(f"No files with extension {extension} found.")
        return None

    if len(files) > 1:
        print(f"Multiple {extension} files found, please select one:")
        for i, f in enumerate(files):
            print(f"{i}: {f}")
        index = int(input("Enter index of file to load: "))
    else:
        index = 0

    file = files[index]
    return file
def showpseudo3d(project_folder = ".",
                resipy_folder = "Resipy_project",
                map_folder = "geodata",
                project_type = "R2",
                show_outputs=False,
                **kwargs):

    plot_boundry = False
    plot_methane = False

    k = Project(typ=project_type)

    file = get_file_name(f"{project_folder}/{resipy_folder}", extension='.resipy')
    k.loadProject(f"{project_folder}/{resipy_folder}/{file}")

    file = get_file_name(f"{project_folder}/{map_folder}", extension='WCS.tif')
    mesh = gg.visualization.read_raster(path=f"{project_folder}/{map_folder}/{file}", nodata_val=0., name='Elevation [m]')

    dem = rasterio.open(f"{project_folder}/{map_folder}/{file}")
    band1 = dem.read(1)

    file = get_file_name(f"{project_folder}/{map_folder}", extension='WMS.tif')

    map = f"{project_folder}/{map_folder}/{file}"

    src = rasterio.open(map)
    sb = src.bounds
    array = src.read()
    array = np.moveaxis(array, 0, -1)
    texture = pv.numpy_to_texture(array)

    sargs = dict(fmt="%.0f", color='black')

    # bounds = [6.122e+05, 6.140e+05, 6.65101e+06, 6.6509e+06, 0, 1.760e+02]

    topo = mesh.warp_by_scalar(scalars="Elevation [m]", factor=1.0)
    topo = topo.clip('z', invert=False, origin=(0, 0, 0))
    # topo = topo.clip_box(bounds)
    topo = topo.texture_map_to_plane(origin=[sb.left, sb.bottom, 0],
                                     point_u=[sb.right, sb.bottom, 0],
                                     point_v=[sb.left, sb.top, 0],
                                     use_bounds=False, inplace=True)
    topo = topo.translate([0, 0, -10])

    ax = pv.Plotter()

    lines = []

    if plot_methane:

        excel_filename = "./Maps/borelogg.xlsx"

        xls = pd.ExcelFile(excel_filename)
        xls.sheet_names

        boundry_width = 13
        methane_line_width = 13

        fill_color = "#a39cba"
        boundry_color = fill_color
        garbage_color = "#f51302"

        methan_min = 0
        methan_max = 20000
        for sheet in xls.sheet_names[1:]:
            df = pd.read_excel(xls, sheet)
            borehole_x = df.x.loc[0]
            borehole_y = df.y.loc[0]

            df.x.fillna(value=borehole_x, inplace=True)
            df.y.fillna(value=borehole_y, inplace=True)
            df.metan = df.metan.interpolate(method='nearest').fillna(method="bfill")

            tiff_x, tiff_y = dem.index(borehole_x, borehole_y)
            df["Altitude"] = band1[tiff_x, tiff_y]
            df["Z"] = df["Altitude"] + df.dybde

            df["Index"] = sheet
            df["Name"] = sheet + " Test"
            df["dybde"] = df.dybde.max() - df.dybde.min()
            df.rename(columns={"x": "X", "y": "Y", "type": "formation", "dybde": "Depth"}, inplace=True)

            if plot_boundry:
                df_tmp = df[df.formation == 1]
                mesh = pv.Line((df_tmp.X.min(), df_tmp.Y.min(), df_tmp.Z.max()), (df_tmp.X.min(), df_tmp.Y.min(), df_tmp.Z.min()))
                ax.add_mesh(mesh, color=fill_color, line_width=boundry_width)

                df_tmp2 = df[df.formation == 2]
                if len(df_tmp2):
                    mesh = pv.Line((df_tmp.X.min(), df_tmp.Y.min(), df_tmp.Z.min()),
                                   (df_tmp.X.min(), df_tmp.Y.min(), df_tmp2.Z.max()))
                    ax.add_mesh(mesh, color=boundry_color, line_width=boundry_width)

                    mesh = pv.Line((df_tmp.X.min(), df_tmp.Y.min(), df_tmp2.Z.max()),
                                   (df_tmp.X.min(), df_tmp.Y.min(), df_tmp2.Z.min()))
                    ax.add_mesh(mesh, color=garbage_color, line_width=boundry_width)

            if plot_methane:
                X_ = df.X.loc[0]
                Y_ = df.Y.loc[0]
                Z_ = df.Z.loc[0]

                for i in df.index[1:]:
                    layer = df.loc[i]
                    X,Y,Z = layer.X,layer.Y,layer.Z
                    mesh = pv.Line((X_,Y_,Z_),(X,Y,Z))
                    ax.add_mesh(mesh, color=strRgb(layer.metan,methan_min,methan_max), line_width=methane_line_width)
                    X_,Y_,Z_ = X,Y,Z

        legend_entries = []

        legend_entries.append(['Fill', fill_color])
        legend_entries.append(['Garbage', garbage_color])
        ax.add_legend(legend_entries,size=(0.1, 0.1))

        xls.close()

    ax.add_mesh(topo, texture=texture)
    ax.set_background('white')
    ax.show_grid(color='black')
    # k.showPseudo3DMesh(cropMesh=True)

    k.showResults(index=-1, ax=ax, cropMesh=False, color_map='jet', vmin=0.8, vmax=4.1, cropMaxDepth=False, contour=True,
                  elec_color="k", elec_size=4., pvshow=True)