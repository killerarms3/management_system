from django.db import models
from contract.models import Box
from accounts.models import Organization
from django.urls import reverse
from lib.Validator import ValidateDate, ValidateAfterDate
from django.core.exceptions import ValidationError
import datetime

# Create your models here.
class Experiment(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    organization = models.ForeignKey(Organization, on_delete='CASCADE')
    receiving_date = models.DateField(validators=[ValidateDate])
    complete_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    data_transfer_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    transfer_organization = models.ForeignKey(Organization, on_delete='CASCADE', related_name='transfer_organization')

    def clean(self):
        errors = dict()
        try:
            self.clean_fields()
        except ValidationError as err:
            errors.update(err.message_dict)
        if not self.complete_date:
            self.complete_date = None
        elif self.receiving_date and not ValidateAfterDate(self.receiving_date, self.complete_date):
            if 'complete_date' not in errors:
                errors['complete_date'] = list()
            errors['complete_date'].append('完成日不可在收到日之前')
        if not self.data_transfer_date:
            self.data_transfer_date = None
        elif self.receiving_date and not ValidateAfterDate(self.receiving_date, self.data_transfer_date):
            if 'data_transfer_date' not in errors:
                errors['data_transfer_date'] = list()
            errors['data_transfer_date'].append('移交日不可在收到日之前')
        elif self.complete_date and not ValidateAfterDate(self.complete_date, self.data_transfer_date):
            if 'data_transfer_date' not in errors:
                errors['data_transfer_date'] = list()
            errors['data_transfer_date'].append('移交日不可在完成日之前')
        raise ValidationError(errors)
    def get_absolute_url(self):
        return reverse("experiment:view_specific_experiment", args=[self.box.serial_number])

