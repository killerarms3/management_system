from django.db import models
from django.contrib.auth.models import User
<<<<<<< HEAD
from customer.models import Customer
from product.models import Plan


# Create your models here.
class Contract(models.Model):
    user = models.ForeignKey(User, on_delete='CASCADE')
    contract_date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete='CASCADE')
    organization_id = models.CharField(max_length=256, blank=True, null=True)
    expected_quantity = models.PositiveIntegerField(blank=True, null=True)
    order_id = models.CharField(max_length=256, blank=True, null=True)
    receipt_id = models.CharField(max_length=256, blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

class Payment_method(models.Model):
    name = models.CharField(max_length=32)

class Order(models.Model):
    order_date = models.DateField()
    contract = models.ForeignKey(Contract, on_delete='CASCADE')
    plan_id = models.CharField(max_length=256)
    quantity = models.CharField(max_length=256)
    memo = models.TextField(blank=True, null=True)

class Receipt(models.Model):
    contract = models.ForeignKey(Contract, on_delete='CASCADE')
    receipt_date = models.DateField(blank=True, null=True)
    receipt_number = models.CharField(max_length=32, blank=True, null=True)
    receipt_amount = models.PositiveIntegerField(blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.ForeignKey(Payment_method, on_delete='CASCADE')
    memo = models.TextField(blank=True, null=True)

class Failed_reason(models.Model):
    failed_reason = models.CharField(max_length=256)
    memo = models.TextField(blank=True, null=True)

class Box(models.Model):
    serial_number = models.CharField(max_length=256)
    order = models.ForeignKey(Order, on_delete='CASCADE')
    plan = models.ForeignKey(Plan, on_delete='CASCADE')
    tracing_number = models.CharField(max_length=64, blank=True, null=True)

class Failed(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    failed_reason = models.ForeignKey(Failed_reason, on_delete='CASCADE')

class Destroyed(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    is_sample_destroyed = models.BooleanField(default=1)
    sample_destroyed_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)

class Examiner(models.Model):
    box = models.ForeignKey(Box, on_delete='CASCADE')
    customer = models.ForeignKey(Customer, on_delete='CASCADE')
=======
from customer.models import Customer, Organization
from product.models import Plan
from django.urls import reverse

# Create your models here.
class Contract(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='負責人')
    contract_date = models.DateField(verbose_name='簽約日期')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客戶/聯絡人')
    organization = models.ManyToManyField(Organization, verbose_name='機構/單位')
    expected_quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name='預期數量')
    # order_id = models.CharField(max_length=256, blank=True, null=True)
    # receipt_id = models.CharField(max_length=256, blank=True, null=True)
    memo = models.TextField(blank=True, null=True, verbose_name='備註')

    def __str__(self):
        return 'Contract' + str(self.pk)

    def get_absolute_url(self):
        return reverse("contract-detail", kwargs={"pk": self.pk})

class Payment_method(models.Model):
    name = models.CharField(max_length=32, unique=True, error_messages={'unique':"該方法已經存在",}, verbose_name='名稱') # 設為unique不希望名稱重複

    def __str__(self):
        return self.name

class Order(models.Model):
    order_date = models.DateField(blank=True, null=True, verbose_name='訂單日期')
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='合約')
    plan = models.ManyToManyField(Plan, verbose_name='方案') # 一個order可以擁有多個plan，一個plan也可以屬於多個order
    memo = models.TextField(blank=True, null=True, verbose_name='備註')

    def __str__(self):
        return 'Order ' + str(self.pk)

    def get_absolute_url(self):
        return reverse('contract:order-detail', args=[str(self.pk)])

# 目前沒用到，網頁上是用count來計算quantity
class Order_quantity(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='訂單')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, verbose_name='方案')
    quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name='商品數量')

class Receipt(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='合約')
    receipt_date = models.DateField(blank=True, null=True, verbose_name='開立發票日期')
    receipt_number = models.CharField(max_length=32, blank=True, null=True, unique=True, verbose_name='發票號碼') # 設為unique不希望編號重複
    receipt_amount = models.PositiveIntegerField(blank=True, null=True, verbose_name='發票金額')
    payment_date = models.DateField(blank=True, null=True, verbose_name='付款日期')
    payment_method = models.ForeignKey(Payment_method, on_delete=models.CASCADE, verbose_name='付款方式')
    memo = models.TextField(blank=True, null=True, verbose_name='備註')

    def __str__(self):
        return self.receipt_number

    def get_absolute_url(self):
        return reverse("contract:receipt-detail", args=[str(self.pk)])

class Failed_reason(models.Model):
    failed_reason = models.CharField(max_length=32, unique=True, verbose_name='失敗原因') # 設為unique不希望名稱重複
    memo = models.TextField(blank=True, null=True, verbose_name='備註')

    def __str__(self):
        return self.failed_reason
        
    def get_absolute_url(self):
        return reverse("contract:failed_reason-detail", args=[str(self.pk)])

class Box(models.Model):
    serial_number = models.CharField(max_length=250, unique=True, verbose_name='流水號') # serial number可重複因為有可能失敗後重新寄送
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='訂單')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, verbose_name='方案')
    tracing_number = models.CharField(max_length=64, blank=True, null=True, verbose_name='宅配單號')

    def __str__(self):
        return self.serial_number + ', ' + str(self.pk)
    
    def get_absolute_url(self):
        return reverse("contract:box-detail", args=[str(self.pk)])

class Failed(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name='採樣盒')
    failed_reason = models.ForeignKey(Failed_reason, on_delete=models.CASCADE, verbose_name='失敗原因')

class Destroyed(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name='檢驗盒')
    is_sample_destroyed = models.BooleanField(default=1, verbose_name='銷毀註記')
    sample_destroyed_date = models.DateField(blank=True, null=True, verbose_name='銷毀日期')
    return_date = models.DateField(blank=True, null=True, verbose_name='DNA取回日期')

    def get_absolute_url(self):
        return reverse("contract:destroyed-detail", args=[str(self.pk)])

class Examiner(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name='採樣盒')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='受測者')
>>>>>>> sheet_contract
