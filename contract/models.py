from django.db import models
from django.contrib.auth.models import User
from customer.models import Customer
from product.models import Plan


# Create your models here.
class Contract(models.Model):
    user = models.ForeignKey(User, on_delete='CASCADE')
    contract_date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete='CASCADE')
    organization_id = models.CharField(max_length=256, blank=True, null=True)
    expected_quantity = models.PositiveIntegerField(blank=True, null=True)
    order_id = models.CharField(max_length=256, blank=True, null=True)
    receipt_id = models.CharField(max_length=256, blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

class Payment_method(models.Model):
    name = models.CharField(max_length=32)

class Order(models.Model):
    order_date = models.DateField()
    contract = models.ForeignKey(Contract, on_delete='CASCADE')
    plan_id = models.CharField(max_length=256)
    quantity = models.CharField(max_length=256)
    memo = models.TextField(blank=True, null=True)

class Receipt(models.Model):
    contract = models.ForeignKey(Contract, on_delete='CASCADE')
    receipt_date = models.DateField(blank=True, null=True)
    receipt_number = models.CharField(max_length=32, blank=True, null=True)
    receipt_amount = models.PositiveIntegerField(blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.ForeignKey(Payment_method, on_delete='CASCADE')
    memo = models.TextField(blank=True, null=True)

class Failed_reason(models.Model):
    failed_reason = models.CharField(max_length=256)
    memo = models.TextField(blank=True, null=True)

class Box(models.Model):
    serial_number = models.CharField(max_length=256)
    order = models.ForeignKey(Order, on_delete='CASCADE')
    plan = models.ForeignKey(Plan, on_delete='CASCADE')
    tracing_number = models.CharField(max_length=64, blank=True, null=True)

class Failed(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    failed_reason = models.ForeignKey(Failed_reason, on_delete='CASCADE')

class Destroyed(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    is_sample_destroyed = models.BooleanField(default=1)
    sample_destroyed_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)

class Examiner(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    customer = models.ForeignKey(Customer, on_delete='CASCADE')