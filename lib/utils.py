from django.apps import apps
from django.db import ProgrammingError
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django import forms
from django.db.models import Q
from language.models import Code
from experiment.models import Experiment
from contract.models import Box
import datetime
from django.shortcuts import render
from collections import namedtuple, OrderedDict
from functools import reduce
import time

def getlabels(AppName, ModelName):
    field_tags = dict()
    Model = apps.get_model(AppName, ModelName)
    field_names = [field.name for field in Model._meta.fields]
    try:
        contenttype = ContentType.objects.get(app_label=AppName, model=ModelName)
    except ProgrammingError:
        contenttype = None
    for field_name in field_names:
        field_tags[field_name] = field_name
        if contenttype is not None:
            codes = Code.objects.filter(content_type=contenttype, code=field_name)
            if codes:
                field_tags[field_name] = codes[0].name
    return field_tags

def GetCustomWidgets(Model):
    widgets = dict()
    for field in Model._meta.fields:
        if field.get_internal_type() == 'DateField':
            widgets[field.name] = forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'id': field.name,
                    'min': '1820-01-01',
                    'max': datetime.datetime.now().strftime('%Y-%m-%d')
                },
            )
    return widgets

def GetHandsontableColumns(form):
    colHeaders = list()
    columns = list()
    field_names = list()
    for visible in form.visible_fields():
        colHeaders.append('* ' + visible.label if visible.field.required else visible.label)
        field_names.append(visible.name)
        column = {
            'data': visible.label,
            'allowEmpty': 'false' if visible.field.required else 'true',
        }
        if visible.field.widget.__class__.__name__ in {'Select', 'SelectMultiple'}:
            column['type'] = 'autocomplete'
            column['source'] = [option[1] for option in visible.field.widget.choices]
            column['allowInvalid'] = 'false'
            column['strict'] = 'true'
        elif visible.field.widget.__class__.__name__ == 'DateInput':
            column['type'] = 'date'
            column['dateFormat'] = 'YYYY-MM-DD'
        elif visible.field.widget.__class__.__name__ == 'NumberInput':
            column['type'] = 'numeric'
        else:
            column['type'] = 'text'
        columns.append(column)
    return field_names, colHeaders, columns

class AddMultiple():
    def __init__(self, request, form):
        self.request = request
        self.form = form
        self.field_names = None

    def AddMultipleView(self, header, view_url, add_multiple_url):
        field_names, colHeaders, columns = GetHandsontableColumns(self.form)
        self.field_names = field_names
        return render(self.request, 'add_multiple.html', locals())

def get_status(box_id):
    lab_list = ['國立台灣大學生物科技學研究所']
    sequencing_list = ['中央研究院', '卡尤迪生物科技', '基龍米克斯生物科技股份有限公司', '豐技生物科技股份有限公司']
    # 預設status
    status = '採樣盒製作中'
    box = Box.objects.get(id=box_id)
    experiments = Experiment.objects.filter(box=box)
    if box.tracing_number:
        status = '採樣盒製作完成'
    # 實驗室收到紀錄(抓第一筆)
    experiment = experiments.filter(organization__name__in=lab_list).first()
    if experiment:
        if experiment.receiving_date:
            if experiment.box.plan.product.name in {'精準化益生菌1.0', '精準化益生菌2.0'}:
                status = '配對中'
                if experiment.complete_date:
                    status = '配對完成'
            else:
                status = 'DNA萃取中'
                if experiment.complete_date:
                    status = 'DNA萃取完成'
    experiment = experiments.filter(transfer_organization__name__in=sequencing_list).first()
    if experiment:
        if experiment.data_transfer_date:
            status = '定序中'
            experiment = experiments.filter(organization__name__in=sequencing_list).first()
            if experiment and experiment.complete_date:
                status = '定序完成'
    experiment = experiments.filter(organization__department='研究發展部').first()
    if experiment:
        if experiment.receiving_date:
            status = '分析中'
            if experiment.complete_date:
                status = '分析完成'
    return status

class DataTablesServer():
    def __init__(self, request, columns, queryset, datadict=None):
        self.columns = columns
        self.request = request
        self.request_values = request.GET
        self.queryset = queryset
        self.datadict = datadict
        self.resultdata = None
        self.resultset = self.queryset
        self.cadinalityFiltered = 0
        self.cadinality = 0
        # self.runQueries()
        # self.outputResult()

    def getData(self, request, queryset):
        # 跟queryset同順序
        Data = dict()
        for q_set in queryset:
            data = []
            for column in self.columns:
                if column == '__str__':
                    data.append(str(q_set))
                elif '()' in column:
                    # 只接受最後一個是()
                    data.append(str(reduce(getattr, column[:-2].split('.'), q_set)()))
                else:
                    data.append(str(reduce(getattr, column.split('.'), q_set)))
            Data[q_set.id] = data
        return Data

    def outputResult(self):        
        output = OrderedDict()
        output['draw'] = str(int(self.request_values['draw']))
        output['recordsTotal'] = str(self.cardinality)
        output['recordsFiltered'] = str(self.cadinalityFiltered)
        output['data'] = list()
        for row in self.resultdata:
            output['data'].append(row)
        return output

    def runQueries(self):
        if self.filtering() or self.ordering():
            self.datadict = self.getData(request=self.request, queryset=self.queryset)
            self.resultdata = self.datadict.values()
        if self.filtering():
            for query in self.filtering():
                filterData_id = []
                for q_set in self.resultset:
                    if query[0]:
                        # or
                        if any(query[2] in data for data in self.datadict[q_set.id]):
                            filterData_id.append(q_set.id)
                    elif (not query[0]) and (query[2] in self.datadict[q_set.id][query[1]]):
                        # and
                        filterData_id.append(q_set.id)
                self.resultset = self.resultset.filter(id__in=filterData_id)
            filterData_id = self.resultset.values_list('id', flat=True)
            self.resultdata = [self.datadict[q_id] for q_id in self.datadict if q_id in filterData_id]

        if self.ordering() is not None:
            self.resultdata = sorted(self.resultdata, key=lambda data: data[self.ordering()[1]], reverse=self.ordering()[0])[self.paging().start: self.paging().start+self.paging().length]
        elif self.resultdata is not None:
            self.resultdata = self.resultdata[self.paging().start: self.paging().start+self.paging().length]
        else:
            self.resultdata = self.getData(request=self.request, queryset=self.queryset[self.paging().start: self.paging().start+self.paging().length]).values()
        # Total records, before filtering
        self.cardinality = len(self.queryset)
        # Total records, after filtering
        self.cadinalityFiltered = len(self.resultset)

    def filtering(self):
        search = []
        # (is_or, column_id, target_value)
        if ( 'search[value]' in self.request_values ) and (self.request_values['search[value]'] != '' ):
            search.append((True, None, self.request_values['search[value]']))
        for i in range(len(self.columns)):
            key = 'columns['+str(i)+'][search][value]'
            if (key in self.request_values) and (self.request_values[key] != ''):
                search.append((False, i, self.request_values[key]))
        return search

    def ordering(self):
        # (is_reverse, idx)
        if (self.request_values['order[0][column]'] != '') and (int(self.request_values['order[0][column]']) > 0):
            if self.request_values['order[0][dir]'] == 'asc':
                return (False, int(self.request_values['order[0][column]']))
            else:
                return (True, int(self.request_values['order[0][column]']))

    def paging(self):
        pages = namedtuple('pages', ['start', 'length'])
        if (self.request_values['start'] != "" ) and (self.request_values['length'] != -1 ):
            pages.start = int(self.request_values['start'])
            pages.length = int(self.request_values['length'])
        return pages