# Create your models here.
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User

class Organization(models.Model):
    name = models.CharField(max_length = 50)
    department = models.CharField(max_length = 50)
    contact_person = models.CharField(max_length = 50)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        if self.department == '':
            return self.name + '-' + self.contact_person
        else:
            return self.name + '-' + self.department + '-' + self.contact_person
    
    def get_internal_org_and_contact_person(self):
        return self.name + '-' + self.department + '-' + self.contact_person

    def get_external_org_and_conttact_person(self):
        if self.department == '':
            return self.name + '-' + self.contact_person
        else:
            return self.name + '-' + self.department + '-' + self.contact_person

class Title(models.Model):
    name = models.CharField(max_length = 10)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    nick_name = models.CharField(max_length=10, default='', unique=True)
    phone_number = models.CharField(max_length=10, null=True)
    address = models.CharField(max_length=50, null=True)
    gender = models.CharField(max_length=10, null=True)