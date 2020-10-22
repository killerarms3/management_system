from django.db import models
from django.contrib.auth.models import User
from customer.models import Customer, Organization
from product.models import Plan
from django.urls import reverse
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Contract(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='* 負責人')
    contract_name = models.CharField(max_length=12, unique=True, default='', verbose_name='* 合約名稱/代號')
    contract_date = models.DateField(verbose_name='* 簽約日期')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='* 客戶/聯絡人')
    organization = models.ManyToManyField(Organization, verbose_name='* 機構/單位')
    expected_quantity = models.PositiveIntegerField(blank=False, null=True, verbose_name='* 預期數量')
    memo = models.TextField(blank=True, null=True, verbose_name='備註')

    def __str__(self):  
        return self.contract_name

    def get_absolute_url(self):
        return reverse("contract-detail", kwargs={"pk": self.pk})    

class Payment_method(models.Model):
    name = models.CharField(max_length=32, unique=True, error_messages={'unique':"該方法已經存在",}, verbose_name='名稱') # 設為unique不希望名稱重複

    def __str__(self):
        return self.name

class Order(models.Model):
    order_date = models.DateField(blank=True, null=True, verbose_name='訂單日期')
    order_name = models.CharField(max_length=64, default='', verbose_name='* 訂單代號')
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='* 合約')
    plan = models.ManyToManyField(Plan, verbose_name='* 方案') # 一個order可以擁有多個plan，一個plan也可以屬於多個order
    memo = models.TextField(blank=True, null=True, verbose_name='備註')
    
    def __str__(self):
        return self.order_name

    def get_absolute_url(self):
        return reverse('contract:order-detail', args=[str(self.pk)])

# 目前沒用到，網頁上是用count來計算quantity
class Order_quantity(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='訂單')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, verbose_name='方案')
    quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name='商品數量')

class Receipt(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='* 合約')
    receipt_date = models.DateField(blank=False, null=True, verbose_name='* 開立發票日期')
    receipt_number = models.CharField(blank=False, null=True, max_length=32, unique=True, verbose_name='* 發票號碼') # 設為unique不希望編號重複
    receipt_amount = models.PositiveIntegerField(blank=False, null=True,verbose_name='* 發票金額')
    payment_date = models.DateField(blank=True, null=True, verbose_name='入賬日期')
    receipt_org = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE, verbose_name='* 單位')
    payment_method = models.ForeignKey(Payment_method, on_delete=models.CASCADE, verbose_name='* 付款方式')
    receipt_content = models.TextField(blank=True, null=True, verbose_name='發票內容')
    memo = models.TextField(blank=True, null=True, verbose_name='備註')

    def __str__(self):
        return self.receipt_number

    def get_absolute_url(self):
        return reverse("contract:receipt-detail", args=[str(self.pk)])

class Failed_reason(models.Model):
    failed_reason = models.CharField(max_length=32, unique=True, verbose_name='* 失敗原因') # 設為unique不希望名稱重複
    memo = models.TextField(blank=True, null=True, verbose_name='備註')

    def __str__(self):
        return self.failed_reason

    def get_absolute_url(self):
        return reverse("contract:failed_reason-detail", args=[str(self.pk)])

class Box(models.Model):
    serial_number = models.CharField(max_length=250, unique=True, verbose_name='* 流水號') # serial number可重複因為有可能失敗後重新寄送
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='* 訂單')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, verbose_name='* 方案')
    tracing_number = models.CharField(max_length=64, blank=True, null=True, verbose_name='宅配單號')

    def __str__(self):
        return self.serial_number

    def get_absolute_url(self):
        return reverse("contract:box-detail", args=[str(self.pk)])

class Failed(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name='* 採樣盒')
    failed_reason = models.ForeignKey(Failed_reason, on_delete=models.CASCADE, verbose_name='* 失敗原因')

class Destroyed(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name='* 檢驗盒')
    is_sample_destroyed = models.BooleanField(default=1, verbose_name='* 銷毀註記')
    sample_destroyed_date = models.DateField(blank=True, null=True, verbose_name='銷毀日期')
    return_date = models.DateField(blank=True, null=True, verbose_name='DNA取回日期')

    def get_absolute_url(self):
        return reverse("contract:destroyed-detail", args=[str(self.pk)])

class Examiner(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name='* 採樣盒')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='* 受測者')

class Upload_Image(models.Model):
    content_type = models.ForeignKey(ContentType, blank=False, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=False)
    image = models.ImageField(upload_to='image/', blank=False, null=False)

class Upload_File(models.Model):
    content_type = models.ForeignKey(ContentType, blank=False, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=False)
    file_upload = models.FileField(upload_to='file/', blank=False, null=False)