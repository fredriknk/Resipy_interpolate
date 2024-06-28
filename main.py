import os
import sys
from libs import processdata
from libs import invertproject


if __name__ == '__main__':
    project_folder = "./Projects/Sara"
    gps_filename = "GPS_kordinater.xlsx"
    processdata.make_all_projects( project_folder=project_folder,
                                   gps_filename=gps_filename,
                                   user_input=False)
    print("Done")

    #make a list of all project folders
    folders = os.listdir(project_folder)

    for folder in folders:
        project_folder_name = f"{project_folder}/{folder}"
        print(f"wokring on {project_folder_name}")
        try:
            print(f"Starting 2d inversion for {project_folder_name}")
            invertproject.meshinvertPseudo3d(   project_folder=project_folder_name,
                                                project_name="Sara_datapseudo3d",
                                                show_outputs=False)
        except:
            print(f"2d inversion failed for {project_folder_name}")
            pass

        try:
            invertproject.meshinvert3d( project_folder=project_folder_name,
                                        project_name="Sara_datafilreal3d",
                                        project_type="R3t",
                                        show_outputs=False)
        except:
            print(f"3d inversion failed for {project_folder_name}")
            pass