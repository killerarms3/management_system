from django.db import models
from contract.models import Box

# project
# Create your models here.
class MicrobioRx(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    dna_concentration = models.DecimalField(max_digits=7, decimal_places=2)
    report_complete_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

class Next_Generation_Sequencing(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    report_complete_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

class GenoHealth(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    dna_concentration = models.DecimalField(max_digits=7, decimal_places=2)
    od_260_230 = models.DecimalField(max_digits=7, decimal_places=2)
    od_260_280 = models.DecimalField(max_digits=7, decimal_places=2)
    report_complete_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

class Probiotics1(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    pathway = models.CharField(max_length=16, blank=True, null=True)
    report_complete_date = models.DateField(blank=True, null=True)
    report_delivery_date = models.DateField(blank=True, null=True)
    probiotics_delivery_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

class Probiotics2(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    dna_concentration = models.DecimalField(max_digits=7, decimal_places=2)
    report_complete_date = models.DateField(blank=True, null=True)
    report_delivery_date = models.DateField(blank=True, null=True)
    probiotics_delivery_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)