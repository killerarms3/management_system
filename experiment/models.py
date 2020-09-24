from django.db import models
from contract.models import Box
from accounts.models import Organization
from django.urls import reverse

# Create your models here.
class Experiment(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    organization = models.ForeignKey(Organization, on_delete='CASCADE')
    receiving_date = models.DateField()
    complete_date = models.DateField(blank=True, null=True)
    data_transfer_date = models.DateField(blank=True, null=True)
    transfer_organization = models.ForeignKey(Organization, on_delete='CASCADE', related_name='transfer_organization')

    def get_absolute_url(self):
        return reverse("experiment:view_specific_experiment", args=[self.box.serial_number])