from django.contrib import admin
from .models import Product, Prefix, Product_Prefix, Plan, Project
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'status'
    )

@admin.register(Prefix)
class PrefixAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )

@admin.register(Product_Prefix)
class Product_PrefixAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'prefix'
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
        'contend_type'
    )
