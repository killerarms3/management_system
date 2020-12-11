from django.db import models
from django.core.exceptions import ValidationError
from product.models import Product
import datetime
from lib.Validator import ValidateTelNumber, ValidateMobileNumber, ValidateDate
from django.core.validators import validate_email
from django.urls import reverse
# Create your models here.

class Title(models.Model):
    name = models.CharField(max_length=32)
    is_other = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    name = models.CharField(max_length=32)
    is_other = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Customer_Type(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class Customer(models.Model):
    last_name = models.CharField(max_length=32)
    first_name = models.CharField(max_length=32)
    birth_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    title = models.ForeignKey(Title, on_delete='CASCADE', blank=True, null=True)
    job = models.ForeignKey(Job, on_delete='CASCADE', blank=True, null=True)
    line_id = models.CharField(max_length=32, blank=True, null=True)
    email = models.CharField(max_length=320, blank=True, null=True, validators=[validate_email])
    tel = models.CharField(max_length=32, blank=True, null=True, validators=[ValidateTelNumber])
    mobile = models.CharField(max_length=32, blank=True, null=True, validators=[ValidateMobileNumber])
    address = models.CharField(max_length=320)
    memo = models.TextField(blank=True, null=True)
    customer_type = models.ForeignKey(Customer_Type, on_delete='CASCADE')

    def __str__(self):
        return self.last_name + self.first_name

    def clean(self):
        errors = list()
        # 若重複，則更新舊資料!?
        if not self.tel and not self.mobile:
            errors.extend([{'tel': ['手機電話或市內電話只少要填一個']}, {'mobile': ['手機電話或市內電話只少要填一個']}])
        if not self.birth_date:
            self.birth_date = None
        try:
            self.clean_fields()
        except ValidationError as err:
            errors.append(err.message_dict)
        if errors:
            error_dict = dict()
            for error in errors:
                for key in error:
                    if key not in error_dict:
                        error_dict[key] = list()
                    error_dict[key].extend(error[key])
            raise ValidationError(error_dict)

    def get_absolute_url(self):
        return reverse('customer:view_specific_customer', args=[str(self.id)])

    def get_name_and_job(self):
        return self.last_name + self.first_name + ' ('+ self.job.name +')'

class Relationship(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class Customer_Introducer(models.Model):
    customer = models.ForeignKey(Customer, on_delete='CASCADE', related_name='customer')
    introducer = models.ForeignKey(Customer, on_delete='CASCADE', related_name='introducer')
    relationship = models.ForeignKey(Relationship, on_delete='CASCADE')

    def __str__(self):
        return self.introducer.last_name + self.introducer.first_name

class Feedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete='CASCADE')
    product = models.ForeignKey(Product, on_delete='CASCADE')
    feedback = models.TextField()
    feedback_date = models.DateField()

class Organization(models.Model):
    name = models.CharField(max_length=256)
    department = models.CharField(max_length=256)
    is_other = models.BooleanField(default=True)
    def __str__(self):
        return self.name + '-' + self.department

class Customer_Organization(models.Model):
    customer = models.ForeignKey(Customer, on_delete='CASCADE')
    organization = models.ForeignKey(Organization, on_delete='CASCADE')