import os
import csv


rootdir = "C:\\Users\\fishmand\\Desktop\\dump"


# open the csv we want to write to
with open(os.path.join(rootdir, "row_by_col.csv"), 'w') as csv_write_file:
    csv_writer = csv.writer(csv_write_file, delimiter=',', lineterminator = '\n')
    csv_writer.writerow(['sample_id','species', 'value'])

    # take a look at each row of csv
    row_counter = 0
    cell_counter = 0
    with open(os.path.join(rootdir, "species_table.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        for row in my_csv:
            sample_id = row['sample_id']
            for j in row:
                if not str(j) == "sample_id" and "(TOT)" not in str(j):
                    if row[j]:
                        print("{} row:{}".format(row[j],row_counter))
                        if float(row[j]) > 0 :
                            csv_writer.writerow([sample_id, j, row[j]])
                            cell_counter = cell_counter + 1

            row_counter = row_counter + 1

print("ran through {} rows and wrote {} new lines to {}.".format(row_counter,cell_counter,csv_write_file.name))
