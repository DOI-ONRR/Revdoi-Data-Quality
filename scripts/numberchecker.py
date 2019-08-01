from pathlib import Path
import json
import os
import sys
import pandas as pd


__author__ = 'Edward Chang'


def get_prefix(name):
    '''For naming config files

    Keyword Arguments:
        name -- Name of the Excel file
    '''
    lower = str(name).lower()
    prefixes = ['cy', 'fy', 'monthly', 'company', 'federal', 'native',
                'production', 'revenue', 'disbursements']
    final_prefix = ''
    for string in prefixes:
        if string in lower:
            final_prefix += string
    return final_prefix


# Setup Stuff
def get_num_col(df):
    '''Returns the last column (numbers) in a given DataFrame

    Keyword Arguments:
        df -- A Pandas DataFrame
    '''
    if df.columns.contains('Revenues'):
        return 'Revenues'
    else:
        return df.columns[-1]


def get_sd(grouped_df, sd):
    '''Calculates default standard deviation

    Keyword Arguments:
        grouped_df -- A grouped Pandas DataFrame
        sd -- Multiplier for standard deviation
    '''
    from math import isnan

    sd_dict = {}
    for item, item_df in grouped_df:
        item = str(item)
        col = get_num_col(item_df)
        if item == '':
            continue
        mean = item_df[col].mean()
        std = item_df[col].std() * sd
        if isnan(std):
            sd_dict[item] = (item_df[col].min(), item_df[col].max())
        else:
            sd_dict[item] = (mean - std, mean + std)
    return sd_dict


def make_config_path():
    '''Creates directory "config" if it does not exist'''
    if not os.path.exists('num-config'):
        print('No Num-Config Folder found. Creating folder...')
        os.mkdir('num-config')


def print_cols(df):
    '''Prints out the columns in a given DataFrame

    Keyword Arguments:
        df -- A Pandas DataFrame
    '''
    print('Available Columns:', list(df.columns)[:-1], '\n')


def get_col_input(df):
    print_cols(df)
    return input('Please type in the columns you want to group by. (Exclude quotes)\n\
Seperate the columns by commas followed by a space ", "\nYour input here -> ').split(', ')


def write_config(df, prefix):
    '''Writes a json file with columns to groupby and default sd
    '''
    with open('num-config/sd-' + prefix + '.json', 'w') as file:
        group_by = get_col_input(df)
        df_grouped = df.groupby(group_by)
        config = {
            'groups' : group_by,
            'sd_dict' : get_sd(df_grouped, 3)
        }
        make_config_path()
        json.dump(config, file, indent=4)
        print('Default SD written to file')


def update_config(df, prefix):
    ''' Reads json file for list of Columns
    Will create new SD-Dictionary based on new groups
    '''
    groups = read_config(prefix)[0]
    df_grouped = df.groupby(groups)
    with open('num-config/sd-' + prefix + '.json', 'w') as file:
        config = {
            'groups' : groups,
            'sd_dict' : get_sd(df_grouped, 3)
        }
        json.dump(config, file, indent=4)
        print('Groups have been updated')


# Runtime Stuff
def read_config(prefix):
    '''Returns list of columns and sd-Dictionary'''
    with open('num-config/sd-' + prefix + '.json', 'r') as file:
        config = json.load(file)
        return config['groups'], config['sd_dict']


def check_threshold(df, prefix):
    '''Compares values of number column to sd-dict'''
    groups, sd_dict = set_groups(df, prefix)
    column = get_num_col(df)
    cells = []
    for item, item_df in groups:
        item = str(item)
        if item == '':
            continue
        min_sig = sd_dict[item][0]
        max_sig = sd_dict[item][1]
        deviations = []
        for row in item_df.index:
            value = df.loc[row, column]
            if value in ('W', 'Withheld'):
                continue
            elif value < min_sig:
                deviations.append('Low Value Row ' +  str(row) + ': ' + str(value))
                cells.append(row)
            elif value > max_sig:
                deviations.append('High Value Row ' +  str(row) + ': ' + str(value))
                cells.append(row)
        if deviations:
            sep_line = '-' * len(item)
            print(sep_line + '\n' + item + '\n' + sep_line)
            for d in deviations:
                print(d)
    return cells


def set_groups(df, prefix):
    try:
        config = read_config(prefix)
        return df.groupby(config[0]), config[1]
    except FileNotFoundError:
        print('No SD-Config found. Will run setup\n')
        write_config(df, prefix)
        config = read_config(prefix)
    return df.groupby(config[0]), config[1]


def write_export(df, cells, pathname):
    col = get_num_col(df)
    cindex = df.columns.get_loc(col) + 1
    writer = pd.ExcelWriter('../output/number/NumChecked-' + pathname.stem + '.xlsx', engine='xlsxwriter')

    df.to_excel(writer, sheet_name='Sheet1', index=True)
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    highlight_fmt = workbook.add_format({'font_color': '#FF0000', 'bg_color':'#B1B3B3'})

    for row in cells:
        value = df.loc[row, col]
        worksheet.write(row + 1, cindex, value, highlight_fmt)

    writer.save()

    print('\nDone. Exported NumberCheck to ' + str(Path.cwd()) +
          '\\output\\number\\NumChecked-' + pathname.stem + '\n')


# Main
if __name__ == '__main__':
    path = Path(sys.argv[-1])
    c_prefix = get_prefix(path)
    to_check = pd.read_excel(path).replace({'W' : 0, 'Withheld' : 0})
    to_check.dropna(how='all', inplace=True)
    if sys.argv[1] == 'setup':
        make_config_path()
        write_config(to_check, c_prefix)
    elif sys.argv[1] == 'update':
        update_config(to_check, c_prefix)
    else:
        to_highlight = check_threshold(to_check, c_prefix)
        write_export(to_check, to_highlight, path)

    print('Done')
