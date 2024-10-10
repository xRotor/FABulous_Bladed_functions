from ANSFAB__Utility import Utility

def interpolate_linear(x0, x1, x2, y1, y2):
    # linear interpolation with x1 <= x0 <= x2 and y1 < y2
    y0 = (y2-y1) / (x2-x1) * (x0-x1) + y1
    return y0

def change_dict_from_csv_reader(dict_file_name, interpolation_value):
    # Make sure that the csv file is ordered such that the first column addresses the interpolation (or direct) value
    # ordered from smallest to biggest (first column header is ignored here), the next columns should have the key words
    # as header which should be exchanged in the Bladed prj-file, followed by the respective values.
    change_dict_list = Utility().readListDictFromCSV(dict_file_name)

    keys = [key for key in change_dict_list[0].keys() if key]

    for row_nmbr in range(len(change_dict_list)-1):
        if float(change_dict_list[row_nmbr].get(keys[0])) > interpolation_value:
            ChangeDicts = []
            if row_nmbr != 0:
                row_nmbr = row_nmbr - 1
            for key in keys[1:]:
                change_value = interpolate_linear(interpolation_value,
                                                  float(change_dict_list[row_nmbr].get(keys[0])),
                                                  float(change_dict_list[row_nmbr+1].get(keys[0])),
                                                  float(change_dict_list[row_nmbr].get(key)),
                                                  float(change_dict_list[row_nmbr+1].get(key)))
                ChangeDicts.append({'WORD': key, 'EXCHANGE': key + str(change_value) + ';'})

            print('interpolating', interpolation_value, 'by', change_dict_list[row_nmbr].get(keys[0]), 'and',
                  change_dict_list[row_nmbr + 1].get(keys[0]), 'for', key, 'with', change_dict_list[row_nmbr].get(key),
                  'and', change_dict_list[row_nmbr + 1].get(key), 'to', change_value)

            return ChangeDicts


