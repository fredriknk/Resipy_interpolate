# This is a sample Python scrip
import time

import pandas as pd
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import rasterio
import rasterio.plot
import utm
import math as m
if __name__ != '__main__':
    from . import wcs_lib
else:
    import wcs_lib
import sys
import csv
import os


def contains_substring(substring, array):
    """
    Check if the substring is part of any string in the array.

    Parameters:
    - substring (str): The substring to search for.
    - array (list of str): The array of strings to search within.

    Returns:
    - bool: True if substring is found in any string of the array, otherwise False.
    """
    for item in array:
        if substring in item:
            return True
    return False


def make_string(df_):
    outstring = ""
    outstring += "topo\n4\n%i\n" % len(df_)
    outstring += df_[["X", "Y", "Z"]].to_string(header=False)
    outstring += "\ntopo\n0\n0\n0\n0\n"
    return outstring


def open_raster(filename="./geotiffs/data/dtm1_33_123_113.tif"):
    tiff = rasterio.open(filename)
    rasterio.plot.show(tiff, title=filename)


def show_line(df, ax):
    ax.plot(df["X"].values, df["Y"].values, df["Z"].values, label=sheet)


def poput_plot():
    matplotlib.use('TkAgg')


def calculate_bounding_box(x_min, y_min, x_max, y_max, frame_x, frame_y):
    return (int(x_min - frame_x), int(y_min - frame_y), int(x_max + frame_x), int(y_max + frame_y))


def print_area_dimensions(x_min, y_min, x_max, y_max, frame_x, frame_y):
    area_x = int(x_max + frame_x) - int(x_min - frame_x)
    area_y = int(y_max + frame_y) - int(y_min - frame_y)
    print(f"Area is {area_x}m in X, {area_y}m in Y, does this sound reasonable? Y/N")


