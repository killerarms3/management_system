from django import forms
from django.forms import widgets
from django.forms import ModelChoiceField
from language.models import Code
from contract.models import Box
from product.models import Project, Plan
from project.models import Probiotics1
from django.apps import apps
import datetime
from django.contrib.contenttypes.models import ContentType

def GetCustomWidgets(Model):
    widgets = dict()
    for field in Model._meta.fields:
        if field.get_internal_type() == 'DateField':
            widgets[field.name] = forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'id': field.name,
                    'min': '1820-01-01',
                    'max': datetime.datetime.now().strftime('%Y-%m-%d')
                },
            )
    return widgets

def ProjectBox(ModelName):
    contenttype = ContentType.objects.get(app_label='project', model=ModelName)
    products = Project.objects.filter(content_type=contenttype).values_list('product__id', flat=True)
    plans = Plan.objects.filter(product_id__in=list(products)).values_list('id', flat=True)
    boxes = Box.objects.filter(plan_id__in=list(plans))
    return boxes

def GetDataCreateForm(Model, Labels):
    class DataCreateForm(forms.ModelForm):
        box = forms.ModelChoiceField(queryset=ProjectBox(Model.__name__), required=True)
        if Model.__name__ == 'Probiotics1':
            pathway = forms.ChoiceField(choices=[('',''),('IL-4','IL-4'), ('IFNr','IFNr'), ('IL-10','IL-10')], required=False)
        def __init__(self, *args, **kwargs):
            super(DataCreateForm, self).__init__(*args, **kwargs)
            for visible in self.visible_fields():
                if visible.field.widget.__class__.__name__ == 'Select':
                    visible.field.widget.attrs['class'] = 'multiple-select'
                else:
                    visible.field.widget.attrs['class'] = 'form-control'

        class Meta:
            model = Model
            fields = '__all__'
            labels = Labels
            widgets = GetCustomWidgets(Model)
    return DataCreateForm
