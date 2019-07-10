'''
For Checking anomolies within data
'''
from datetime import datetime
import json
import os
import sys
import pandas as pd


__author__ = 'Edward Chang'


class FormatChecker:

    __slots__ = ['config']

    ''' Constructor for FormatChecker. Uses config based on data '''
    def __init__(self, prefix):
        self.config = self.read_config(prefix)

    ''' Returns an unpickled Setup object '''
    def read_config(self, prefix):
        with open('config/' + prefix + 'config.json', 'r') as config:
            return json.load(config)

    ''' Returns number of Ws found for Volume and Location '''
    def get_w_count(self, file):
        volume_w_count = 0
        state_w_count = 0
        # If Volume is present in file
        if file.columns.contains('Volume'):
            volume_w_count = file['Volume'].eq('W').sum()
        # If State is present in file
        if file.columns.contains('State'):
            state_w_count = file['State'].eq('Withheld').sum()
        # Returns Tuple of W count
        return volume_w_count, state_w_count

    ''' Checks header for Order and missing or unexpected field names '''
    def check_header(self, file):
        default = self.config['header']
        columns = file.columns
        # Set of Unchecked columns.
        unchecked_cols = set(columns)
        for i in range(len(default)):
            # Checks if Field in file and in correct column
            if columns.contains(default[i]):
                if columns[i] == default[i]:
                    print(default[i] + ': True')
                else:
                    print(default[i] + ': Unexpected order')
                unchecked_cols.remove(default[i])
            else:
                # Field not present in the file
                print(default[i] + ': Not Present')
        # Prints all fields not in the format
        if unchecked_cols:
            print('\nNew Cols:', unchecked_cols)
            for col in unchecked_cols:
                if col.endswith(' ') or col.startswith(' '):
                    print('Whitespace found for: ' + col)

    ''' Checks commodities/products for New items or Unexpected units of measurement '''
    def check_unit_dict(self, file, replace=None):
        default = self.config['unit_dict']
        bad = 0
        col = get_com_pro(file.columns)
        replaced_dict = {i:[] for i in replace.keys()}
        is_replaced = False
        if col == 'n/a':
            return 'No Units Available'
        for row in range(len(file[col])):
            cell = file.loc[row, col]
            if replace and replace.__contains__(cell):
                replaced_dict.get(cell).append(row + 1)
                is_replaced = True
                continue
            bad += self._check_unit(cell, default, row)
        if is_replaced:
            print('Items to replace: ', replaced_dict)
        if bad <= 0:
            print('All units valid :)')

    ''' Checks if unit and unit in unit_dict '''
    def _check_unit(self, string, default, index):
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

    ''' Checks non-numerical columns for Unexpected Values '''
    def check_misc_cols(self, file):
        default = self.config['field_dict']
        bad = False
        if file.columns.contains('Calendar Year'):
            self.check_year(file['Calendar Year'])
        for field in default:
            if file.columns.contains(field):
                for row in range(len(file[field])):
                    cell = file.loc[row, field]
                    if cell not in default.get(field) and cell != '':
                        print(field + ' Row ' + str(row)
                              + ': Unexpected Entry: ' + str(cell))
                        bad = True
        if not bad:
            print('All fields valid :)')

    ''' Checks if year column is valid '''
    def check_year(self, col):
        current_year = datetime.now().year
        # current_month = datetime.now().month
        years = {i for i in range(current_year, 1969, -1)}
        for row in range(len(col)):
            if col[row] not in years:
                print('Row ' + str(row + 2) + ': Invalid year ' + str(col[row]))

    ''' Checks if specific columns are missing values '''
    def check_nan(self, file):
        cols = ['Calendar Year', 'Corperate Name', 'Ficsal Year',
                'Mineral Lease Type', 'Month', 'Onshore/Offshore', 'Volume']
        for col in cols:
            if file.columns.contains(col):
                for row in range(len(file.index)):
                    if file.loc[row, col] == '':
                        print('Row ' + str(row + 2) + ': Missing ' + col)



class NumberChecker:
    __slots__ = ['col']

    def __init__(self, file):
        self.col = self._get_vol_rev(file.columns)

    ''' Reports values with difference > n SD '''
    def check_sd(self, file, standard_devation):
        groups = file.groupby([get_com_pro(file.columns)])
        deviation_present = False
        for item, df in groups:
            if item == '':
                continue
            ind = df.index
            mean = df[self.col].mean()
            std = df[self.col].std() * standard_devation

            maxSigma = mean + std
            minSigma = mean - std

            deviations = []

            for i in ind:
                value = file.loc[i, self.col]
                if value > maxSigma or value < minSigma:
                    deviations.append(str(i) + ': ' + str(value))
            if deviations:
                deviation_present = True
                print('------------------------\n', item,
                      minSigma, '|', maxSigma, '\n------------------------')
                for j in deviations:
                    print(j)
        if not deviation_present:
            print('No deviations present')

    ''' Set threshold '''
    def check_threshold(self, file, minSigma=0, maxSigma=0):
        for i in range(len(file[self.col])):
            foo = file.loc[i, self.col]
            if foo < minSigma or foo > maxSigma:
                print(i, foo, 'A')

    ''' Checks if 'Revenue' or 'Volume' is present '''
    def _get_vol_rev(self, cols):
        if cols.contains('Revenue'):
            return 'Revenue'
        return 'Volume'


