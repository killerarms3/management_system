from django import forms
from django.forms import widgets
from django.forms import ModelChoiceField
from contract.models import Box, Destroyed, Failed, Failed_reason, Order, Examiner, Contract, Receipt, Payment_method
from product.models import Plan
from customer.models import Customer, Organization
from django.contrib.auth.models import User
from django.apps import apps
from lib import utils
import datetime

class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_name_and_job()

class CustomUserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        UserProfile = apps.get_model('accounts', 'UserProfile')
        userprofile = UserProfile.objects.get(user=obj)
        return userprofile.nick_name

class ContractCreateForm(forms.ModelForm):
    user = CustomUserModelChoiceField(label='* 負責人', queryset=User.objects.exclude(username='admin'), required=True)
    contract_date = forms.DateField(
        label='* 簽約日期',
        widget=forms.DateInput(
            # 定義Contract Date內容最大值與最小值
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'contract_date',
                'name': 'contract_date',
                'min': '1820-01-01',
                'max': '2100-01-01'
            }),
        required=True
        )
    organization = forms.ModelMultipleChoiceField(label='* 機構/單位', queryset=Organization.objects.all(), required=False)
    customer = CustomModelChoiceField(
        label='* 客戶',
        queryset=Customer.objects.all(),
        required=True
    )
    class Meta:
        model = Contract
        fields = '__all__'

class ContractUpdateForm(forms.ModelForm):
    user = CustomUserModelChoiceField(label='* 負責人', queryset=User.objects.exclude(username='admin'), required=True)
    contract_date = forms.DateField(
        label='* 簽約日期',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'contract_date',
                'name': 'contract_date',
                'min': '1820-01-01',
                'max': '2100-01-01'
            }),
        required=True
    )
    customer = CustomModelChoiceField(
        label = '* 客戶',
        queryset=Customer.objects.all(),
        required=True
        )
    organization = forms.ModelMultipleChoiceField(label='* 機構/單位', queryset=Organization.objects.all(), required=False)
    memo = forms.CharField(
        label='備註',
        # 定義memo textarea屬性
        widget=forms.Textarea(
            attrs={
                'cols':'40',
                'rows':'10',
                'id':'memo',
                'name':'memo'
                }),
        required=False
        )
    class Meta:
        model = Contract
        fields = '__all__'

class OrderUpdateForm(forms.ModelForm):
    order_date = forms.DateField(
        label='訂單日期',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'order_date',
                'name': 'order_date',
                'min': '1820-01-01',
                'max': '2100-01-01'
            }
        ),
        required=True
    )
    plan = forms.ModelMultipleChoiceField(
        label='方案',
        queryset=Plan.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'onchange':"myFunction();"
                }),
        required = False
        )
    memo = forms.CharField(
        label='備註',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'cols':'20',
                'rows':'10',
                'id':'memo',
                'name':'memo'
                }),
        required=False
        )
    class Meta:
        model = Order
        fields = '__all__'

class OrderCreateForm(OrderUpdateForm):
    plan = forms.ModelMultipleChoiceField(
        label='* 方案',
        queryset=Plan.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'onchange':"addtr();"
                }))
    class Meta:
        model = Order
        exclude = ('order_name',)

class SpecifyOrderCreateForm(OrderUpdateForm):
    class Meta:
        model = Order
        # 因contract為指定，故不顯示為form
        fields = ('order_date', 'plan', 'memo')

class DestroyedUpdateForm(forms.ModelForm):
    is_sample_destroyed = forms.BooleanField(label='銷毀註記', help_text='Is destroyed or not', required=False) # 因其為布林值，required=False以表現其狀態
    sample_destroyed_date = forms.DateField(
        label='銷毀日期',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'destroyed_date',
                'min': '1820-01-01',
                'max': '2100-01-01'
            }),
        required=False
        )
    return_date = forms.DateField(
        label='DNA取回日期',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'return_date',
                'min': '1820-01-01',
                'max': '2100-01-01'
            }),
        required=False
        )
    class Meta:
        model = Destroyed
        fields = ('is_sample_destroyed', 'sample_destroyed_date', 'return_date')

class DestroyedCreateForm(DestroyedUpdateForm):
    destroyed = apps.get_model('contract', 'Destroyed')
    id_list = destroyed.objects.all().values_list('box_id', flat=True)
    box = forms.ModelChoiceField(label='採樣盒', queryset=Box.objects.exclude(id__in=id_list), required = True) # 已經存在於destroyed的box不予顯示
    class Meta:
        model = Destroyed
        fields = '__all__'

class FailedCreateForm(forms.ModelForm):
    failed = apps.get_model('contract', 'Failed')
    id_list = failed.objects.all().values_list('box_id', flat=True)
    box = forms.ModelChoiceField(label='採樣盒', queryset=Box.objects.exclude(id__in=id_list), required = True) # 已經存在於failed的box不予顯示
    class Meta:
        model = Failed
        fields = '__all__'

class ExaminerCreateForm(forms.ModelForm):
    examiner = apps.get_model('contract', 'Examiner')
    id_list = examiner.objects.all().values_list('box_id', flat=True)
    box = forms.ModelChoiceField(label='採樣盒', queryset=Box.objects.exclude(id__in=id_list), required = True) # 已經存在於examiner的box不予顯示
    class Meta:
        model = Examiner
        fields = '__all__'

