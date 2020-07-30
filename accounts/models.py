from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User


class Organization(models.Model):
    name = models.CharField(max_length = 50)
    department = models.CharField(max_length = 50)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.name + ', ' + self.department


class Title(models.Model):
    name = models.CharField(max_length = 10)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True)
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    phone_number = models.CharField(max_length=10)
    address = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, null=True)

    

# Create your models here.
