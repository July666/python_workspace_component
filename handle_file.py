#!/usr/bin/python
# coding=utf-8
import xlrd
import openpyxl


def read_excel_xlsx(path, sheet_name):

    workbook = openpyxl.load_workbook(path)
    sheet = workbook[sheet_name]
    list_rows = []

    for row in sheet.rows:
        list_cells = []
        for cell in row:
            list_cells.append(cell.value)
        list_rows.append(list_cells)
    print(list_rows[1:])
    print('*************')
    return list_rows[1:]

read_excel_xlsx('documents/server_info.xlsx', 'Sheet1')
