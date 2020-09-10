from django.contrib import admin
from .models import Customer, Feedback, Organization, Customer_Organization
from django.conf import settings
# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'last_name',
        'first_name',
        'birth_date',
        'title',
        'email',
        'phone_number',
        'address',
        'memo'
    )
@admin.register(Feedback)
class FeebackAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'product',
        'feedback',
        'feedback_date'
    )
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'department'
    )
@admin.register(Customer_Organization)
class Customer_OrgnaizationAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'organization'
    )
