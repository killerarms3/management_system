from django.db import models
from django.core.exceptions import ValidationError
from product.models import Product
import datetime
from lib.Validator import ValidateTelNumber, ValidateMobileNumber, ValidateDate
from django.core.validators import validate_email
from django.urls import reverse
# Create your models here.

class Title(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class Customer_Type(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class Organization(models.Model):
    name = models.CharField(max_length=32)
    department = models.CharField(max_length=32, blank=True)

    class Meta:
        unique_together = ('name', 'department',)

    def __str__(self):
        return self.name + '-' + self.department if self.department else self.name

class Relationship(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    last_name = models.CharField(max_length=32)
    first_name = models.CharField(max_length=32)
    birth_date = models.DateField(blank=True, null=True, validators=[ValidateDate])
    organization = models.ForeignKey(Organization, on_delete='CASCADE', blank=True, null=True)
    title = models.ForeignKey(Title, on_delete='CASCADE', blank=True, null=True)
    job = models.ForeignKey(Job, on_delete='CASCADE')
    line_id = models. CharField(max_length=32, blank=True, null=True)
    email = models.CharField(max_length=320, blank=True, null=True, validators=[validate_email])
    tel = models.CharField(max_length=32, blank=True, null=True, validators=[ValidateTelNumber])
    mobile = models.CharField(max_length=32, blank=True, null=True, validators=[ValidateMobileNumber])
    address = models.CharField(max_length=320)
    memo = models.TextField(blank=True, null=True)
    customer_type = models.ForeignKey(Customer_Type, on_delete='CASCADE')
    introducer = models.ForeignKey('self', on_delete='CASCADE', blank=True, null=True)
    relationship = models.ForeignKey(Relationship, on_delete='CASCADE', blank=True, null=True)

    class Meta:
        unique_together = ('last_name', 'first_name', 'job',)

    def __str__(self):
        return self.last_name + self.first_name

    def clean(self):
        errors = list()
        if not self.tel and not self.mobile:
            errors.extend([{'tel': ['手機電話或市內電話只少要填一個']}, {'mobile': ['手機電話或市內電話只少要填一個']}])
        if (self.introducer and not self.relationship) or (not self.introducer and self.relationship):
            errors.extend([{'introducer': ['推薦人與關係必須兩個都填或都不填']}, {'relationship': ['推薦人與關係必須兩個都填或都不填']}])
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

class Feedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete='CASCADE')
    product = models.ForeignKey(Product, on_delete='CASCADE')
    feedback = models.TextField()
    feedback_date = models.DateField()

class Customer_Data(models.Model):
    customer = models.ForeignKey(Customer, on_delete='CASCADE')
    # content_type = models.ForeignKey(ContentType, blank=False, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField(blank=False)
    file = models.FileField(upload_to='customer_file/', blank=False, null=False)

    def __str__(self):
        name = str(self.file).replace('customer_file/', '')
        return name