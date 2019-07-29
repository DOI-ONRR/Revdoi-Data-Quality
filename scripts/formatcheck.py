'''
For Checking anomolies within data
'''
from datetime import datetime
from pathlib import Path
import json
import os
import sys
import pandas as pd


__author__ = 'Edward Chang'


class FormatChecker:
    '''
    Checks Excel File for Header format, Correct Units, and other fields
    Also counts Withheld
    '''

    __slots__ = ['config']

    def __init__(self, prefix):
        '''Constructor for FormatChecker. Uses config based on data

        Keyword Arguments:
            prefix -- Prefix of the json file
        '''
        self.config = self.read_config(prefix)


    def read_config(self, prefix):
        '''Returns an decoded json file

        Keyword Arguments:
            prefix -- Prefix of the json file
        '''
        with open('config/' + prefix + 'config.json', 'r') as config:
            return json.load(config)


    def get_w_count(self, df):
        '''Returns number of Ws found for Volume and Location
        Keyword Arguments:
            df -- A pandas DataFrame
        '''
        volume_w_count = 0
        state_w_count = 0
        # If Volume is present in df
        if df.columns.contains('Volume'):
            for entry in df['Volume']:
                if entry == 'W':
                    volume_w_count += 1
        # If State is present in df
        if df.columns.contains('State'):
            for entry in df['State']:
                if entry == 'Withheld':
                    state_w_count += 1
        # Returns Tuple of W count
        return volume_w_count, state_w_count


    def check_header(self, df):
        '''Checks header for Order and missing or unexpected field names'''
        default = self.config['header']
        columns = df.columns
        # Set of Unchecked columns.
        unchecked_cols = set(columns)
        for i, field in enumerate(default):
            # Checks if Field in df and in correct column
            if columns.contains(field):
                if columns[i] == field:
                    print(field + ': True')
                else:
                    print(field + ': Unexpected order')
                unchecked_cols.remove(field)
            else:
                # Field not present in the df
                print(field + ': Not Present')
        # Prints all fields not in the format
        if unchecked_cols:
            print('\nNew Cols:', unchecked_cols)
            for col in unchecked_cols:
                if col.endswith(' ') or col.startswith(' '):
                    print('Whitespace found for: ' + col)


    def check_unit_dict(self, df):
        '''Checks commodities/products for New items or
        Unexpected units of measurement

        Keyword Arguments:
            df -- A pandas DataFrame
            replace -- Dictionary with values to replace
        '''
        default = self.config['unit_dict']
        replace = self.config['replace_dict']
        errors = 0
        col = get_com_pro(df)
        replaced_dict = {i:[] for i in replace.keys()}
        is_replaced = False
        if col == 'n/a':
            return 'No Units Available'
        for row in range(len(df[col])):
            cell = df.loc[row, col]
            if replace and replace.__contains__(cell):
                replaced_dict.get(cell).append(row + 1)
                is_replaced = True
                continue
            errors += self._check_unit(cell, default, row)
        if is_replaced:
            print('Items to replace: ', replaced_dict)
        if errors <= 0:
            print('All units valid :)')
        return errors


    def _check_unit(self, string, default, index):
        '''Checks if item and unit in unit_dict'''
        if string == '':
            return 0
        # Splits line by Item and Unit
        line = split_unit(string)
        # Checks if Item is valid and has correct units
        if default.__contains__(line[0]):
            if line[1] not in default.get(line[0]):
                print('Row ' + str(index) + ': Unexpected Unit - (' + line[1]
                      + ') [For Item: ' + line[0] + ']')
                return 1
        elif line[0] != '':
            print('Row ' + str(index) + ': Unknown Item: ' + line[0])
            return 1
        return 0


    def check_misc_cols(self, df):
        '''Checks non-numerical columns for Unexpected Values'''
        default = self.config['field_dict']
        is_valid = True
        if df.columns.contains('Calendar Year'):
            self.check_year(df['Calendar Year'])
        elif df.columns.contains('Fiscal Year'):
            self.check_year(df['Fiscal Year'])
        for field in default:
            if df.columns.contains(field):
                for row in range(len(df[field])):
                    cell = df.loc[row, field]
                    if cell not in default.get(field) and cell != '':
                        print(field + ' Row ' + str(row)
                              + ': Unexpected Entry: ' + str(cell))
                        is_valid = False
        if is_valid:
            print('All fields valid :)')
        return is_valid


    def check_year(self, col):
        '''Checks if year column is valid

        Keyword Arguments:
            col -- Column in which year is located
        '''
        current_year = datetime.now().year
        years = {i for i in range(current_year, 1969, -1)}
        for row, year in enumerate(col):
            if year not in years:
                print('Row ' + str(row + 2) + ': Invalid year ' + str(year))


    def check_nan(self, df):
        '''Checks if specific columns are missing values
        '''
        cols = self.config['na_check']
        for col in cols:
            if df.columns.contains(col):
                for row in range(len(df.index)):
                    if df.loc[row, col] == '':
                        print('Row ' + str(row + 2) + ': Missing ' + col)


