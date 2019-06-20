__author__ = "Edward Chang"

from math import isnan
import pandas as pd
from sys import argv

# Reads Unit Config File
# Commodity and Unit seperated by an equals sign " = "
def read_uconfig(type):
    units = {}
    with open("config/" + type + "unitdef.txt") as udef:
        for line in udef:
            split = line.split(" = ")
            add_item(split[0], split[1].strip(), units)
    return units


# Reads Header Config File
def read_hconfig(type):
    columns = []
    with open("config/" + type + "headerdef.txt") as hdef:
        columns = [line.strip() for line in hdef]
    return columns


def get_data_type(name):
    type = ""
    if "federal" in name:
        type += "f"
    if "production" in name:
        type += "p"
    elif "revenue" in name:
        type += "r"
    return type


# Returns Product if present else returns Commodity
def get_com_or_pro(col):
    if col.contains("Product"):
        return "Product"
    return "Commodity"


col_wlist = {'Calendar Year', 'Revenue', 'Volume', 'Month'}
# Returns a set based on Field given
def get_column(file, col):
    if col not in col_wlist:
        return {row for row in file[col]}


# Returns number of W's in column
def get_w_count(file, col):
    w_count = 0
    for row in file[col]:
        if row == 'W':
            w_count += 1
    return w_count


# Returns Split String based on Commodity and Unit
def split_unit(string):
    string = str(string)
    # For general purpose commodities
    if "(" in string:
        split = string.rsplit(" (",1)
        split[1] = split[1].rstrip(")")
        return split
    # The comma is for Geothermal
    elif "," in string:
        return string.split(", ",1)
    # In case no unit is found
    return [string,'']


def add_item(key, value, dictionary):
    # Adds Value to Set if Key exists
    if key in dictionary:
        dictionary[key].add(value)
    # Else adds new key with value
    else:
        dictionary[key] = {value}


def check_header(file, default):
    columns = file.columns
    uncheckedCols = set(columns)
    for i in range(len(default)):
        # Checks if Field in file and in correct column
        if columns.contains(default[i]):
            if columns[i] == default[i]:
                print(default[i] + ": True")
            else:
                print(default[i] + ": Wrong order")
            uncheckedCols.remove(default[i])
        else:
            # Field not present in the file
            print(default[i] + ": N/A")
    # Prints all fields not in the format
    if len(uncheckedCols) > 0:
        print("\nNew Cols:", uncheckedCols)


def check_unit_dict(file, default):
    index = 0
    bad = False
    col = get_com_or_pro(file.columns)
    for u in file[col]:
        # Splits line by Item and Unit
        line = split_unit(u)
        # Checks if Item is valid and has correct units
        if default.__contains__(line[0]):
            if line[1] not in default.get(line[0]):
                print('Row ' + str(index) + ': Unknown Unit - (' + line[1]  + ') [For Item: ' + line[0] + ']')
                bad = True
        else:
            print('Row ' + str(index) + ': Unknown Item: ' + line[0])
            bad = True
        index+=1
    if not bad:
        print('No Errors Found :)')

def check_misc_cols(file, default):
    index = 0
    for row in file[col]:
        if row not in default:
            print(row + ' ' + str(index) + ': Unknown Input: ' + line[0])


# Reports if a row is NaN for a certain column
def check_nan(file, col):
    for i in range(len(file)):
        if isnan(row):
            print("Row " + str(i) + ": Missing " + col)


def main():
    type = get_data_type(argv[1])
    file = pd.read_excel(argv[1])
    default_header = read_hconfig(type)
    default_units = read_uconfig(type)
    check_header(file, default_header)
    check_unit_dict(file, default_units)


if __name__ == '__main__':
    main()
