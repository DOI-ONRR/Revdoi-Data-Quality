# Credit to Matthew Kudija for the Source Code
# https://matthewkudija.com/blog/2018/07/21/excel-diff/
import pandas as pd
import tkinter as tk
from tkinter import StringVar, filedialog
from pathlib import Path


def excel_diff(path_OLD, path_NEW):

    df_OLD = pd.read_excel(path_OLD).fillna(0)
    df_NEW = pd.read_excel(path_NEW).fillna(0)

    # Perform Diff
    dfDiff = df_NEW.copy()
    droppedRows = []
    newRows = []
    changedCells = []
    exclusionSet = {"Volume", "Revenue"}

    cols_OLD = set(df_OLD.columns) - exclusionSet
    cols_NEW = set(df_NEW.columns) - exclusionSet
    sharedCols = list(cols_OLD & cols_NEW)
    newCols = list(cols_NEW - cols_OLD)
    droppedCols = list(cols_OLD - cols_NEW)

    for row in dfDiff.index:
        if (row in df_OLD.index) and (row in df_NEW.index):
            for col in sharedCols:
                value_OLD = df_OLD.loc[row,col]
                value_NEW = df_NEW.loc[row,col]
                if value_OLD==value_NEW:
                    dfDiff.loc[row,col] = df_NEW.loc[row,col]
                else:
                    dfDiff.loc[row,col] = ('{}→{}').format(value_OLD,value_NEW)
                    changedCells.append(chr(65 + sharedCols.index(col) + 1) + str(row))
        else:
            newRows.append(row)

    for row in df_OLD.index:
        if row not in df_NEW.index:
            droppedRows.append(row)
            dfDiff = dfDiff.append(df_OLD.loc[row,:])

    dfDiff = dfDiff.sort_index().fillna('')
    output_string = '\nNew Rows: {}'.format(newRows) + '\nDropped Rows: {}'.format(droppedRows)
    if len(changedCells) <= 20:
        output_string += '\nChanged Cells: {}'.format(changedCells)
    else:
        print("There are a lot of changed cells. Will only display length")
        output_string += '\nChanged Cells: {} changed cells'.format(len(changedCells))
    output_string += '\nNew Columns: {}'.format(newCols)
    output_string += '\nDropped Columns: {}\n'.format(droppedCols)

    # Save output and format
    fname = '{} vs {}.xlsx'.format(path_OLD.stem,path_NEW.stem)
    writer = pd.ExcelWriter('../output/diff/' + fname, engine='xlsxwriter')

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
    highlight_fmt = workbook.add_format({'font_color': '#FF0000', 'bg_color':'#B1B3B3'})
    new_fmt = workbook.add_format({'font_color': '#32CD32','bold':True})

    # set format over range
    ## highlight changed cells
    end = 'ZZ' + str(len(dfDiff))
    worksheet.conditional_format('A1:'+ end, {'type': 'text',
                                            'criteria': 'containing',
                                            'value':'→',
                                            'format': highlight_fmt})

    # highlight new/changed rows
    for row in range(dfDiff.shape[0]):
        if row+1 in newRows:
            worksheet.set_row(row+2, 15, new_fmt)
        if row+1 in droppedRows:
            worksheet.set_row(row+2, 15, grey_fmt)

    # save
    writer.save()

    return output_string + '\nExported DIFF to ' + str(Path.cwd()) + '\\output\\' + fname + '\n'


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.old = StringVar()
        self.new = StringVar()
        self.output = StringVar()
        self.padx = 5
        self.pady = 10
        self.entry_width = 94
        self.grid()
        self.create_widgets()

    def create_widgets(self):

        old_file = tk.Button(self)
        old_file["text"] = "Select Old File"
        old_file["command"] = self.set_old
        old_file.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        old_label = tk.Entry(self, textvariable=self.old)
        old_label.config(width=self.entry_width)
        old_label.grid(row=0, column=1)

        new_file = tk.Button(self)
        new_file["text"] = "Select new File"
        new_file["command"] = self.set_new
        new_file.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        new_label = tk.Entry(self, textvariable=self.new)
        new_label.config(width=self.entry_width)
        new_label.grid(row=1, column=1)

        run_diff = tk.Button(self)
        run_diff["text"] = "Run DIFF"
        run_diff["command"] = self.start_diff
        run_diff.grid(row=2, column=0, padx=self.padx, pady=self.pady)

        run_msg = tk.Message(self, textvariable=self.output, width=200, relief="solid", bg="white")
        run_msg.grid(row=2, column=1)

    def start_diff(self):
        try:
            results = excel_diff(Path(self.old.get()), Path(self.new.get()))
            print(results)
            self.output.set("Done. Check the console for the results")
        except PermissionError:
            error_msg = '[ERROR] Could not find file(s). Are both paths valid?'
            self.output.set(error_msg)

    def set_old(self):
        self.old.set(self.get_file())
        self.output.set("Old File Set")

    def set_new(self):
        self.new.set(self.get_file())
        self.output.set("New File Set")

    def get_file(self):
        path = filedialog.askopenfilename(initialdir = '../input',
                                          title = "Select file",
                                          filetypes = (("xlsx files","*.xlsx"),("all files","*.*")))
        return path


if __name__ == '__main__':
    root = tk.Tk()
    root.minsize(500, 100)
    app = Application(master=root)
    app.mainloop()
