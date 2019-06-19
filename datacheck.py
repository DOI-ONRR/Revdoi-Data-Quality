__author__ = "Edward Chang"

from math import isnan
import os
import pandas as pd
from sys import argv

# Returns Product if present else returns Commodity
def get_com_or_pro(col):
    if col.contains("Product"):
        return "Product"
    return "Commodity"

# Reads Unit Config File
# Commodity and Unit seperated by an equals sign " = "
def read_uconfig():
    units = {}
    with open("config/unitdef.txt") as udef:
        for line in udef:
            split = line.split(" = ")
            add_item(split[0], split[1].strip(), units)
    return units


# Reads Header Config File
def read_hconfig():
    columns = []
    with open("config/headerdef.txt") as hdef:
        for line in hdef:
            columns.append(line.strip())
    return columns


# Returns Header List based on Excel file
def get_header(file):
    return list(file.columns)


# Returns Unit Dictionary on Excel file
def get_unit_dict(file):
    units = {}
    col = get_com_or_pro(file.columns)
    for row in file[col]:
        # Key and Value split
        line = split_unit(row)
        k,v = line[0], line[1]
        add_item(k,v,units)
    return units


# Returns a set based on Field given
def get_column(file, name):
    items = set()
    for row in file[name]:
        items.add(row)
    return items


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


# Wrties to config to speed up process later
# TODO: Maybe have it write seperate files for each type?
def write_units(units):
    with open("config/unitdef.txt", "w") as config:
        for k,v in units.items():
            for u in v:
                line = k + " = " +  u.strip("'")  + '\n'
                config.write(line)


# TODO: Same as above
def write_header(header):
    with open("config/headerdef.txt","w") as config:
        for field in header:
            config.write(field + '\n')


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


# Reports if a row is NaN for a certain column
def check_nan(file, col):
    for i in range(len(file))
        if isnan(row):
            print("Row " + str(i) + ": Missing " + col)


def setup(pathname):
    sample = pd.read_excel(pathname)
    if not os.path.exists('config'):
        print('No Config Folder found. Creating folder...')
        os.mkdir('config')
    write_header(get_header(sample))
    write_units(get_unit_dict(sample))
    print("Setup Complete")


def main():
    if argv[1].lower() == 'setup':
        setup(argv[2])
    else:
        file = pd.read_excel(argv[1])
        default_header = read_hconfig()
        default_units = read_uconfig()
        print('\n')
        check_header(file, default_header)
        print('\n')
        check_unit_dict(file, default_units)

if __name__ == '__main__':
    main()
