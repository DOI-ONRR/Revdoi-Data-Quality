# Credit to Matthew Kudija for the Source Code
# Link: https://matthewkudija.com/blog/2018/07/21/excel-diff/
import os
import pandas as pd
from pathlib import Path


def excel_diff(path_OLD, path_NEW):

    df_OLD = pd.read_excel("files/monthly_production_05-2019.xlsx").fillna(0)
    df_NEW = pd.read_excel("files/mothpro2019.xlsx").fillna(0)

    # Perform Diff
    dfDiff = df_NEW.copy()
    droppedRows = []
    newRows = []
    changedRows = []

    cols_OLD = df_OLD.columns
    cols_NEW = df_NEW.columns
    sharedCols = list(set(cols_OLD).intersection(cols_NEW))

    for row in dfDiff.index:
        if (row in df_OLD.index) and (row in df_NEW.index):
            for col in sharedCols:
                value_OLD = df_OLD.loc[row,col]
                value_NEW = df_NEW.loc[row,col]
                if value_OLD==value_NEW:
                    dfDiff.loc[row,col] = df_NEW.loc[row,col]
                else:
                    dfDiff.loc[row,col] = ('{}→{}').format(value_OLD,value_NEW)
                    changedRows.append(row)
        else:
            newRows.append(row)

    for row in df_OLD.index:
        if row not in df_NEW.index:
            droppedRows.append(row)
            dfDiff = dfDiff.append(df_OLD.loc[row,:])

    dfDiff = dfDiff.sort_index().fillna('')
    print(dfDiff)
    print('\nNew Rows:     {}'.format(newRows))
    print('Dropped Rows: {}'.format(droppedRows))
    print('Changed Rows: {}'.format(changedRows))

    # Save output and format
    fname = '{} vs {}.xlsx'.format(path_OLD.stem,path_NEW.stem)
    writer = pd.ExcelWriter(fname, engine='xlsxwriter')

    dfDiff.to_excel(writer, sheet_name='DIFF', index=True)
    df_NEW.to_excel(writer, sheet_name=path_NEW.stem, index=True)
    df_OLD.to_excel(writer, sheet_name=path_OLD.stem, index=True)

    # get xlsxwriter objects
    workbook  = writer.book
    worksheet = writer.sheets['DIFF']
    worksheet.hide_gridlines(2)
    worksheet.set_default_row(15)

    # define formats
    date_fmt = workbook.add_format({'align': 'center', 'num_format': 'yyyy-mm-dd'})
    center_fmt = workbook.add_format({'align': 'center'})
    number_fmt = workbook.add_format({'align': 'center', 'num_format': '#,##0.00'})
    cur_fmt = workbook.add_format({'align': 'center', 'num_format': '$#,##0.00'})
    perc_fmt = workbook.add_format({'align': 'center', 'num_format': '0%'})
    grey_fmt = workbook.add_format({'font_color': '#E0E0E0'})
    highlight_fmt = workbook.add_format({'font_color': '#4286F4', 'bg_color':'#EDEAEA'})
    new_fmt = workbook.add_format({'font_color': '#529973','bold':True})

    # set format over range
    ## highlight changed cells
    worksheet.conditional_format('A1:ZZ1000', {'type': 'text',
                                            'criteria': 'containing',
                                            'value':'→',
                                            'format': highlight_fmt})

    # highlight new/changed rows
    for row in range(dfDiff.shape[0]):
        if row+1 in newRows:
            worksheet.set_row(row+1, 15, new_fmt)
        if row+1 in droppedRows:
            worksheet.set_row(row+1, 15, highlight_fmt)

    # save
    writer.save()
    print('\nDone. Exported DIFF to ' + os.getcwd() + '\\' + fname + '\n')


def main():
    path_OLD = Path('files/monthly_production_05-2019.xlsx')
    path_NEW = Path('files/mothpro2019.xlsx')

    # get index col from data
    df = pd.read_excel(path_NEW)

    excel_diff(path_OLD, path_NEW)


if __name__ == '__main__':
    main()