def main(project_folder=".\\Projects\\Example",
         excel_filename="GPS_kordinater.xlsx",
         **kwargs):
    """
    Main function to process the excel file and perform various operations based on the parameters.

    Parameters:
    project_folder (str): The path to the project folder.
    gps_filename (str): The name of the GPS data file.
    make_topo_files (bool): If True, creates resipy topo files. Default is True.
    make_3d_topo_file (bool): If True, creates resipy 3D topo files. Default is True.
    download_maps (bool): If True, downloads maps. Default is True.
    frame_x (int): The frame size expand in the x+/- direction. Default is 20.
    frame_y (int): The frame size expand in the y+/- direction. Default is 20.
    query_user (bool): If True, queries the user for approving map download size. Default is False.
    plot (bool): If True, plots overview data. Default is False.
    png_filename (str): The name of map geotiff if you have one. Default is None.
    DTM_filename (str): The name of the DTM geotiff file if you have one. Default is None.
    resolution_map (float): The resolution of the sattelite image for download. Default is 0.5.
    resolution_dtm (float): The resolution of the DTM image for download. Default is 1.
    Returns:

    Returns:
    dtm_tiff: The digital terrain model as a tiff file.
    map_tiff: The map as a tiff file.
    df: The processed DataFrame with x,y,z coordinates.
    """

    # Set default values or override them with kwargs
    make_topo_files = kwargs.get('make_topo_files', True)
    make_3d_topo_file = kwargs.get('make_3d_topo_file', True)
    download_maps = kwargs.get('download_maps', True)
    frame_x = kwargs.get('frame_x', 20)
    frame_y = kwargs.get('frame_y', 20)
    query_user = kwargs.get('query_user', False)
    plot = kwargs.get('plot', False)
    png_filename = kwargs.get('png_filename', None)
    DTM_filename = kwargs.get('DTM_filename', None)
    resolution_map = kwargs.get('resolution_map', 0.5)
    resolution_dtm = kwargs.get('resolution_dtm', 1)

    plt.ioff()
    print(f"Processing project in folder: {project_folder} with GPS data file: {excel_filename}")
    xls = pd.ExcelFile(f"{project_folder}\\{excel_filename}")
    for sheet in xls.sheet_names[:]:
        print(sheet)
        df = pd.read_excel(xls, sheet)
        files_in_folder = os.listdir(f"{project_folder}\\syscal_files")
        #Select only files in the df which exists in the syscal files folder using the ontains_substring(fn, files_in_folder):
        df = df[df["File"].apply(lambda x: contains_substring(x, files_in_folder))]

        if df.iloc[0]["Type"] == "declatlon":
            xy = utm.from_latlon(latitude=df.Y, longitude=df.X, force_zone_number=32, force_zone_letter="N")
            df.X = xy[0]
            df.Y = xy[1]

        if df.iloc[0]["Type"] == "utm33":
            latlon = utm.to_latlon(easting=df["X"], northing=df["Y"], zone_letter="N", zone_number=33)
            xy = utm.from_latlon(latitude=latlon[0], longitude=latlon[1], force_zone_number=32, force_zone_letter="N")
            df.X = xy[0]
            df.Y = xy[1]

        sc = 0.1
        x_max = df.X.max()
        x_min = df.X.min()
        y_max = df.Y.max()
        y_min = df.Y.min()

        bbox = (int(x_min - frame_x), int(y_min - frame_y), int(x_max + frame_x), int(y_max + frame_y))
        print(
            f"Area is {int(x_max + frame_x) - int(x_min - frame_x)}m in X, {int(y_max + frame_y) - int(y_min - frame_y)} m in Y, does this sound reasonable? Y/N")

        if query_user:
            answer = input()
            if answer == "N":
                sys.exit()

        fig, ax = plt.subplots(1, figsize=(15, 11))
        fig2, ax2 = plt.subplots(1, figsize=(15, 11))
        ax2.axis('equal')
        print(f"project_folder1: {project_folder}")
        if download_maps:
            print(f"Downloading maps with resolution: {resolution_map} and DTM with resolution: {resolution_dtm}")
            map_tiff, dtm_tiff = wcs_lib.get_data(bbox,
                                                  f"{project_folder}\\geodata",
                                                  resolution_map=resolution_map,
                                                  resolution_dtm=resolution_dtm,
                                                  png=False,
                                                  DTM=False,
                                                  png_filename=None,
                                                  DTM_filename=None
                                                  )
            dtm_tiff_band1 = dtm_tiff.read(1)

            rasterio.plot.show((map_tiff, 1), cmap='gray', alpha=0.9, ax=ax)
            rasterio.plot.show(dtm_tiff, contour=True, alpha=0.4, ax=ax)
        print(f"project_folder2: {project_folder}")
        i = 1
        last_electrode = 0

        for fn in df["File"].unique()[:]:
            df_ = df[df["File"] == fn]
            df_.index = df_["Elektrode"]
            df_ = df_.reindex(range(df_.index.min(), df_.index.max() + 1)).interpolate(method='linear')

            df_["i"] = str(i) + " "
            df_["Elektrode_"] = df_["i"] + df_["Elektrode"].map('{:.0f}'.format)
            df_[["dX", "dY"]] = df_[["X", "Y"]].diff().fillna(0)
            df_["X_"] = df_.apply(lambda x: m.sqrt(x['dX'] ** 2 + x['dY'] ** 2), axis=1).cumsum()

            if download_maps:
                df_["Z"] = dtm_tiff_band1[dtm_tiff.index(df_.X, df_.Y)]
            else:
                df_["Z"] = 0

            df_.fillna(method="ffill", inplace=True)

            ax2.plot(df_["X_"], df_["Z"], label=fn, linewidth=2)

            ax.plot(df_.X.values, df_.Y.values, label=fn, linewidth=2)
            label_x = df_.X.values[-1]
            label_y = df_.Y.values[-1]
            ax.annotate(fn, (label_x, label_y), textcoords="offset points", xytext=(5, 5), ha='left', color="blue")

            if make_topo_files:
                stringtopo = make_string(df_)
                df_[["Elektrode", "X_", "Z"]].to_csv(f"{project_folder}\\topofiles\\topo" + fn + ".csv",
                                                     header=["label", "X", "Z"],
                                                     index=False)
            if make_3d_topo_file:
                stringtopo = make_string(df_)
                df_[["Elektrode", "X", "Y", "Z"]].to_csv(f"{project_folder}\\topofiles\\topo3d" + fn + ".csv",
                                                         header=["label", "X", "Y", "Z"], index=False)
                if i == 1:
                    df_[["Elektrode_", "X", "Y", "Z"]].to_csv(f"{project_folder}\\topofiles\\topo3d_ALL.csv",
                                                              header=["label", "x", "y", "z"], index=False)
                else:
                    df_[["Elektrode_", "X", "Y", "Z"]].to_csv(f"{project_folder}\\topofiles\\topo3d_ALL.csv",
                                                              index=False, mode='a',
                                                              header=False)
            i += 1

        if plot:
            #ax.legend()
            fig.show()
            ax2.legend()
            fig2.show()
        else:
            fig.savefig(f"{project_folder}\\Overview.png")
            ax2.legend()
            fig2.savefig(f"{project_folder}\\profiles.png")
            plt.close(fig)
            plt.close(fig2)

        return dtm_tiff, map_tiff, df


