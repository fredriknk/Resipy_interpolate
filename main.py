import os
import sys
from libs import processdata,invertproject,plotting


if __name__ == '__main__':
    project_folder = "./Projects/Sara"
    gps_filename = "GPS_kordinater.xlsx"

    #make a list of all project folders
    folders = os.listdir(project_folder)

    for folder in folders:
        project_folder_name = f"{project_folder}/{folder}"
        print(f"wokring on {project_folder_name}")

        processdata.makeproject(project_folder_name, gps_filename)
        print(f"Starting 2d inversion for {project_folder_name}")
        invertproject.meshinvertPseudo3d(   project_folder=project_folder_name,
                                            project_name="Sara_datapseudo3d",
                                            show_outputs=True
                                            parrallel_processing=True )

        # invertproject.showpseudo3d(project_folder=project_folder_name)
        # plotting.showpseudo3d(project_folder=project_folder_name)
