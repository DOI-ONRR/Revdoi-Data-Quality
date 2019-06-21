# potato = [1,2,3,4,5,6]
# with open('potato.bin', mode= 'wb') as file:
#     pickle.dump(potato, file)
# yam = pickle.load(open('potato.bin', 'rb'))
# print(yam)

__author__ = "Edward Chang"

import os
import pandas as pd
import pickle
from sharedfunctions import add_item, split_unit, get_data_type, get_com_pro
from sys import argv

""" Returns Header List based on Excel file
Keyword arguements:
file -- A Pandas DataFrame
"""
def get_header(file):
    return list(file.columns)


""" Returns Unit Dictionary on Excel file"""
def get_unit_dict(file):
    units = {}
    col = get_com_pro(file.columns)
    for row in file[col]:
        # Key and Value split
        line = split_unit(row)
        k,v = line[0], line[1]
        add_item(k,v,units)
    return units


col_wlist = {'Calendar Year', 'Revenue', 'Volume', 'Month'}
''' Returns a dictionary of fields not listed in col_wlist '''
def get_misc_cols(file):
    fields = {}
    for col in file.columns:
        if col not in col_wlist:
            fields[col] = { i for i in file[col] }
    return fields


""" Writes a text file as on item and expected units of measurement """
def write_units(units, type):
    with open("config/" + type + "unitdict.bin", "wb") as config:
        pickle.dump(units, config)


""" Writes a text file based on a given header format """
def write_header(header, type):
    with open("config/" + type + "headerlist.bin","wb") as config:
        pickle.dump(header, config)


def write_misc_cols(cols, type):
    with open("config/" + type + "fielddict.bin","wb") as config:
        pickle.dump(cols, config)


""" Writing happens here """
def setup(pathname, type):
    sample = pd.read_excel(pathname)
    if not os.path.exists('config'):
        print('No Config Folder found. Creating folder...')
        os.mkdir('config')
    write_header(get_header(sample), type)
    write_units(get_unit_dict(sample), type)
    write_misc_cols(get_misc_cols(sample), type)
    print("Setup Complete")


def main():
    type = get_data_type(argv[1])
    setup(argv[1], type)


if __name__ == '__main__':
    main()