from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=64)
    prefix = models.CharField(max_length=16)
    status = models.BooleanField(default=1)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product:view_product_plan', args=[str(self.id)])

class Plan(models.Model):
    product = models.ForeignKey(Product, on_delete='CASCADE')
    name = models.CharField(max_length=64)
    price = models.PositiveIntegerField()
    status = models.BooleanField(default=1)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.product.name + '-' + self.name

    def get_absolute_url(self):
        return reverse('product:view_specific_plan', args=[str(self.id)])

class Project(models.Model):
    product = models.ForeignKey(Product, on_delete='CASCADE')
    content_type = models.ForeignKey(ContentType, on_delete='CASCADE')
