from django.contrib import admin
from .models import Contract, Payment_method, Order, Receipt, Failed_reason, Box, Failed, Destroyed, Examiner, Order_quantity

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'contract_date',
        'customer',
        'expected_quantity',
        'memo'
    )

@admin.register(Payment_method)
class Payment_methodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_date',
        'contract',
        'memo'
    )

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'contract',
        'receipt_date',
        'receipt_number',
        'receipt_amount',
        'payment_method',
        'payment_date',
        'memo'
    )

@admin.register(Failed_reason)
class Failed_reasonAdmin(admin.ModelAdmin):
    list_display = (
        'failed_reason',
        'memo'
    )

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number',
        'order',
        'plan',
        'tracing_number'
    )

@admin.register(Failed)
class FailedAdmin(admin.ModelAdmin):
    list_display = (
        'box',
        'failed_reason'
    )

@admin.register(Destroyed)
class DestroyedAdmin(admin.ModelAdmin):
    list_display = (
        'box',
        'is_sample_destroyed',
        'sample_destroyed_date',
        'return_date'
    )

@admin.register(Examiner)
class ExaminerAdmin(admin.ModelAdmin):
    list_display = (
        'box',
        'customer'
    )

@admin.register(Order_quantity)
class Order_quantityAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'plan',
        'quantity',
    )
# Register your models here.
