from django.db import models
from contract.models import Box
from django.urls import reverse
# project
# Create your models here.
class MicrobioRx(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    dna_concentration = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    report_complete_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.serial_number])

class Next_Generation_Sequencing(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    report_complete_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.serial_number])

class GenoHealth(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    dna_concentration = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    od_260_230 = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    od_260_280 = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    report_complete_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.serial_number])

class Probiotics1(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    pathway = models.CharField(max_length=16, blank=True, null=True)
    report_complete_date = models.DateField(blank=True, null=True)
    report_delivery_date = models.DateField(blank=True, null=True)
    probiotics_delivery_date = models.DateField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.serial_number])

class Probiotics2(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    dna_concentration = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    report_complete_date = models.DateField(blank=True, null=True)
    report_delivery_date = models.DateField(blank=True, null=True)
    probiotics_delivery_date = models.DateField(blank=True, null=True)
<<<<<<< HEAD
    memo = models.TextField(blank=True, null=True)
=======
    memo = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("project:view_specific_data", args=[self.__class__.__name__.lower(), self.box.serial_number])

>>>>>>> 1b9e22db940c62d6b380ee395c71f84b4fcecffe
