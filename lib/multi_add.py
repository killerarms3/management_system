from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
import xlrd
from django.conf import settings
from django.shortcuts import HttpResponse
import os

class AddMultiData():
    def __init__(self, field_number):
        # 0-based
        # first sheet
        self.sheet_index = 0
        self.column_code_row_index = 4
        self.header_row_index = 5
        self.start_row_index = self.header_row_index + 1
        self.start_column_index = 1
        self.end_column_index = self.start_column_index + field_number
        self.date_format = '%Y-%m-%d'

        # self.header = header
        # self.sheet_template = sheet_template
        # self.action_url = action_url

    def view_upload(self, request, header, sheet_template, action_url):
        return render(request, 'add_multiple_data.html', locals())

    def read_upload(self, file_contents):
        wb = xlrd.open_workbook(filename=None, file_contents=file_contents)
        table = wb.sheets()[self.sheet_index]
        number_of_rows = table.nrows
        column_codes = table.row_values(self.column_code_row_index, self.start_column_index, self.end_column_index)
        column_names = table.row_values(self.header_row_index, self.start_column_index, self.end_column_index)
        column_dict = dict(zip(column_codes, column_names))
        data = list()
        for row_index in range(self.start_row_index, number_of_rows):
            row_values = list()
            for column_index in range(self.start_column_index, self.end_column_index):
                if table.cell_type(row_index, column_index) == xlrd.XL_CELL_DATE:
                    column_value = xlrd.xldate.xldate_as_datetime(table.cell(row_index, column_index).value, 0).strftime(self.date_format)
                else:
                    column_value = table.cell(row_index, column_index).value
                row_values.append(column_value)
            data_dict = dict(zip(column_codes, row_values))
            data_dict.update({'status': '', 'messages': list()})
            data.append(data_dict)
        return column_codes, column_dict, data

def download(request, filename):
    in_file = open(os.path.join(settings.BASE_DIR, 'templates', 'download', filename), 'rb')
    response = HttpResponse(in_file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % (filename)
    return response

