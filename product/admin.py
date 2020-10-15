from django.contrib import admin
from .models import Product, Plan, Project
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'prefix',
        'status'
    )

@admin.register(Plan)
class PlanAsmin(admin.ModelAdmin):
    list_display = (
        'product',
        'name',
        'price',
        'status',
        'description'
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'content_type'
    )