from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django import forms
from language.models import Code
import datetime

def getlabels(AppName, ModelName):
    field_tags = dict()
    Model = apps.get_model(AppName, ModelName)
    field_names = [field.name for field in Model._meta.fields]
    contenttype = ContentType.objects.get(app_label=AppName, model=ModelName)
    for field_name in field_names:
        field_tags[field_name] = field_name
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
        colHeaders.append(visible.label)
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
