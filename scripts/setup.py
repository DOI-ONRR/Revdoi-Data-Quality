__author__ = "Edward Chang"

import os
import pandas as pd
from sys import argv


def get_data_type(name):
    type = ""
    if "federal" in name:
        type += "f"
    if "production" in name:
        type += "p"
    elif "revenue" in name:
        type += "r"
    return type


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


col_wlist = {'Calendar Year', 'Revenue', 'Volume', 'Month'}
# Returns a set based on Field given
def get_column(file, col):
    if col not in col_wlist:
        return {row for row in file[col]}


# Wrties to config to speed up process later
# TODO: Maybe have it write seperate files for each type?
def write_units(units, type):
    with open("config/" + type + "unitdef.txt", "w") as config:
        for k,v in units.items():
            for u in v:
                line = k + " = " +  u.strip("'")  + '\n'
                config.write(line)


# TODO: Same as above
def write_header(header, type):
    with open("config/" + type + "headerdef.txt","w") as config:
        for field in header:
            config.write(field + '\n')


def setup(pathname, type):
    sample = pd.read_excel(pathname)
    if not os.path.exists('config'):
        print('No Config Folder found. Creating folder...')
        os.mkdir('config')
    write_header(get_header(sample), type)
    write_units(get_unit_dict(sample), type)
    print("Setup Complete")


def main():
    type = get_data_type(argv[1])
    setup(argv[1], type)


if __name__ == '__main__':
    main()
