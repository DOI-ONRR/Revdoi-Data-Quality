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
    if col == "n/a":
        return "No Units Available"
    for u in file[col]:
        bad = check_unit(u, file)
        index+=1
    if not bad:
        print("All units valid :)")


''' Helper method for check_unit_dict '''
def _check_unit(string, file):
    # Splits line by Item and Unit
    line = split_unit(string)
    # Checks if Item is valid and has correct units
    if default.__contains__(line[0]):
        if line[1] not in default.get(line[0]):
            print('Row ' + str(index) + ': Expected Unit - (' + line[1]  + ') [For Item: ' + line[0] + ']')
            file.loc[index, col] = '[New Unit]' + u
            return True
    else:
        print('Row ' + str(index) + ': Unknown Item: ' + line[0])
        file.loc[index, col] =  '[New Item]' + u
        return True


''' For checking non-numerical columns '''
def check_misc_cols(file, default):
    bad = False
    for field in default:
        index = 0
        for i in file[field]:
            if i not in default.get(field) and i != 'n/a':
                print(field + ' Row ' + str(index) + ': Unexpected Entry: ' + i)
                file.loc[index, field] = '[New Item]' + i
                bad = True
            index += 1
    if not bad:
        print("All fields valid")


''' Reports if a column is missing values '''
def check_nan(file, col):
    for i in range(len(file)):
        if isnan(row):
            print("Row " + str(i) + ": Missing " + col)


def main():
    type = get_data_type(argv[1])
    file = pd.read_excel(argv[1]).fillna('n/a')

    df_NEW = file.copy()

    default_header = read_hconfig(type)
    default_units = read_uconfig(type)
    default_fields = read_fconfig(type)

    print()
    check_header(df_NEW, default_header)
    check_unit_dict(df_NEW, default_units)
    check_misc_cols(df_NEW, default_fields)

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