class SpecifyFailedCreateForm(forms.ModelForm):
    class Meta:
        model = Failed
        fields = ('failed_reason',) # 因指定了box所以不顯示

class SpecifyDestroyedCreateForm(DestroyedUpdateForm):
    class Meta:
        model = Destroyed
        fields = ('is_sample_destroyed', 'sample_destroyed_date', 'return_date') # 因指定了box所以不顯示

class SpecifyExaminerCreateForm(forms.ModelForm):
    class Meta:
        model = Examiner
        fields = ('customer',) # 因指定了box所以不顯示

class BoxUpdateForm(forms.Form):
    user = CustomUserModelChoiceField(label='負責人', queryset=User.objects.exclude(username='admin'), required=False)
    order = forms.ModelChoiceField(label='訂單', queryset=Order.objects.all(), required=True)
    plan = forms.ModelChoiceField(label='方案', queryset=Plan.objects.all(), required = True)
    failed_reason = forms.ModelChoiceField(label='失敗原因', queryset=Failed_reason.objects.all(), required=False)
    examiner = forms.ModelChoiceField(label='受測者', queryset=Customer.objects.all(), required=False)
    is_sample_destroyed = forms.BooleanField(label='銷毀註記', help_text='Is destroyed or not', required=False)
    sample_destroyed_date = forms.DateField(
        label='銷毀日期',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'destroyed_date',
                'min': '1820-01-01',
                'max': '2100-01-01'
            }),
        required=False
        )
    return_date = forms.DateField(
        label='DNA取回日期',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'return_date',
                'min': '1820-01-01',
                'max': '2100-01-01'
            }),
        required=False
        )
    tracing_number = forms.CharField(
        label='宅配單號',
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
            }),
        required=False
    )
    fields = (
        'user',
        'order',
        'plan',
        'failed_reason',
        'examiner',
        'is_sample_destroyed',
        'sample_destroyed_date',
        'return_date',
        'tracing_number'
        )

class ReceiptUpdateForm(forms.ModelForm):
    receipt_date = forms.DateField(
        label='* 開立發票日期',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'receipt_date',
                'min': '1820-01-01',
                'max': '2100-01-01'
            }),
        required=False
        )
    payment_date = forms.DateField(
        label='入賬日期',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'payment_date',
                'min': '1820-01-01',
                'max': '2100-01-01'
            }),
        required=False
        )
    memo = forms.CharField(
        label='備註',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'cols':'10',
                'rows':'10',
                'id':'memo',
                'name':'memo'
                }),
        required=False
        )
    class Meta:
        model = Receipt
        fields = '__all__'

class ReceiptCreateForm(ReceiptUpdateForm):
    class Meta:
        model = Receipt
        fields = '__all__'

class SpecifyReceiptCreateForm(ReceiptUpdateForm):
    class Meta:
        model = Receipt
        fields = ('receipt_date', 'receipt_number', 'receipt_amount', 'payment_date', 'payment_method', 'memo',) # 因指定了contract所以不顯示

class MultipleBoxCreateForm(forms.ModelForm):
    user = CustomUserModelChoiceField(label='負責人', queryset=User.objects.exclude(username='admin'), required=False)
    order = forms.ModelChoiceField(label='訂單', queryset=Order.objects.all(), required=True)
    plan = forms.ModelChoiceField(label='方案', queryset=Plan.objects.all(), required = True)
    quantity = forms.IntegerField(
        label='* 採樣盒數量',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'max': '4000',
            }),
        required=True
        )
    tracing_number = forms.CharField(
        label='宅配單號',
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
            }),
        required=False
    )
    class Meta:
        model = Box
        fields = ('user', 'quantity', 'order', 'plan', 'tracing_number')

class SpecifyBoxCreateForm(forms.Form):
    user = CustomUserModelChoiceField(label='負責人', queryset=User.objects.exclude(username='admin'), required=False)
    plan = forms.ModelChoiceField(label='方案', queryset=Plan.objects.all(), required = True)
    quantity = forms.IntegerField(
        label='* 採樣盒數量',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'max': '500',
            }),
        required=True
        )
    tracing_number = forms.CharField(
        label='宅配單號',
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
            }),
        required=False
    )
    fields = ('user', 'quantity', 'plan', 'tracing_number') # 因指定了order所以不顯示

class MultipleSerialNumberCreateForm(forms.Form):
    sub_plan = forms.ModelChoiceField(label='方案', queryset=Plan.objects.all(), required=True)
    quantity = forms.IntegerField(
        label='* 採樣盒數量',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'max': '100',
            }),
        required=True
        )

class TracingNumberMultiUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TracingNumberMultiUpdateForm, self).__init__(*args, **kwargs)
        # if not self.instance.id:
        #     pass

        for visible in self.visible_fields():
            if visible.field.widget.__class__.__name__ == 'Select' or visible.field.widget.__class__.__name__ == 'SelectMultiple':
                visible.field.widget.attrs['class'] = 'multiple-select'
            else:
                visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Box
        fields = ('serial_number', 'tracing_number',)
        labels = utils.getlabels('contract', 'box')
        widgets = utils.GetCustomWidgets(Box)