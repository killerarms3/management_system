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
from lib import utils

def ProjectBox(ModelName, exclude_exist=True):
    Model = apps.get_model('project', ModelName)
    contenttype = ContentType.objects.get(app_label='project', model=ModelName)
    products = Project.objects.filter(content_type=contenttype).values_list('product__id', flat=True)
    plans = Plan.objects.filter(product_id__in=list(products)).values_list('id', flat=True)
    if exclude_exist:
        boxes = Box.objects.filter(plan_id__in=list(plans)).exclude(id__in=list(Model.objects.all().values_list('box_id', flat=True)))
    else:
        boxes = Box.objects.filter(plan_id__in=list(plans))
    return boxes

def GetDataCreateForm(Model, exclude_exist=True):
    class DataCreateForm(forms.ModelForm):
        box = forms.ModelChoiceField(label='採樣盒', queryset=ProjectBox(Model.__name__, exclude_exist), required=True)
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
            labels = utils.getlabels('project', Model.__name__)
            widgets = utils.GetCustomWidgets(Model)
    return DataCreateForm
