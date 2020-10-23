from django import forms
from django.forms import widgets
from django.forms import ModelChoiceField
from language.models import Code
from contract.models import Box
from product.models import Product, Plan
from django.apps import apps
import datetime
from lib import utils
from django.contrib.contenttypes.models import ContentType

class ProductCreateForm(forms.ModelForm):
    product_labels = utils.getlabels('product', 'product')
    status = forms.ChoiceField(label=product_labels['status'], choices=[('1','Available'),('0','Unavilable')], required=True)
    project = forms.ModelChoiceField(label='產品大表', queryset=ContentType.objects.filter(app_label='project'), required=False)

    def __init__(self, *args, **kwargs):
        super(ProductCreateForm, self).__init__(*args, **kwargs)
        if not self.instance.id:
            self.fields.pop('status')

        for visible in self.visible_fields():
            if visible.field.widget.__class__.__name__ == 'Select':
                visible.field.widget.attrs['class'] = 'multiple-select'
            else:
                visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Product
        fields = '__all__'
        labels = utils.getlabels('product', 'product')


class PlanCreateForm(forms.ModelForm):
    plan_labels = utils.getlabels('product', 'plan')
    product = forms.ModelChoiceField(label=plan_labels['product'], queryset=Product.objects.all(), required=True)
    price = forms.IntegerField(label=plan_labels['price'], widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}), required=True)
    status = forms.ChoiceField(label=plan_labels['status'], choices=[('1','Available'),('0','Unavilable')], required=True)

    def __init__(self, *args, **kwargs):
        super(PlanCreateForm, self).__init__(*args, **kwargs)
        if not self.instance.id:
            self.fields.pop('status')
            self.fields['product'].queryset = Product.objects.filter(status=True)
        for visible in self.visible_fields():
            if visible.field.widget.__class__.__name__ == 'Select':
                visible.field.widget.attrs['class'] = 'multiple-select'
            else:
                visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Plan
        fields = '__all__'
        labels = utils.getlabels('product', 'plan')