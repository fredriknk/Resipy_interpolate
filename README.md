# Resipy Interpolate
## IMPORTANT
Because of resipy dependency hell, use python version 3.8 and install dependencies using pip install -r requirements.txt. You can try other solutions if you want, but its the only one ive found which reliably works.
## Description
This script is for interpolating GPS positions for a ERT measurement and georeferencing each position to a DTM map. 
Then it creates a resipy psuedo3d project and premesh is.

You will need to make an excel file with the following columns in the main folder of the project
You can copy the table and paste it in the excel file to get the format right:

| File         | Elektrode | X       | Y        | Type      |
|--------------|-----------|---------|----------|-----------|
| Filename 1   | 1         | 5.359254| 60.351705| declatlon |
| Filename 1   | 96        | 5.360976| 60.351511| declatlon |
| Filename 2   | 1         | 5.360526| 60.352193| UTM32     |
| Filename 2   | 96        | 5.360526| 60.352193| UTM32     |

The coordinates can be either utm32, utm33, or declatlon (decimal latlon). The script will convert all values to utm32
for calculations. The script will also interpolate the positions between intermidiatry electrodes.
The filenames in the column  must be the same as the ERT files, but without the extension. The script will look for the 
files in the "syscal_files" folder and generate a 3d and 2d topo file for each file in the "topo_files" folder. and a combined 
"topo3d_ALL" which is used in the batch conversion 

## Usage
i would reccomend using docker to run the script, but you can also run it on your local machine.

### Docker
To run the script in docker, you will need to build the docker image first. You can do this by running the following command in the project folder:
```bash
docker build -t resipy_interpolate .
```
Then you can run the script by running the following command:
```bash
docker run -it --rm --name resipy_interpolate -v ${PWD}:/app resipy_interpolate
```


### PyVista 3D view Controls:
 - Left Mouse moves the camera around the focus point
 - CTRL Left Mouse spins the camera around its view plane normal
 - SHIFT Left Mouse pans the camera
 - Middle mouse button pans the camera
 - CTRL SHIFT Left Mouse zooms the camera
 - Right mouse button Zooms the camera