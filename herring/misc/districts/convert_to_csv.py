import os
import csv
import datetime

rootdir = "C:\\Users\\fishmand\\Projects\\glf_sci_site\\herring\\misc\\districts"

# open the csv we want to write to
with open(os.path.join(rootdir, "district_new_list.csv"), 'w') as new_file:
    new_file_writer = csv.writer(new_file, delimiter=',', lineterminator = '\n')
    new_file_writer.writerow(['district_id','province_id', 'locality_list'])

    with open(os.path.join(rootdir, "district_list.csv"), 'r') as old_file:
        my_csv = csv.reader(old_file)
        my_dict = {}

        for row in my_csv:
            if not row[0].startswith("ID"):
                district_id = row[1]
                province_id = row[2]
                locality_list = row[3]

                try:
                    my_dict[province_id]
                except Exception as e:
                    my_dict[province_id]={}
                    my_dict[province_id][district_id] = locality_list
                else:
                    try:
                        my_dict[province_id][district_id]
                    except Exception as e:
                        my_dict[province_id][district_id] = locality_list
                    else:
                        my_dict[province_id][district_id] = my_dict[province_id][district_id] + ", " + locality_list

        for p in my_dict:
            for d in my_dict[p]:
                province_id = p
                district_id = d
                locality_list = my_dict[p][d]
                new_file_writer.writerow([district_id, province_id, locality_list])



        #
        #
        #
        #
        #
        # for subdir, dirs, files in os.walk(os.path.join(rootdir, "hdr")):
        #
        #     for file in files:
        #         # for each cast
        #
        #         ## get filepath of HDR File
        #         hdr_filepath = os.path.join(subdir, file)
        #
        #         ## get set number as string
        #         set = file.replace("18196","").replace(".hdr","")
        #
        #         ## take a look at each row of csv
        #         with open(hdr_filepath, 'r') as csvfile:
        #             my_csv = csv.reader(csvfile)
        #             for row in my_csv:
        #
        #                 if row[0].startswith("** Set_number:"):
        #                     set_str = row[0].replace("** Set_number:","").replace(" ","")
        #                     set_int = int(set_str)
        #
        #                 if row[0].startswith("* NMEA Latitude"):
        #                     lat = row[0].replace("* NMEA Latitude = ","").replace("N","")
        #                     lat_d = float(lat.split(" ")[0])+(float(lat.split(" ")[1])/60)
        #
        #                 if row[0].startswith("* NMEA Longitude"):
        #                     long = row[0].replace("* NMEA Longitude = ","").replace("W","")
        #                     long_d = float(long.split(" ")[0])+(float(long.split(" ")[1])/60)
        #
        #
        #                 if row[0].startswith("* System UTC"):
        #                     set_datetime_str = datetime.datetime.strptime(row[0].replace("* System UTC = ",""), '%b %d %Y %H:%M:%S').strftime('%b %d, %Y %H:%M:%S')
        #
        #                 if row[0].startswith("** ID_start:"):
        #                     start_bottle_int = int(row[0].replace("** ID_start:","").replace(" ",""))
        #
        #         set_info_writer.writerow([set, set_int, set_datetime_str, lat_d, long_d, file.replace(".hdr",".hex")])
        #
        #         bl_filepath = os.path.join(rootdir, "bl", file.replace(".hdr",".bl"))
        #
        #         ## take a look at each row of csv
        #         with open(bl_filepath, 'r') as bl_csvfile:
        #             my_csv1 = csv.reader(bl_csvfile, delimiter='|')
        #             start_writing = False
        #             for row in my_csv1:
        #                 # print(row[0])
        #                 if row[0].startswith("1,"):
        #                     start_writing = True
        #
        #                 if start_writing:
        #                     bottle_id = int(row[0].split(", ")[0]) + start_bottle_int - 1
        #                     bottle_datetime_str = datetime.datetime.strptime(row[0].split(", ")[2], '%b %d %Y %H:%M:%S').strftime('%b %d, %Y %H:%M:%S')
        #                     bottle_writer.writerow([bottle_id, bottle_datetime_str])
