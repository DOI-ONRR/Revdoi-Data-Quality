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
    lower = name.lower()
    prefixes = ['cy', 'fy', 'monthly', 'company', 'federal', 'native',
                'production', 'revenue', 'disbursements']
    final_prefix = ''
    for string in prefixes:
        if string in lower:
            final_prefix += string
    return final_prefix


'''----- Setup Stuff -----'''
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
    from math import isnan
    '''Calculates default standard deviation

    Keyword Arguments:
        grouped_df -- A grouped Pandas DataFrame
        sd -- Multiplier for standard deviation
    '''
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
    print('Available Columns:', list(df.columns)[:-1], end="\n")


def get_col_input(df):
    print_cols(df)
    return input('Please type in the columns you want to group by. (Exclude quotes)\n\
Seperate the columns by commas followed by a space ", "\n').split(', ')


def write_config(df, prefix):
    '''Writes a json file with columns to groupby and default sd
    '''
    with open('num-config/sd-' + prefix + '.json', 'w') as file:
        group_by = get_col_input(df)
        sorted = df.groupby(group_by)
        config = {
            'groups' : group_by,
            'sd_dict' : get_sd(sorted, 3)
        }
        make_config_path()
        json.dump(config, file, indent=4)
        print('Default SD written to file')


def update_config(df, prefix):
    groups = read_config()[0]
    sorted = df.groupby(groups)
    with open('num-config/sd-' + prefix + '.json', 'w') as file:
        config = {
            'groups' : groups,
            'sd_dict' : get_sd(sorted, 3)
        }
        json.dump(config, file, indent=4)
        print('Groups have been updated')


'''----- Runtime Stuff -----'''
def read_config(prefix):
    with open('num-config/sd-' + prefix + '.json', 'r') as file:
        config = json.load(file)
        return config['groups'], config['sd_dict']


def check_threshold(df, prefix, read_type='dict'):
    groups, sd_dict = set_groups(read_type, prefix)
    column = get_num_col(df)
    for item, item_df in groups:
        item = str(item)
        if item == '':
            continue
        min_sig = sd_dict[item][0]
        max_sig = sd_dict[item][1]
        deviations = []
        for row in item_df.index:
            value = df.loc[row, column]
            if value == 'W' or value == 'Withheld':
                continue
            if value < min_sig or value > max_sig:
                deviations.append('Row ' +  str(row) + ': ' + str(value))
        if deviations:
            print('------------------\n' + item + '\n------------------')
            for d in deviations:
                print(d)


def set_groups(read_type, prefix):
    groups = []
    # Read json file. config[0] = group_by, config[1] = sd_dict
    if read_type == 'dict':
        config = read_config(prefix)
        return df.groupby(config[0]), config[1]
    else:
        groups = df.groupby(get_col_input(df))
        return groups, get_sd(groups, 3)


'''----- Main -----'''
if __name__ == '__main__':
    prefix = get_prefix(sys.argv[-1])
    df = pd.read_excel(sys.argv[-1]).replace({'W' : 0, 'Withheld' : 0})
    df.dropna(how='all', inplace=True)
    if sys.argv[1] == 'setup':
        make_config_path()
        write_config(df, prefix)
    elif sys.argv[1] == 'update':
        update_config(df, prefix)
    else:
        check_threshold(df, prefix)
    print('Done')
