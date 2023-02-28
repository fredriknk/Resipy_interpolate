import csv

def converter(file_name,save_name,add=5):
    # Open the file for reading and create a CSV reader
    with open(file_name, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=' ')

        # Open a new file for writing and create a CSV writer
        with open(save_name, 'w', newline='') as output_file:
            writer = csv.writer(output_file, delimiter=' ')

            # Loop through each row of the input file
            for lineno, row in enumerate(reader):
                # Check if the row has at least 8 columns
                print(lineno)
                if len(row) == 16 and lineno >8 :

                    # Write the updated row to the output file
                    row[2] = str(float(row[2]) + add)
                    row[5] = str(float(row[5]) + add)
                    row[8] = str(float(row[8]) + add)
                    row[11] = str(float(row[11]) + add)
                    writer.writerow(row)
                # If row doesnt have 16 columns, write it to the output file as is
                else:
                    writer.writerow(row)