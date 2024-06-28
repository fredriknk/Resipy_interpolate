import csv
from resipy import Project
import time
import numpy as np



def meshinvert3d(project_folder = ".",
                syscal_folder = "syscal_files",
                topo_file = "topofiles\\topo3d_ALL.csv",
                surf_file = "topofiles\\surfaceplotxyz.csv",
                resipy_folder = "Resipy_project",
                project_name = "Resipy_datafilreal3d",
                project_type = "R3t",
                show_outputs=False,
                **kwargs):
    """
    This function is used to create a 3d mesh and invert it using resipy
    :param project_folder: The main folder where all the project files are located
    :param syscal_folder: The folder where the ert files are located
    :param topo_file: path to file containing the 3d topography
    :param surf_file: path to file containing the 3d surface
    :param resipy_folder: path to folder where the resipy project will be saved
    :param project_name: Name of the project
    :param project_type:
    :param kwargs:
    :return: none
    """
    project_name = f"{project_name}_{project_type}"

    syscal_folder = f"{project_folder}\\{syscal_folder}"
    topo_file = f"{project_folder}\\{topo_file}"
    surf_file = f"{project_folder}\\{surf_file}"
    resipy_folder = f"{project_folder}\\{resipy_folder}"

    k = Project(typ=project_type, dirname=resipy_folder)

    print("Importing_files")
    k.create3DSurvey(syscal_folder, lineSpacing=20, ftype="ResInv",**kwargs)
    print("All Files Imported\n")

    print("Importing 3d file")
    k.importElec(topo_file)
    print("3d file imported\n")
    #open csv as array from csv file and convert from string to float and skip first row

    print(f"Importing 3d surface file {surf_file}")
    file = csv.reader(open(surf_file, "r"), delimiter=",")
    surface = []
    for row in file:
        if row[0] != "x":
            surface.append([float(row[0]), float(row[1]), float(row[2])])
    surface =np.array(surface)

    print("3d surface file imported\n")

    print("Meshing")
    k.createMesh(typ="tetra", surface=surface, fmd=None, cl=-1.00, cl_factor=5.00, cln_factor=100000.00, refine=0, **kwargs)
    print("Meshing done,Showing mesh, look for meshwindow in app bar if it didnt pop up")
    if show_outputs:
        k.showMesh()
    print("Meshing done\n")

    print("Start Inversion with parralell processing")
    # k.param['b_wgt'] = 0.01
    k.invert(modErr=False, parallel=True, modelDOI=False)
    print("Finished inversion")
    if show_outputs:
        k.showResults( attr="Resistivity(log10)", edge_color="none", vmin=None, vmax=None, color_map="viridis", background_color=(0.8, 0.8, 0.8),pvslices=([], [], []), pvthreshold=None, pvdelaunay3d=False, pvgrid=True, pvcontour=[])

    datetimestring = time.strftime("%Y%m%d-%H%M%S")
    savefilename = f"{resipy_folder}\\{datetimestring}_{project_name}.resipy"
    k.saveProject(savefilename)

    return savefilename

def meshinvertPseudo3d(project_folder = ".",
                syscal_folder = "syscal_files",
                topo_file = "topofiles\\topo3d_ALL.csv",
                surf_file = "topofiles\\surfaceplotxyz.csv",
                resipy_folder = "Resipy_project",
                project_name = "Resipy_datafilreal3d",
                project_type = "R2",
                show_outputs=False,
                **kwargs):
    """
    This function is used to create a 3d mesh and invert it using resipy
    :param project_folder:
    :param syscal_folder:
    :param topo_file:
    :param surf_file:
    :param resipy_folder:
    :param project_name:
    :param project_type:
    :param kwargs:
    :return: none
    """
    project_name = f"{project_name}_{project_type}"

    syscal_folder = f"{project_folder}\\{syscal_folder}"
    topo_file = f"{project_folder}\\{topo_file}"
    surf_file = f"{project_folder}\\{surf_file}"
    resipy_folder = f"{project_folder}\\{resipy_folder}"

    k = Project(typ=project_type, dirname=resipy_folder)

    print("Importing_files")
    k.createPseudo3DSurvey(syscal_folder, lineSpacing=20, ftype="ResInv",**kwargs)
    print("All Files Imported\n")

    print("Importing 3d file")
    k.importPseudo3DElec(topo_file)
    print("3d file imported\n")

    print(f"Importing 3d surface file {surf_file}")
    file = csv.reader(open(surf_file, "r"), delimiter=",")
    surface = []
    for row in file:
        if row[0] != "x":
            surface.append([float(row[0]), float(row[1]), float(row[2])])
    surface =np.array(surface)

    print("3d surface file imported\n")

    print("Meshing")
    k.createMultiMesh(typ='trian', show_output=False, dump=None, runParallel=True)
    if show_outputs:
        print("Meshing done,Showing mesh, look for meshwindow in app bar if it didnt pop up")
        k.showPseudo3DMesh(cropMesh=True)
    print("Meshing done\n")

    print("Start Inversion with parralell processing")
    # k.param['b_wgt'] = 0.01
    k.invertPseudo3D(runParallel=True)
    print("Finished inversion")
    if show_outputs:
        k.showResults(index=-1, cropMesh=False, color_map='jet', vmin=0.8, vmax=4, cropMaxDepth=False, clipContour=False)

    datetimestring = time.strftime("%Y%m%d-%H%M%S")
    savefilename = f"{resipy_folder}\\{datetimestring}_{project_name}.resipy"
    k.saveProject(savefilename)

    return savefilename