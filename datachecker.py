import pandas as pd

# Reads Unit Config File
# Commodity and Unit seperated by an equals sign " = "
# Fast, Best for small number of Units / after initial read
def read_uconfig():
    units = {}
    with open('config/unitdef.txt') as udef:
        for line in udef:
            split = line.split(" = ")
            add_item(split[0], split[1].strip(), units)
    return units


# Reads Header Config File
def read_hconfig():
    columns = []
    with open('config/headerdef.txt') as hdef:
        # Seperated by commas, no whitespace plz :(
        columns = hdef.readline().split(',')
    return columns


# Returns Header List based on Excel file
# Use if large amount of Field Names
def set_header(file):
    return list(file.columns)


# Returns Unit Dictionary on Excel file
# Very Slow, but better than manually setting large # of units
def make_unit_dict(file):
    units = {}
    for row in file['Product']:
        # Key and Value split
        line = split_unit(row)
        k,v = line[0], line[1]
        add_item(k,v,units)
    return units


# Returns Split String based on Commodity and Unit
def split_unit(string):
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
    config = open("config/unitdef.txt","w")
    for k,v in units.items():
        for u in v:
            line = k + ' = ' +  u.strip("'")  + '\n'
            config.write(line)
    config.close()

# TODO: Same as above
def write_header(header):
    config = open("config/headerdef.txt","w")
    for field in header:
        config.write(field)
    config.close()


def check_header(file):
    columns = file.columns
    uncheckedCols = set(columns)
    for i in range(len(header)):
        # Checks if Field in file and in correct column
        if columns.contains(header[i]):
            if columns[i] == header[i]:
                print(header[i] + ": True")
            else:
                print(header[i] + ": Wrong order")
            uncheckedCols.remove(header[i])
        else:
            # Field not present in the file
            print(header[i] + ': N/A')
    # Prints all fields not in the format
    print('\nNew Cols:', uncheckedCols)


def check_unit_dict(file, default):
    index = 0
    bad = False
    for u in file['Product']:
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