def export_geotiff_to_csv(dtm_tiff, output_csv_path):
    """
    Extracts data from a GeoTIFF file and writes x, y, z coordinates to a CSV file.

    Parameters:
    - geotiff_path (str): Path to the GeoTIFF file.
    - output_csv_path (str): Path where the CSV file will be saved.

    This function reads the first band of the GeoTIFF file to extract elevation data (or other raster data),
    computes the geographical coordinates for each pixel, and writes the x, y, and z values to a CSV file.
    Each row in the CSV represents a pixel, with 'x' and 'y' being the geographical coordinates and 'z' being the pixel value.
    """
    data = dtm_tiff.read(1)
    # Get the transformation object
    transform = dtm_tiff.transform

    # Prepare to write to CSV
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['x', 'y', 'z']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        # Generate x, y coordinates for each pixel and write to CSV
        for row in range(data.shape[0]):  # iterate over rows (height)
            for col in range(data.shape[1]):  # iterate over columns (width)
                # Convert pixel coordinates (col, row) to geographical coordinates (x, y)
                x, y = transform * (col, row)

                # Get the pixel value (z-value)
                z = data[row, col]

                # Write to CSV
                writer.writerow({'x': x, 'y': y, 'z': z})


def ensure_folders_exist(base_dir, folders):
    """
    Ensures that specified folders exist within a given base directory. If any folder does not exist, it creates it.

    Parameters:
    - base_dir (str): The path to the base directory where folders are to be checked or created.
    - folders (list of str): A list of folder names that should exist within the base directory.

    This function iterates through the list of folders and checks if each one exists within the base directory.
    If a folder does not exist, it is created.
    """
    print(f"Ensuring folders exist in: {base_dir},with folders: {folders}")

    for folder in folders:
        # Construct the full path to the folder
        folder_path = os.path.join(base_dir, folder)

        # Check if the folder exists
        if not os.path.exists(folder_path):
            # Create the folder if it does not exist
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")


#include all sub
def makeproject(project_folder,
                gps_filename,
                **kwargs):
    """
    Creates a project by ensuring necessary folders exist, processing the GPS data, downloading
    and exporting the GeoTIFF data as geotiffs, and converts it to a CSV file readable
    by resipy.

    Parameters:
    project_folder (str): The path to the project folder.
    gps_filename (str): The name of the GPS data file.
    *kwargs: Additional keyword arguments to pass to the main

    Returns:
    dtm_tiff: The digital terrain model as a rasterio file.
    map_tiff: The map as a rasterio file.
    df: The processed DataFrame with x,y,z coordinates.
    """
    print(f"Creating project in folder: {project_folder} with GPS data file: {gps_filename}")
    ensure_folders_exist(project_folder, folders=["syscal_files", "topofiles", "Resipy_project", "geodata"])
    #if syscal folders are empty, then throw error and exit
    if not os.listdir(f"{project_folder}\\syscal_files"):
        print(f"Error: No files in {project_folder}\\syscal_files ! Remember to add files to the folder.")
        sys.exit(1)

    #if gps file is not found, then throw error and exit
    if not os.path.exists(f"{project_folder}\\{gps_filename}"):
        print(f"Error: GPS file {gps_filename} not found in {project_folder}! Remember to add a gps file to the project folder")
        sys.exit(1)

    dtm_tiff, map_tiff, df = main(project_folder=project_folder,
                                  excel_filename=f"{gps_filename}",
                                  **kwargs)
    export_geotiff_to_csv(dtm_tiff, output_csv_path=f"{project_folder}\\topofiles\\surfaceplotxyz.csv")
    return dtm_tiff, map_tiff, df


def make_all_projects(project_folder, gps_filename, **kwargs):
    for subproject in os.listdir(project_folder):
        makeproject(f"{project_folder}\\{subproject}", gps_filename, )


if __name__ == '__main__':
    project_folder = "..\\Projects\\Example"
    gps_filename = "GPS_kordinater.xlsx "
    makeproject(project_folder, gps_filename, resolution_map=1., resolution_dtm=1.)

