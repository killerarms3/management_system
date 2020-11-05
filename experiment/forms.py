from django import forms
from django.forms import widgets
from django.forms import ModelChoiceField
from accounts.models import Organization
from experiment.models import Experiment
from django.apps import apps
import datetime
from lib import utils

class ExperimentCreateForm(forms.ModelForm):
    experiment_labels = utils.getlabels('experiment', 'experiment')
    organization = forms.ModelChoiceField(label=experiment_labels['organization'], queryset=Organization.objects.all())
    transfer_organization = forms.ModelChoiceField(label=experiment_labels['transfer_organization'], queryset=Organization.objects.all())

    def __init__(self, *args, **kwargs):
        super(ExperimentCreateForm, self).__init__(*args, **kwargs)
        if not self.instance.id:
            self.fields['organization'].queryset = Organization.objects.filter(is_active=True)
            self.fields['transfer_organization'].queryset = Organization.objects.filter(is_active=True)

        for visible in self.visible_fields():
            if visible.field.widget.__class__.__name__ == 'Select' or visible.field.widget.__class__.__name__ == 'SelectMultiple':
                visible.field.widget.attrs['class'] = 'multiple-select'
            else:
                visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Experiment
        fields = '__all__'
        labels = utils.getlabels('experiment', 'experiment')
        widgets = utils.GetCustomWidgets(Experiment)
