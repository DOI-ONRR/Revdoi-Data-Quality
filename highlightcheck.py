__author__ = "Edward Chang"

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
# Fast, Best for small number of Units / after initial read
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
# Use if large amount of Field Names
def get_header(file):
    return list(file.columns)


# Returns Unit Dictionary on Excel file
# Very Slow, but better than manually setting large # of units
def get_unit_dict(file):
    units = {}
    col = get_com_or_pro(file.columns)
    for row in file[col]:
        # Key and Value split
        line = split_unit(row)
        k,v = line[0], line[1]
        add_item(k,v,units)
    return units


def get_land_classes(file):
    classes = set()
    for row in file['Land Class']:
        classes.add(row)
    return classes


def get_land_categories(file):
    categories = set()
    for row in file['Land Categories']:
        categories.add(row)
    return categories


def get_states(file):
    states = set()
    for row in file['State']:
        categories.add(row)
    return states


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
                file.loc[index, col] = '[New Unit]' + u
                bad = True
        else:
            print('Row ' + str(index) + ': Unknown Item: ' + line[0])
            file.loc[index, col] =  '[New Item]' + u
            bad = True
        index+=1
    if not bad:
        print('No Errors Found :)')


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
        df_NEW = file.copy()

        default_header = read_hconfig()
        default_units = read_uconfig()

        print('\n')
        check_header(df_NEW, default_header)
        print('\n')
        check_unit_dict(df_NEW, default_units)

        writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')
        df_NEW.to_excel(writer, sheet_name='Sheet1')
        workbook  = writer.book
        worksheet = writer.sheets['Sheet1']
        highlight_fmt = workbook.add_format({'font_color': '#FF0000', 'bg_color':'#B1B3B3', 'bold':True})
        new_fmt = workbook.add_format({'font_color': '#32CD32', 'bold':True})

        worksheet.conditional_format('A1:ZZ1000', {'type': 'text',
                                            'criteria': 'containing',
                                            'value':'[New Unit]',
                                            'format': highlight_fmt}, )

        worksheet.conditional_format('A1:ZZ1000', {'type': 'text',
                                            'criteria': 'containing',
                                            'value':'[New Item]',
                                            'format': new_fmt}, )

        # save
        writer.save()
        print('done')

if __name__ == '__main__':
    main()
