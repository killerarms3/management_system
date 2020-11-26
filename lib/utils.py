from django.apps import apps
from django.db import ProgrammingError
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django import forms
from language.models import Code
from experiment.models import Experiment
from contract.models import Box
import datetime
from django.shortcuts import render

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