class Setup:

    '''
    For creating json files
    '''

    __slots__ = ['file']

    ''' Constructor for Setup '''
    def __init__(self, file):
        self.file = file

    ''' Returns Header List based on Excel file  '''
    def get_header(self):
        return list(self.file.columns)

    ''' Returns Unit Dictionary on Excel file '''
    def get_unit_dict(self):
        units = {}
        col = get_com_pro(self.file.columns)
        if col == 'n/a':
            pass
        for row in self.file[col]:
            # Key and Value split
            line = split_unit(row)
            key, value = line[0], line[1]
            add_item(key, value, units)
        return units

    ''' Returns a dictionary of fields not listed in col_wlist '''
    def get_misc_cols(self):
        col_wlist = {'Revenue', 'Volume', 'Month', 'Production Volume',
                     'Total', 'Calendar Year'}
        col_wlist.add(get_com_pro(self.file.columns))
        fields = {}
        for col in self.file.columns:
            if col not in col_wlist:
                fields[col] = list({i for i in self.file[col]})
        return fields

    def get_replace_dict(self):
        return {'Mining-Unspecified' : 'Humate'} #Entries to be replaced

    ''' Creates directory "config" if it does not exist '''
    def make_config_path(self):
        if not os.path.exists('config'):
            print('No Config Folder found. Creating folder...')
            os.mkdir('config')

    ''' Writes a json file containing all variables from Setup '''
    def write_config(self, prefix):
        self.make_config_path()
        with open('config/' + prefix + 'config.json', 'w') as config:
            json_config = {'header' : self.get_header(),
                           'unit_dict' : self.get_unit_dict(),
                           'field_dict' : self.get_misc_cols(),
                           'replace_dict' : self.get_replace_dict(),
                           'withheld_check' : []}
            json.dump(json_config, config, indent=4)



''' Adds key to dictionary if not present. Else adds value to key set.
Keyword arguements:
key -- Key entry for the dict, e.g. A commodity
value -- Value entry corresponding to key, e.g. Unit or Value
dictionary -- Reference to dictionary
'''
def add_item(key, value, dct):
    # Adds Value to Set if Key exists
    if key in dct:
        if value not in dct.get(key):
            dct[key].append(value)
    # Else adds new key with value
    else:
        dct[key] = [value]

''' For naming config files '''
def get_prefix(name):
    lower = name.lower()
    prefixes = ['cy', 'fy', 'monthly', 'company', 'federal', 'native',
                'production', 'revenue', 'disbribution']
    final_prefix = ''
    for p in prefixes:
        if p in lower:
            final_prefix += p
    return final_prefix + '_'

""" Returns a list of the split string based on item and unit """
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



""" Checks if 'Commodity', 'Product', both, or neither are present """
def get_com_pro(cols):
    if not cols.contains('Product') and not cols.contains('Commodity'):
        return 'n/a'
    elif cols.contains('Commodity'):
        return 'Commodity'
    return 'Product'

""" Creates FormatChecker and runs methods """
def do_check(file, prefix, to_replace):
    check = FormatChecker(prefix)
    check.check_header(file)
    print()
    check.check_unit_dict(file, to_replace)
    print()
    check.check_misc_cols(file)
    check.check_nan(file)
    w = check.get_w_count(file)
    print('\n(Volume) Ws Found: ' + str(w[0]))
    print('(Location) Ws Found: ' + str(w[1]))

""" Exports an Excel file with replaced entries """
def export_excel(file, to_replace):
    file.replace(to_replace, inplace=True)
    writer = pd.ExcelWriter('PlaceholderName.xlsx', engine='xlsxwriter')
    file.to_excel(writer, index=False, header=False)
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
    for col_num, value in enumerate(file.columns.values):
        worksheet.write(0, col_num, value, header_format)
    writer.save()
    print('Exported new file')


def main():
    prefix = get_prefix(sys.argv[-1])
    file = pd.read_excel(sys.argv[-1]).fillna('')
    to_replace = {'Mining-Unspecified' : 'Humate'} #Entries to be replaced
    if sys.argv[1] == 'setup':
        config = Setup(file)
        config.write_config(prefix)
    elif sys.argv[1] == 'num':
        num = NumberChecker(file)
        num.check_sd(file, standard_devation=3)
    else:
        do_check(file, prefix, to_replace)
        if sys.argv[1] == 'export':
            export_excel(file, to_replace)
    print('Done')


if __name__ == '__main__':
    main()
