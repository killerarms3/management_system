from django.db import models
from contract.models import Box
from django.urls import reverse
from django.core.validators import MinValueValidator
from lib.Validator import ValidateDate
from decimal import Decimal
# project
# Create your models here.
class MicrobioRx(models.Model):
    box = models.OneToOneField(Box, on_delete='CASCADE')
    dna_concentration = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    report_complete_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.id])

class Next_Generation_Sequencing(models.Model):
    box = models.OneToOneField(Box, on_delete='CASCADE')
    report_complete_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.id])

class GenoHealth(models.Model):
    box = models.OneToOneField(Box, on_delete='CASCADE')
    dna_concentration = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    od_260_230 = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    od_260_280 = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    report_complete_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.id])

class Probiotics1(models.Model):
    box = models.OneToOneField(Box, on_delete='CASCADE')
    pathway = models.CharField(max_length=16, choices=[('',''),('IL-4','IL-4'), ('IFNr','IFNr'), ('IL-10','IL-10')], blank=True, null=True)
    report_complete_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    report_delivery_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    probiotics_delivery_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.id])

class Probiotics2(models.Model):
    box = models.OneToOneField(Box, on_delete='CASCADE')
    dna_concentration = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    report_complete_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    report_delivery_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    probiotics_delivery_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.id])

