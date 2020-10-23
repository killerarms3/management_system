from django import forms
from django.forms import widgets
from django.forms import ModelChoiceField
from language.models import Code
from customer.models import Organization, Customer, Customer_Organization, Title, Job, Customer_Type, Relationship
from django.apps import apps
import datetime
from lib import utils
from lib.Validator import ValidateTelNumber, ValidateMobileNumber
from django.contrib.contenttypes.models import ContentType


class CustomerCreateForm(forms.ModelForm):
    customer_labels = utils.getlabels('customer', 'customer')
    birth_date = forms.DateField(label=customer_labels['birth_date'],
    widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'birth_date',
                'min': '1820-01-01',
                'max': datetime.datetime.now().strftime('%Y-%m-%d')
            }), required=False)
    organization = forms.ModelMultipleChoiceField(label='機構', queryset=Organization.objects.all(), required=False)
    email = forms.EmailField(label=customer_labels['email'], required=False)
    tel = forms.CharField(label=customer_labels['tel'], validators=[ValidateTelNumber], required=False)
    mobile = forms.CharField(label=customer_labels['mobile'], validators=[ValidateMobileNumber], required=False)
    introducer = forms.ModelChoiceField(label='推薦人', queryset=Customer.objects.all(), required=False)
    relationship = forms.ModelChoiceField(label='關係', queryset=Relationship.objects.all(), required=False)
    field_order = ['last_name', 'first_name', 'birth_date', 'organization', 'title', 'job', 'line_id', 'email', 'tel', 'mobile', 'address', 'customer_type', 'memo']
    def __init__(self, *args, **kwargs):
        super(CustomerCreateForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            if visible.field.widget.__class__.__name__ == 'Select' or visible.field.widget.__class__.__name__ == 'SelectMultiple':
                visible.field.widget.attrs['class'] = 'multiple-select'
            else:
                visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Customer
        fields = '__all__'
        labels = utils.getlabels('customer', 'customer')
        widgets = utils.GetCustomWidgets(Customer)
