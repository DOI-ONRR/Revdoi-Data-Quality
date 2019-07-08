__author__ = "Edward Chang"

# Imports
from math import isnan
import os
import pandas as pd
import pickle
from sys import argv

class FormatChecker:
    __slots__ = ['config']
    ''' Constructor for FormatChecker. Uses config based on data type'''
    def __init__(self, type):
        self.config = self.read_config(type)

    ''' Returns an unpickled Setup object '''
    def read_config(self, type):
        with open("config/" + type + "config.bin","rb") as config:
            return pickle.load(config)

    ''' Returns number of W's found for Volume and Location'''
    def get_w_count(self, file):
        volume_w_count = 0
        state_w_count = 0
        # If Volume is present in file
        if file.columns.contains("Volume"):
            for row in file["Volume"]:
                if row == 'W':
                    volume_w_count += 1
        # If State is present in file
        if file.columns.contains("State"):
            for row in file["State"]:
                if row == "Withheld":
                    state_w_count += 1
        # Returns Tuple of W count
        return volume_w_count, state_w_count

    ''' Checks header for Order and missing or unexpected field names '''
    def check_header(self, file):
        default = self.config.header
        columns = file.columns
        # Set of Unchecked columns.
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

    ''' Checks commodities/products for New items or Unexpected units of measurement '''
    def check_unit_dict(self, file, replace=None):

        def _check_unit(string, default, index):
            # Splits line by Item and Unit
            line = split_unit(string)
            # Checks if Item is valid and has correct units
            if default.__contains__(line[0]):
                if line[1] not in default.get(line[0]):
                    print('Row ' + str(index) + ': Expected Unit - (' + line[1]
                        + ') [For Item: ' + line[0] + ']')
                    return 1
            elif line[0] != "-0":
                print(col + ' Row ' + str(index) + ': Unknown Item: ' + line[0])
                return 1
            return 0

        default = self.config.units
        bad = 0
        col = get_com_pro(file.columns)
        replaced_dict = {i:[] for i in replace.keys()}
        if col == "n/a":
            return "No Units Available"
        for row in range(len(file[col])):
            cell = file.loc[row, col]
            if replace and replace.__contains__(cell):
                new_cell = replace[cell]
                # file.loc[row, col] = new_cell
                # print(col, row, "Found:", cell, "| Replace with:", new_cell)
                replaced_dict.get(cell).append(row + 1)
                continue
            bad += _check_unit(cell, default, row)
        print("Items to replace: ", replaced_dict)
        if bad <= 0 :
            print("All units valid :)")

    ''' Checks non-numerical columns for Unexpected Values '''
    def check_misc_cols(self, file):
        default = self.config.field_dict
        bad = False
        for field in default:
            if file.columns.contains(field):
                for row in range(len(file[field])):
                    cell = file.loc[row, field]
                    if cell not in default.get(field) and cell != "-0":
                        print(field + ' Row ' + str(row)
                            + ': Unexpected Entry: ' + str(cell))
                        bad = True
        if not bad:
            print("All fields valid :)")

    ''' Checks if specific columns are missing values '''
    def check_nan(self, file):
        cols = [ "Calendar Year", "Corperate Name", "Ficsal Year",
            "Mineral Lease Type", "Month", "Onshore/Offshore",
            "Revenue", "Volume" ]
        for col in cols:
            if file.columns.contains(col):
                for row in range(len(file.index)):
                    if file.loc[row, col] == "-0":
                        print("Row " + str(row) + ": Missing " + col)


class Setup:
    __slots__ = ['header', 'units', 'field_dict']

    ''' Constructor for Setup '''
    def __init__(self, file=None):
        if file is not None:
            self.set_file(file)

    ''' Sets variables based on file given '''
    def set_file(self, file):
        self.header = self.get_header(file) # List
        self.units = self.get_unit_dict(file) # Dictionary
        self.field_dict = self.get_misc_cols(file) # Dictionary

    """ Returns Header List based on Excel file
    Keyword arguements:
    file -- A Pandas DataFrame
    """
    def get_header(self, file):
        return list(file.columns)

    """ Returns Unit Dictionary on Excel file """
    def get_unit_dict(self, file):
        u = {}
        col = get_com_pro(file.columns)
        if col == "n/a":
            return
        for row in file[col]:
            # Key and Value split
            line = split_unit(row)
            k,v = line[0], line[1]
            add_item(k, v, u)
        return u

    """ Returns a dictionary of fields not listed in col_wlist """
    def get_misc_cols(self, file):
        col_wlist = { 'Revenue', 'Volume', 'Month', 'Production Volume', 'Total' }
        col_wlist.add(get_com_pro(file.columns))
        fields = {}
        for col in file.columns:
            if col not in col_wlist:
                fields[col] = { i for i in file[col] }
        return fields

    """ Writes a bin file containing all variables from Setup """
    def write_config(self, type):
        if not os.path.exists('config'):
            print('No Config Folder found. Creating folder...')
            os.mkdir('config')
        with open("config/" + type + "config.bin", "wb") as config:
            pickle.dump(self, config)
        print("Setup Complete")



""" For naming config files """
def get_data_type(name):
    lower = name.lower()
    prefixes = ["cy","fy","monthly","company","federal","native","production","revenue","disbribution"]
    final_prefix = ""
    for p in prefixes:
        if p in lower:
            final_prefix += p
    return final_prefix + "_"

""" Returns a list of the split string based on item and unit """
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

""" Adds key to dictionary if not present. Else adds value to key set.
Keyword arguements:
key -- Key entry for the dict, e.g. A commodity
value -- Value entry corresponding to key, e.g. Unit or Value
dictionary -- Reference to dictionary
"""
def add_item(key, value, dictionary):
    # Adds Value to Set if Key exists
    if key in dictionary:
        dictionary[key].add(value)
    # Else adds new key with value
    else:
        dictionary[key] = {value}

''' Checks if "Commodity", "Product", both, or neither are present '''
def get_com_pro(cols):
    if not cols.contains("Product") and not cols.contains("Commodity"):
        return "n/a"
    if cols.contains("Product"):
        if cols.contains("Commodity"):
            return"n/a"
        else:
            return "Product"
    return "Commodity"



''' Where all the stuff is ran '''
def main():
    if argv[1] == "setup":
        type = get_data_type(argv[2])
        file = pd.read_excel(argv[2])
        config = Setup(file)
        config.write_config(type)
    else:
        to_replace = {"Mining-Unspecified" : "Humate"}
        type = get_data_type(argv[1])
        file = pd.read_excel(argv[1]).fillna("-0")
        check = FormatChecker(type)
        check.check_header(file)
        print()
        check.check_unit_dict(file, to_replace)
        check.check_misc_cols(file)
        check.check_nan(file)
        w = check.get_w_count(file)
        print("\n(Volume) W's Found: " + str(w[0]) )
        print("(Location) W's Found: " + str(w[1]) )
        if argv[2] == "export":
            file.replace(to_replace, inplace=True)
            writer = pd.ExcelWriter("PlaceholderName.xlsx", engine='xlsxwriter')
            file.to_excel(writer, index=False, header=False)
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            header_format = workbook.add_format({
                "align" : "center",
                "bold" : False,
                "border" : 1,
                "bg_color" : "#C0C0C0",
                "valign" : "bottom"
            })
            cur_format = workbook.add_format({'num_format': '$#,##0.00'})
            num_format = workbook.add_format({'num_format': '#,##0.00'})
            for col_num, value in enumerate(file.columns.values):
                worksheet.write(0, col_num, value, header_format)
            writer.save()
            print("Exported new file")
        print("Done")

if __name__ == '__main__':
    main()
