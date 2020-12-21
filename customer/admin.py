from django.contrib import admin
from .models import Customer, Feedback, Organization
from django.conf import settings
# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'last_name',
        'first_name',
        'birth_date',
        'organization',
        'title',
        'job',
        'line_id',
        'email',
        'tel',
        'mobile',
        'address',
        'memo',
        'customer_type',
        'introducer',
        'relationship'
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