class Setup:
    '''
    For creating json files
    '''

    __slots__ = ['df']

    def __init__(self, df):
        '''Constructor for setup

        Keyword Arguments:
            df -- A pandas DataFrame
        '''
        self.df = df


    # Returns Header List based on Excel DataFrame
    def get_header(self):
        return list(self.df.columns)


    # Returns Unit Dictionary on Excel DataFrame
    def get_unit_dict(self):
        units = {}
        col = get_com_pro(self.df)
        if col == 'n/a':
            return None
        for row in self.df[col]:
            # Key and Value split
            line = split_unit(row)
            key, value = line[0], line[1]
            add_item(key, value, units)
        return units


    # Returns a dictionary of fields not listed in col_wlist
    def get_misc_cols(self):
        col_wlist = {'Revenue', 'Volume', 'Month', 'Production Volume',
                     'Total', 'Calendar Year'}
        col_wlist.add(get_com_pro(self.df))
        fields = {}
        for col in self.df.columns:
            if col not in col_wlist:
                fields[col] = list({i for i in self.df[col]})
        return fields


    def get_na_check(self):
        return ['Calendar Year', 'Corperate Name', 'Ficsal Year',
                'Mineral Lease Type', 'Month', 'Onshore/Offshore', 'Volume']


    def get_replace_dict(self):
        return {'Mining-Unspecified' : 'Humate'}

    def make_config_path(self):
        '''Creates directory "config" if it does not exist'''
        if not os.path.exists('config'):
            print('No Config Folder found. Creating folder...')
            os.mkdir('config')


    def write_config(self, prefix):
        '''Writes a json file based on the given Excel File

        Keyword Arguments:
            prefix -- Prefix of the new json file
        '''
        self.make_config_path()
        with open('config/' + prefix + 'config.json', 'w') as config:
            json_config = {'header' : self.get_header(),
                           'unit_dict' : self.get_unit_dict(),
                           'field_dict' : self.get_misc_cols(),
                           'replace_dict' : self.get_replace_dict(),
                           'na_check' : self.get_na_check(),
                           }
            json.dump(json_config, config, indent=4)


def add_item(key, value, dct):
    '''Adds key to dictionary if not present. Else adds value to key 'set'.

    Keyword Arguments:
        key -- Key entry for the dict, e.g. A commodity
        value -- Value entry corresponding to key, e.g. Unit or Value
        dictionary -- Reference to dictionary
    '''
    # Adds Value to Set if Key exists
    if key in dct:
        if value not in dct[key]:
            dct[key].append(value)
    # Else adds new key with value
    else:
        dct[key] = [value]


def get_prefix(name):
    '''For naming config files

    Keyword Arguments:
        name -- Name of the Excel file
    '''
    lower = name.lower()
    prefixes = ['cy', 'fy', 'monthly', 'company', 'federal', 'native',
                'production', 'revenue', 'disbursements']
    final_prefix = ''
    for string in prefixes:
        if string in lower:
            final_prefix += string
    return final_prefix + '_'


# Returns a list of the split string based on item and unit
def split_unit(string):
    string = str(string)
    # For general purpose commodities
    if '(' in string:
        split = string.rsplit(' (', 1)
        split[1] = split[1].rstrip(')')
        return split
    # The comma is for Geothermal
    elif ',' in string:
        return string.split(', ', 1)
    # In case no unit is found
    return [string, '']


# Checks if 'Commodity', 'Product', both, or neither are present
def get_com_pro(df):
    if not df.columns.contains('Product') and not df.columns.contains('Commodity'):
        return 'n/a'
    elif df.columns.contains('Commodity'):
        return 'Commodity'
    else:
        return 'Product'


# Creates FormatChecker and runs methods
def do_check(df, prefix, name, export):
    check = FormatChecker(prefix)
    # Exports an Excel df with replaced entries
    def export_excel(df, to_replace):
        df.replace(to_replace, inplace=True)
        writer = pd.ExcelWriter('../output/[new] ' + name, engine='xlsxwriter')
        df.to_excel(writer, index=False, header=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        header_format = workbook.add_format({
            'align' : 'center',
            'bold' : False,
            'border' : 1,
            'bg_color' : '#C0C0C0',
            'valign' : 'bottom'
        })
    #    cur_format = workbook.add_format({'num_format': '$#,##0.00'})
    #    num_format = workbook.add_format({'num_format': '#,##0.00'})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        writer.save()
        print('Exported new df to output')
    check.check_header(df)
    print()
    check.check_unit_dict(df)
    check.check_misc_cols(df)
    check.check_nan(df)
    w_count = check.get_w_count(df)
    print('\n(Volume) Ws Found: ' + str(w_count[0]))
    print('(Location) Ws Found: ' + str(w_count[1]))

    if export:
        export_excel(df, check.config['replace_dict'])


# Where all the stuff runs
def main():
    prefix = get_prefix(sys.argv[-1])
    df = pd.read_excel(sys.argv[-1]).fillna('')
    if sys.argv[1] == 'setup':
        config = Setup(df)
        config.write_config(prefix)
    else:
        try:
            do_check(df, prefix, sys.argv[-1], sys.argv[2] == 'export')
        except FileNotFoundError:
            print("Config not found! Please use setup for: " + prefix)
    print('Done')


if __name__ == '__main__':
    main()
