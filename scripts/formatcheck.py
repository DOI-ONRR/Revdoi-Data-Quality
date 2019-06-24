__author__ = "Edward Chang"

from math import isnan
import pandas as pd
import pickle
from sharedfunctions import add_item, split_unit, get_data_type, get_com_pro
from sys import argv

''' Reads Unit Config File
Commodity and Unit seperated by an equals sign " = " '''
def read_uconfig(type):
    units = {}
    with open("config/" + type + "unitdict.bin", "rb") as udef:
        units = pickle.load(udef)
    return units


''' Reads Header Config File '''
def read_hconfig(type):
    columns = []
    with open("config/" + type + "headerlist.bin", "rb") as hdef:
        columns = pickle.load(hdef)
    return columns


''' Reads Unit Config File
Commodity and Unit seperated by an equals sign " = " '''
def read_fconfig(type):
    fields = {}
    with open("config/" + type + "fielddict.bin", "rb") as fdef:
        fields = pickle.load(fdef)
    return fields



''' Returns number of W's in a given column '''
def get_w_count(file, col):
    w_count = 0
    for row in file[col]:
        if row == 'W':
            w_count += 1
    return w_count


''' Checks header for any inconsistences
i.e. Order, missing or unexpected fields'''
def check_header(file, default):
    columns = file.columns
    uncheckedCols = set(columns)
    for i in range(len(default)):
        # Checks if Field in file and in correct column
        if columns.contains(default[i]):
            if columns[i] == default[i]:
                print(default[i] + ": True")
            else:
                print(default[i] + ": Unexpected order")
            uncheckedCols.remove(default[i])
        else:
            # Field not present in the file
            print(default[i] + ": Not Present")
    # Prints all fields not in the format
    if len(uncheckedCols) > 0:
        print("\nNew Cols:", uncheckedCols)

''' Checks commodities/products for inconsistences
i.e. New items, Unexpected units of measurement '''
def check_unit_dict(file, default):
    index = 0
    bad = False
    col = get_com_pro(file.columns)
    if col == "both":
        return "No Units Available"
    for u in file[col]:
        bad = check_unit(u)
        index+=1
    if not bad:
        print("All units valid :)")

''' Helper method for check_unit_dict '''
def _check_unit(string):
    # Splits line by Item and Unit
    line = split_unit(string)
    # Checks if Item is valid and has correct units
    if default.__contains__(line[0]):
        if line[1] not in default.get(line[0]):
            print('Row ' + str(index) + ': Expected Unit - (' + line[1]  + ') [For Item: ' + line[0] + ']')
            return True
    else:
        print('Row ' + str(index) + ': Unknown Item: ' + line[0])
        return True


''' For checking non-numerical columns '''
def check_misc_cols(file, default):
    index = 0
    bad = False
    for field in default:
        for i in file[field]:
            if i not in default.get(field):
                print('Row ' + str(index) + ': Unexpected Entry: ' + i)
                bad = True
    if not bad:
        print("All fields valid")

''' Reports if a column is missing values '''
def check_nan(file, col):
    for i in range(len(file)):
        if isnan(row):
            print("Row " + str(i) + ": Missing " + col)


def main():
    type = get_data_type(argv[1])
    file = pd.read_excel(argv[1])

    default_header = read_hconfig(type)
    default_units = read_uconfig(type)
    default_fields = read_fconfig(type)

    print()
    check_header(file, default_header)
    check_unit_dict(file, default_units)
    check_misc_cols(file, default_fields)


if __name__ == '__main__':
    main()
