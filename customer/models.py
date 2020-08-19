from django.db import models
from product.models import Product

# Create your models here.
class Customer(models.Model):
    last_name = models.CharField(max_length=32)
    first_name = models.CharField(max_length=32)
    birth_date = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=32, blank=True, null=True)
    email = models.CharField(max_length=320, blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    address = models.CharField(max_length=320, blank=True, null=True)
    memo = models.TextField(max_length = 1000, blank=True, null=True)

    def __str__(self):
        return self.last_name + ', ' + self.first_name

class Feedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete='CASCADE')
    product = models.ForeignKey(Product, on_delete='CASCADE')
    feedback = models.TextField()
    feedback_date = models.DateField()

class Organization(models.Model):
    name = models.CharField(max_length=256)
    department = models.CharField(max_length=256)

    def __str__(self):
        return self.name + ', ' + self.department

class Customer_Organization(models.Model):
    customer = models.ForeignKey(Customer, on_delete='CASCADE')
    organization = models.ForeignKey(Organization, on_delete='CASCADE')