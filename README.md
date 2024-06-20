# Resipy Interpolate

This script is for interpolating GPS positions for a ERT measurement and georeferencing each position to a DTM map

You will need to make an excel file with the following columns in the main folder of the project
You can copy the table and paste it in the excel file to get the format right:

| File         | Elektrode | X       | Y        | Type      |
|--------------|-----------|---------|----------|-----------|
| Filename 1   | 1         | 5.359254| 60.351705| declatlon |
| Filename 1   | 96        | 5.360976| 60.351511| declatlon |
| Filename 2   | 1         | 5.360526| 60.352193| UTM32     |
| Filename 2   | 96        | 5.360526| 60.352193| UTM32     |

The coordinates can be either utm32, utm33, or declatlon (decimal latlon). The script will convert all values to utm32
for calculations.

The filenames in the column  must be the same as the ERT files, but without the extension. The script will look for the 
files in the "syscal_files" folder.