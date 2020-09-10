from django.db import models
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=256)
    status = models.BooleanField(default=1)

class Prefix(models.Model):
    name = models.CharField(max_length=16)

class Product_Prefix(models.Model):
    product = models.ForeignKey(Product, on_delete='CASCADE')
    prefix = models.ForeignKey(Prefix, on_delete='CASCADE')

class Plan(models.Model):
    product = models.ForeignKey(Product, on_delete='CASCADE')
    name = models.CharField(max_length=256)
    price = models.PositiveIntegerField()
    status = models.BooleanField(default=1)
    description = models.TextField(blank=True, null=True)

class Project(models.Model):
    product = models.ForeignKey(Product, on_delete='CASCADE')
    content_type = models.ForeignKey(ContentType, on_delete='CASCADE')