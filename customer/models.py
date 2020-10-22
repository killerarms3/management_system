from django.db import models
from django.core.exceptions import ValidationError
from product.models import Product
import datetime

# Create your models here.

class Title(models.Model):
    name = models.CharField(max_length=32)
    is_other = models.BooleanField(default=True)

class Job(models.Model):
    name = models.CharField(max_length=32)
    is_other = models.BooleanField(default=True)

class Customer_Type(models.Model):
    name = models.CharField(max_length=32)

class Customer(models.Model):
    last_name = models.CharField(max_length=32)
    first_name = models.CharField(max_length=32)
    birth_date = models.DateField(blank=True, null=True)
    title = models.ForeignKey(Title, on_delete='CASCADE')
    job = models.ForeignKey(Job, on_delete='CASCADE')
    line_id = models.CharField(max_length=32, blank=True, null=True)
    email = models.CharField(max_length=320, blank=True, null=True)
    tel = models.CharField(max_length=32, blank=True, null=True)
    mobile = models.CharField(max_length=32, blank=True, null=True)
    address = models.CharField(max_length=320, blank=True, null=True)
    memo = models.TextField(blank=True, null=True)
    customer_type = models.ForeignKey(Customer_Type, on_delete='CASCADE')

    def __str__(self):
        return self.first_name + ', ' + self.last_name

    def clean(self):
        errors = list()
        # 若重複，則更新舊資料!?
        if not self.tel and not self.mobile:
            errors.append({'phone_number': ['手機電話或市內電話只少要填一個']})
        if self.birth_date:
            try:
                if isinstance(self.birth_date, datetime.date):
                #     date = self.birth_date.strftime('%Y-%m-%d')
                    self.birth_date = datetime.datetime(self.birth_date.year, self.birth_date.month, self.birth_date.day)
                else:
                    self.birth_date = datetime.datetime.strptime(self.birth_date, '%Y-%m-%d')
                now = datetime.datetime.now()
                if self.birth_date > now:
                    errors.append({'birth_date': ['不接受未來日期']})
            except ValueError:
                errors.append({'birth_date': ['日期格式錯誤，只接受"YYYY-MM-DD']})
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

    def __str__(self):
        return self.last_name + self.first_name

    def get_name_and_org(self):
        return self.last_name + self.first_name + ' ('+ self.title.name +')' 

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