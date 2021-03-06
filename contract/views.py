from django.shortcuts import render, redirect
from .models import Contract, Payment_method, Order, Receipt, Failed_reason, Box, Failed, Destroyed, Examiner, Order_quantity, Upload_Image, Upload_File
from experiment.models import Experiment
from product.models import Project, Plan
from history.models import History
from history.function import log_addition, object_to_dict, Update_log_dict, Create_log_dict
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.db.models import Count
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from .forms import (DestroyedCreateForm, DestroyedUpdateForm, FailedCreateForm, BoxUpdateForm, SpecifyFailedCreateForm,
                    SpecifyDestroyedCreateForm, ExaminerCreateForm, SpecifyExaminerCreateForm, OrderUpdateForm, OrderCreateForm,
                    ContractCreateForm, ContractUpdateForm, ReceiptUpdateForm, SpecifyReceiptCreateForm, SpecifyOrderCreateForm,
                    SpecifyBoxCreateForm, ReceiptCreateForm, MultipleBoxCreateForm, MultipleSerialNumberCreateForm, TracingNumberMultiUpdateForm)
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from lib import utils
from lib.multi_add import AddMultiData
from lib.Validator import ValidateOrganization
from django.core.exceptions import ValidationError
import datetime
from decimal import Decimal
import json
import time

# customize class
# 繼承CreateView並自定義form_valid
class CreateView_add_log(CreateView):
    # --------- history --------
    def form_valid(self, form):
        obj_id, dict = Create_log_dict(self, form, self.model)
        log_addition(self.request.user, 'contract', self.object._meta.model_name, obj_id, '1', dict, {})
        return super().form_valid(form)
    # --------- history --------

# 繼承UpdateView並自定義form_valid
class UpdateView_add_log(UpdateView):
    # --------- history --------
    def form_valid(self, form):
        obj_id, dict, pre_dict = Update_log_dict(self, form)
        log_addition(self.request.user, 'contract', self.object._meta.model_name, obj_id, '2', dict, pre_dict)
        return super().form_valid(form)
    # --------- history --------

# 繼承DeleteView並自定義form_valid
class DeleteView_add_log(DeleteView):
    # --------- history --------
    # DeleteView中並沒有formValid函式，其在進行刪除功能時會在網頁回傳POST時會在post函式中回傳並呼叫delete函式，
    # 具體的刪除功能寫在delete中，所以這裡將紀錄log的部分自定義在post裡，並呼叫父類別的post以使用Django定義的delete函式
    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        pre_dict = object_to_dict(obj)
        log_addition(request.user, 'contract', obj._meta.model_name, obj.id, '3', {}, pre_dict)
        return super().post(request, *args, **kwargs)
    # --------- history --------

# Create your views here.

class ContractListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.add_contract'
    model = Contract

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dict = {}
        Upload_File = apps.get_model('contract', 'Upload_File')
        upload_file = Upload_File.objects.filter(content_type=ContentType.objects.get(app_label='contract', model='contract'))
        for file in upload_file:
            dict[file.object_id] = file.file_upload
        context['upload_file'] = upload_file
        context['dict'] = dict
        return context

def getContractData(request, queryset):
    upload_file_dict = {}
    Upload_File = apps.get_model('contract', 'Upload_File')
    upload_file = Upload_File.objects.filter(content_type=ContentType.objects.get(app_label='contract', model='contract'))
    for file in upload_file:
        upload_file_dict[file.object_id] = file.file_upload
    Data = dict()
    for contract in queryset:
        Data[contract.id] = [
            '<a href="%s"><i class="fas fa-edit"></i></a>' % (reverse('contract:contract_edit', args=[contract.id])) if request.user.has_perm('contract.change_contract') else '',
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=700\', height=\'800\'); return false">%s</a>' % (reverse('contract:contract_delete', args=[contract.id]), reverse('contract:contract_delete', args=[contract.id]), '<i class="fas fa-trash"></i>') if request.user.has_perm('contract.delete_contract') else '',
            '<a href="%s"><i class="fas fa-file-pdf"></i></a>' % (upload_file_dict[contract.id].url) if contract.id in upload_file_dict else '<a href="%s"><i class="fas fa-upload"></i></a>' % (reverse('contract:upload_file', args=[contract.id])),
            str(contract.contract_name),
            str(contract.customer),
            str(contract.user),
            str(contract.contract_date),
            ';'.join([str(organization) for organization in contract.organization.all()]) if contract.organization.all() else 'None',
            '&nbsp;&nbsp;<a href="%s"><i class="fas fa-list"></i></a>' % (reverse('contract:partial-order-list', args=[contract.id])) if contract.order_set.all() else 'None',
            '&nbsp;&nbsp;<a href="%s"><i class="fas fa-list"></i></a>' % (reverse('contract:contract-box-list', args=[contract.id])) if contract.order_set.all() else 'None',
            '&nbsp;&nbsp;<a href="%s"><i class="fas fa-list"></i></a>' % (reverse('contract:partial-receipt-list', args=[contract.id])) if contract.receipt_set.all() else 'None',
            str(contract.memo)
        ]
    return Data

@login_required
@permission_required('contract.view_contract', raise_exception=True)
def view_contract(request):
    if request.GET:
        columns = ['id', 'id', 'id', 'contract_name', 'customer', 'user', 'contract_date', 'organization.all()', 'id', 'id', 'id', 'memo']
        contracts = Contract.objects.all().order_by('-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, contracts)
        DataTablesServer.getData = getContractData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'contract/contract_list.html', locals())

class ContractCreate(PermissionRequiredMixin, CreateView_add_log):
    permission_required = 'contract.add_contract'
    model = Contract
    form_class = ContractCreateForm
    success_url = reverse_lazy('contract:view_contract')

    def post(self, request, *args, **kwargs):
        if Contract.objects.filter(contract_name=request.POST['contract_name']):
            messages.error(request, '合約代號重複!')
        return super().post(request, *args, **kwargs)

class ContractUpdateView(PermissionRequiredMixin, UpdateView_add_log):
    permission_required = 'contract.change_contract'
    model = Contract
    form_class = ContractUpdateForm
    template_name = 'contract/contract_change.html'
    success_url = reverse_lazy('contract:view_contract')

    def post(self, request, *args, **kwargs):
        contract_upload_file(request, self.kwargs['pk'])
        return super().post(request, *args, **kwargs)

    # 傳入Order與Receipt給template並固定contract
    def get_context_data(self, **kwargs):
        Order = apps.get_model('contract', 'Order')
        Receipt = apps.get_model('contract', 'Receipt')
        contract = Contract.objects.get(pk=self.kwargs.get('pk'))
        orders = Order.objects.filter(contract=contract)
        receipts = Receipt.objects.filter(contract=contract)
        context = super().get_context_data(**kwargs)
        context['orders'] = orders
        context['receipts'] = receipts
        return context

class ContractDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.delete_contract'
    model = Contract
    success_url = reverse_lazy('contract:view_contract')

    # --------- history --------
    def post(self, request, *args, **kwargs):
        sub_table_list = ['Order', 'Receipt']
        obj = self.get_object()
        # 檢查這個contract是否與其子表有CASCADE關係，若有，則因應CASCADE關聯會將子表一同刪除的特性，紀錄子表的刪除紀錄，以下皆同
        for model_name in sub_table_list:
            sub_obj = apps.get_model('contract', model_name)
            if sub_obj.objects.filter(contract=obj): # 檢查是否存在
                specify_sub_obj = sub_obj.objects.filter(contract=obj) # 找出
                for ssobj in specify_sub_obj:
                    sub_pre_dict = object_to_dict(ssobj)
                    log_addition(request.user, 'contract', model_name.lower(), ssobj.id, '3', {}, sub_pre_dict)

        pre_dict = object_to_dict(obj)
        log_addition(request.user, 'contract', 'contract', obj.id, '3', {}, pre_dict)
        return super().post(request, *args, **kwargs)
    # --------- history --------

class OrderDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.view_order'
    model = Order
    # 傳入Box以取得屬於本Order的Box
    def get_context_data(self, **kwargs):
        all_order_quantity = apps.get_model('contract', 'Order_quantity')
        all_box = apps.get_model('contract', 'Box')
        order = Order.objects.get(pk=self.kwargs.get('pk'))
        order_quantity = all_order_quantity.objects.filter(order=order)
        box = all_box.objects.filter(order=order)
        experiment = box.filter(id__in=list(Experiment.objects.all().values_list('box__id', flat=True)))
        context = super().get_context_data(**kwargs)
        context['order_quantity'] = order_quantity
        context['box'] = box
        context['experiment'] = experiment
        return context

class OrderListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.view_order'
    model = Order
    template_name = 'contract/order_list.html'

    # 傳入Box以取得對應Order的Box
    def get_context_data(self, **kwargs):
        order_quantity = apps.get_model('contract', 'Order_quantity')
        box = apps.get_model('contract', 'Box')
        context = super().get_context_data(**kwargs)
        context['order_quantity'] = order_quantity
        context['box'] = box
        return context

def getOrderData(request, queryset):
    Data = dict()
    for order in queryset:
        Data[order.id] = [
            '<a href="%s"><i class="fas fa-edit"></i></a>' % (reverse('contract:order_edit', args=[order.id])) if request.user.has_perm('contract.change_order') else '',
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=700\', height=\'800\'); return false">%s</a>' % (reverse('contract:order_delete', args=[order.id]), reverse('contract:order_delete', args=[order.id]), '<i class="fas fa-trash"></i>') if request.user.has_perm('contract.delete_order') else '',
            '<a href="%s">%s</a>' % (order.get_absolute_url(), order),
            str(order.contract),
            str(order.contract.customer),
            str(order.order_date),
            ';'.join(['<a href="">%s</a>(%s)' % (Plan.objects.get(pk=plan), Box.objects.filter(plan=plan, order=order).values_list('serial_number').distinct().count()) for plan in Box.objects.filter(order=order).values_list('plan', flat=True).distinct()]) if order.plan.all() else 'None',
            '&nbsp;&nbsp;<a href="%s"><i class="fas fa-list"></i></a>' % (reverse('contract:partial-box-list', args=[order.id])) if Box.objects.filter(order=order) else 'None',
            str(order.memo)
        ]
    return Data

@login_required
@permission_required('contract.view_order', raise_exception=True)
def view_order(request):
    ajax_url = reverse('contract:order-list')
    if request.GET:
        columns = ['id', 'id', '__str__', 'contract', 'contract.customer', 'order_date', 'plan.all()', 'id', 'memo']
        orders = Order.objects.all().order_by('-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, orders)
        DataTablesServer.getData = getOrderData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'contract/order_list.html', locals())

class OrderUpdateView(PermissionRequiredMixin, UpdateView_add_log):
    permission_required = 'contract.change_order'
    model = Order
    form_class = OrderUpdateForm
    template_name = 'contract/order_change.html'

    def get_context_data(self, **kwargs):
        Box = apps.get_model('contract', 'Box')
        order = Order.objects.get(pk=self.kwargs.get('pk'))
        box_list = Box.objects.filter(order=order).order_by('serial_number')
        experiment_list = box_list.filter(id__in=list(Experiment.objects.all().values_list('box__id', flat=True)))
        status = [utils.get_status(b.id) for b in box_list]
        context = super().get_context_data(**kwargs)
        # box_list 用以顯示Order中的Box
        context['box_list'] = box_list
        context['experiment_list'] = experiment_list
        context['status'] = status
        return context

class OrderCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.add_order'
    model = Order
    form_class = OrderCreateForm
    template_name = 'contract/order_form.html'
    success_url = reverse_lazy('contract:order-list')

    # 處理box新增
    def post(self, request):
        form = self.form_class(request.POST)
        order = Order()
        if form.is_valid():
            Order2 = apps.get_model('contract', 'order')
            contract = form.cleaned_data['contract']
            try:
                num = Order2.objects.filter(contract=contract).count()
            except:
                num = 0
            contract_name = contract.contract_name
            order.order_name = contract_name + '-訂單 '+str(num+1)
            order.order_date=form.cleaned_data['order_date']
            order.contract=form.cleaned_data['contract']
            order.memo=form.cleaned_data['memo']
            order.save()
            for plan in form.cleaned_data['plan']:
                order.plan.add(plan.id)
            order.save()

            # plan是ManytoMany關係，有可能有複數個，故利用迴圈逐個處理，以下皆考慮相同plan的狀況
            for plan in form.cleaned_data['plan']:
                quantity_tag = plan.product.name+'-'+plan.name+'_quantity' # template上quantity欄位的name
                quantity = request.POST[quantity_tag] # 利用前面得到的name取得在template輸入的值
                #tracing_number_tag = plan.name+'_tracing_number' # template上tracing_number欄位的對應name
                #tracing_number = request.POST[tracing_number_tag] # 同上
                new_serial_number_list = []

                prefix = plan.product.prefix
                box_serial_number_list = Box.objects.filter(serial_number__icontains=prefix).values_list('serial_number').order_by('-serial_number') # 根據serial number大到小排列

                if box_serial_number_list:
                    max_serial_number = box_serial_number_list[0][0]
                else:
                    max_serial_number = prefix+'000000'
                len_prefix = len(prefix)
                max_number = int(max_serial_number[len_prefix:]) #將前綴詞之外的轉成正整數數值
                for i in range(int(quantity)): # 先前取得的quantity即為本次新增的box數量
                    new_serial_number_list.append(prefix + str(max_number+i+1).zfill(6)) # 從現存在於database中serial number的最大值之後產生新的serial number，並將數字部分補齊六個(ex: 36補成000036)
                # 新增
                for list in new_serial_number_list:
                    Box.objects.create(
                    serial_number = list,
                    plan = plan,
                    order = order,
                    tracing_number = ''
                    )
                    # --------- history --------
                    box_new =  Box.objects.all().order_by('-id').first()
                    log_addition(self.request.user, 'contract', 'box', box_new.id, '1', object_to_dict(box_new), {})
            # --------- history --------
            log_addition(self.request.user, 'contract', 'order', order.id, '1', object_to_dict(order), {})
            # --------- history --------
            return HttpResponseRedirect('/contract/order')
        return render(request, self.template_name, {'form':form})

class OrderDeleteView(PermissionRequiredMixin, DeleteView_add_log):
    permission_required = 'contract.delete_order'
    model = Order
    success_url = reverse_lazy('contract:order-list')

class OrderbyContractListView(OrderListView):
    model = Order
    template_name = 'contract/order_list.html'
    # 觀看特定Contract的Order
    def get_queryset(self):
        contracts = apps.get_model('contract', 'Contract')
        contract = contracts.objects.get(pk=self.kwargs.get('pk'))
        order = Order.objects.filter(contract=contract)
        return order

@login_required
@permission_required('contract.view_order', raise_exception=True)
def orderbycontractlistview(request, pk):
    ajax_url = reverse('contract:partial-order-list', args=[pk])
    if request.GET:
        columns = ['id', 'id', '__str__', 'contract', 'contract.customer', 'order_date', 'plan.all()', 'id', 'memo']
        contract = Contract.objects.get(pk=pk)
        orders = Order.objects.filter(contract=contract).order_by('-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, orders)
        DataTablesServer.getData = getOrderData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'contract/order_list.html', locals())

class ReceiptListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.view_receipt'
    model = Receipt

def getReceiptData(request, queryset):
    Data = dict()
    for receipt in queryset:
        Data[receipt.id] = [
            '<a href="%s"><i class="fas fa-edit"></i></a>' % (reverse('contract:receipt_edit', args=[receipt.id])) if request.user.has_perm('contract.change_receipt') else '',
            '<a href="%s"><i class="fas fa-trash"></i></a>' % (reverse('contract:receipt_delete', args=[receipt.id])) if request.user.has_perm('contract.delete_receipt') else '',
            '<a href="%s">%s</a>' % (receipt.get_absolute_url(), receipt),
            str(receipt.contract),
            str(receipt.receipt_date),
            str(receipt.receipt_amount),
            str(receipt.payment_date),
            str(receipt.receipt_org),
            str(receipt.payment_method),
            str(receipt.receipt_content),
            str(receipt.memo)
        ]
    return Data

@login_required
@permission_required('contract.view_receipt', raise_exception=True)
def view_receipt(request):
    ajax_url = reverse('contract:receipt-list')
    if request.GET:
        columns = ['id', 'id', '__str__', 'contract', 'receipt_date', 'receipt_amount', 'payment_date', 'receipt_org', 'payment_method', 'receipt_content', 'memo']
        receipts = Receipt.objects.all().order_by('-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, receipts)
        DataTablesServer.getData = getReceiptData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'contract/receipt_list.html', locals())


class ReceiptbyContract(ReceiptListView):
    def get_queryset(self):
        contracts = apps.get_model('contract', 'Contract')
        contract = contracts.objects.get(pk=self.kwargs.get('pk'))
        receipt = Receipt.objects.filter(contract=contract)
        return receipt

@login_required
@permission_required('contract.view_receipt', raise_exception=True)
def receiptbycontract(request, pk):
    ajax_url = reverse('contract:partial-receipt-list', args=[pk])
    if request.GET:
        columns = ['id', 'id', '__str__', 'contract', 'receipt_date', 'receipt_amount', 'payment_date', 'receipt_org', 'payment_method', 'receipt_content', 'memo']
        contract = Contract.objects.get(pk=pk)
        receipts = Receipt.objects.filter(contract=contract).order_by('-pk')
        Data = dict()
        for idx, receipt in enumerate(receipts):
            Data[receipt.id] = [
                '<a href="%s"><i class="fas fa-edit"></i></a>' % (reverse('contract:receipt_edit', args=[receipt.id])) if request.user.has_perm('contract.change_receipt') else '',
                '<a href="%s"><i class="fas fa-trash"></i></a>' % (reverse('contract:receipt_delete', args=[receipt.id])) if request.user.has_perm('contract.delete_receipt') else '',
                '<a href="%s">%s</a>' % (receipt.get_absolute_url(), receipt),
                str(receipt.contract),
                str(receipt.receipt_date),
                str(receipt.receipt_amount),
                str(receipt.payment_date),
                str(receipt.receipt_org),
                str(receipt.payment_method),
                str(receipt.receipt_content),
                str(receipt.memo)
            ]
        DataTablesServer = utils.DataTablesServer(request, columns, receipts, data=Data)
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'contract/receipt_list.html', locals())

class ReceiptDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.view_receipt'
    model = Receipt

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Upload_Image = apps.get_model('contract', 'Upload_Image')
        if Upload_Image.objects.filter(content_type=ContentType.objects.get(app_label='contract', model='receipt'), object_id=self.kwargs.get('pk')):
            tag = True
            upload_image = Upload_Image.objects.get(content_type=ContentType.objects.get(app_label='contract', model='receipt'), object_id=self.kwargs.get('pk'))
            context['upload_image'] = upload_image.image
        else:
            tag = False

        context['tag'] = tag
        return context

class ReceiptCreateView(PermissionRequiredMixin, CreateView_add_log):
    permission_required = 'contract.add_receipt'
    model = Receipt
    form_class = ReceiptCreateForm

class ReceiptUpdateView(PermissionRequiredMixin, UpdateView_add_log):
    permission_required = 'contract.change_receipt'
    model = Receipt
    template_name = 'contract/receipt_change.html'
    form_class = ReceiptUpdateForm

    def post(self, request, *args, **kwargs):
        receipt_upload_image(request, self.kwargs['pk'])
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Upload_Image = apps.get_model('contract', 'Upload_Image')
        if Upload_Image.objects.filter(content_type=ContentType.objects.get(app_label='contract', model='receipt'), object_id=self.kwargs.get('pk')):
            tag = True
            upload_image = Upload_Image.objects.get(content_type=ContentType.objects.get(app_label='contract', model='receipt'), object_id=self.kwargs.get('pk'))
            context['upload_image'] = upload_image.image
        else:
            tag = False
        context['tag'] = tag
        return context

class ReceiptDeleteView(PermissionRequiredMixin, DeleteView_add_log):
    permission_required = 'contract.delete_receipt'
    model = Receipt
    success_url = reverse_lazy('contract:view_contract')

class BoxDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.view_box'
    model = Box

    def get_context_data(self, **kwargs):
        sub_table_list = ['Failed', 'Examiner', 'Destroyed']
        context = super().get_context_data(**kwargs)
        box = self.get_object()
        for Name in sub_table_list:
            name = Name.lower()
            objs = apps.get_model('contract', Name)
            # 若不存在則不輸出
            if objs.objects.filter(box=box):
                obj = objs.objects.get(box=box)
                context[name] = obj
            else:
                context[name] = False
        # experiment
        experiments = Experiment.objects.filter(box=box).order_by('box__id', '-receiving_date','-pk')
        if experiments:
            context['experiment'] = experiments[0]
        else:
            context['experiment'] = False
        context['status'] = utils.get_status(box.id)
        # project
        for Obj in apps.get_app_config('project').get_models():
            if Obj.objects.filter(box=box):
                obj = Obj.objects.get(box=box)
                context['project'] = obj
                break
            else:
                context['project'] = False
        return context

class BoxListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.view_box'
    model = Box
    # 為了輸出與Box有關的資料
    def get_context_data(self, **kwargs):
        sub_table_list = ['Failed', 'Examiner', 'Destroyed']
        context = super().get_context_data(**kwargs)
        for Name in sub_table_list:
            name = Name.lower()
            obj = apps.get_model('contract', Name)
            context[name] = obj
        context['experiment'] = Experiment
        context['get_status'] = utils.get_status
        context['project'] = list()
        for Obj in apps.get_app_config('project').get_models():
            context['project'].append(Obj)
        return context

def getBoxData(request, queryset):
    Data = dict()
    for box in queryset:
        Data[box.id] = [
            '<a href="%s"><i class="fas fa-edit"></i></a>' % (reverse('contract:box_edit', args=[box.id])) if request.user.has_perm('contract.change_box') else '',
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=800\', height=\'600\'); return false"><i class="fas fa-trash"></i></a>' % (reverse('contract:box_delete', args=[box.id]), reverse('contract:box_delete', args=[box.id])) if request.user.has_perm('contract.delete_box') else '',
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=800\', height=\'600\'); return false">%s</a>' % (reverse("contract:box-detail", args=[box.id]), reverse("contract:box-detail", args=[box.id]), box.serial_number),
            str(box.order),
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=800\', height=\'600\'); return false">%s</a>' % (reverse('product:view_product_plan', args=[box.plan.id]), reverse('product:view_product_plan', args=[box.plan.id]), box.plan) if request.user.has_perm('product.view_plan') else '',
            str(box.user.userprofile.nick_name) if box.user else '',
            '<a href="%s">%s</a>' % (Examiner.objects.get(box=box).customer.get_absolute_url(), Examiner.objects.get(box=box).customer) if request.user.has_perm('customer.view_customer') and Examiner.objects.filter(box=box) else '',
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=800\', height=\'600\'); return false">%s</a>' % (Experiment.objects.filter(box=box).order_by('box__id', '-receiving_date','-pk').first().get_absolute_url(), Experiment.objects.filter(box=box).order_by('box__id', '-receiving_date','-pk').first().get_absolute_url(), utils.get_status(box.id)) if request.user.has_perm('experiment.view_experiment') and Experiment.objects.filter(box=box) else utils.get_status(box.id),
            str(box.tracing_number),
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=800\', height=\'600\'); return false"><i class="fas fa-list-alt"></i></a>' % (box.get_project().get_absolute_url(), box.get_project().get_absolute_url()) if box.get_project() else '',
            '失敗' if Failed.objects.filter(box=box) else '-',
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=800\', height=\'600\'); return false">%s</a>' % (Failed.objects.get(box=box).failed_reason.get_absolute_url(), Failed.objects.get(box=box).failed_reason.get_absolute_url(), Failed.objects.get(box=box).failed_reason) if Failed.objects.filter(box=box) else '',
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=800\', height=\'600\'); return false">%s</a>' % (Destroyed.objects.get(box=box).get_absolute_url(), Destroyed.objects.get(box=box).get_absolute_url(), box.get_destroyed()) if request.user.has_perm('contract.view_destroyed') and Destroyed.objects.filter(box=box) else ''
        ]
    return Data

@login_required
@permission_required('contract.view_box', raise_exception=True)
def view_box(request):
    ajax_url = reverse('contract:box-list')
    if request.GET:
        columns = ['id', 'id', 'serial_number', 'order', 'plan', 'user.userprofile.nick_name', 'get_examiner()', 'id', 'tracing_number', 'id', 'get_failed()', 'get_failed_reason()', 'get_destroyed()']
        boxes = Box.objects.all().order_by('-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, boxes)
        DataTablesServer.getData = getBoxData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'contract/box_list.html', locals())

class BoxDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.delete_box'
    model = Box
    success_url = reverse_lazy('contract:box-list')

    # --------- history --------
    def post(self, request, *args, **kwargs):
        sub_table_list = ['Failed', 'Examiner', 'Destroyed']
        obj = self.get_object()
        # 檢查這個box是否與其子表有關係，若有，則因應CASCADE關聯會將子表一同刪除的特性，紀錄子表的刪除紀錄，以下皆同
        for model_name in sub_table_list:
            sub_obj = apps.get_model('contract', model_name)
            if sub_obj.objects.filter(box=obj):
                specify_sub_obj = sub_obj.objects.get(box=obj)
                sub_pre_dict = object_to_dict(specify_sub_obj)
                log_addition(request.user, 'contract', model_name.lower(), specify_sub_obj.id, '3', {}, sub_pre_dict)

        pre_dict = object_to_dict(obj)
        log_addition(request.user, 'contract', 'box', obj.id, '3', {}, pre_dict)
        return super().post(request, *args, **kwargs)
    # --------- history --------

class BoxCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.add_box'
    model = Box
    form_class = MultipleBoxCreateForm

    def form_valid(self, form):
        new_serial_number_list = []
        plan = form.cleaned_data['plan']
        prefix = plan.product.prefix
        num = len(prefix)
        max_number = 0
        quantity = form.cleaned_data['quantity'] # 判斷需要新增幾個box
        box_serial_number_list = Box.objects.filter(serial_number__icontains=prefix).values_list('serial_number').order_by('-serial_number') # 根據serial number大到小排列
        # 上述為找出含有目標prefix的serial number，並由大至小排列，但是今若有MRT、MRTF，兩種prefix
        # 在搜尋含有MRT的serial number時也會將含有MRTF的serial number一並納入
        if box_serial_number_list:
            for box_serial_number in box_serial_number_list:
                total_length = len(box_serial_number[0])
                if (total_length - num) == 6:
                    temp_number = int(box_serial_number[0][num:])
                    if temp_number > max_number:
                        max_number = temp_number
                    else:
                        max_number = max_number
                else:
                    pass
                    # 編號格式有誤
        else:
            max_number = 0

        for i in range(quantity):
            new_serial_number_list.append(prefix + str(max_number+i+1).zfill(6)) # 創造新增的box的serial number，數字會補齊六位
        for list in new_serial_number_list:
            Box.objects.create(
                user = form.cleaned_data['user'],
                serial_number = list,
                plan = form.cleaned_data['plan'],
                order = form.cleaned_data['order'],
                tracing_number = form.cleaned_data['tracing_number'],
            )
            # --------- history --------
            box_new =  Box.objects.all().order_by('-id').first()
            log_addition(self.request.user, 'contract', 'box', box_new.id, '1', object_to_dict(box_new), {})
            # --------- history --------
        return HttpResponseRedirect('/contract/box')

class BoxbyOrderListView(BoxListView):
    model = Box
    # 觀看特定Order的Box
    def get_queryset(self):
        orders = apps.get_model('contract', 'Order')
        order = orders.objects.get(pk=self.kwargs.get('pk'))
        box = Box.objects.filter(order=order)
        return box

@login_required
@permission_required('contract.view_box', raise_exception=True)
def boxbyorderlistview(request, pk):
    ajax_url = reverse('contract:partial-box-list', args=[pk])
    if request.GET:
        columns = ['id', 'id', 'serial_number', 'order', 'plan', 'user.userprofile.nick_name', 'get_examiner()', 'id', 'tracing_number', 'id', 'get_failed()', 'get_failed_reason()', 'get_destroyed()']
        order = Order.objects.get(pk=pk)
        boxes = Box.objects.filter(order=order).order_by('-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, Box.objects.filter(order=order).order_by('-pk'))
        DataTablesServer.getData = getBoxData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'contract/box_list.html', locals())

@login_required
@permission_required('contract.view_box', raise_exception=True)
def boxbycontractlistview(request, pk):
    ajax_url = reverse('contract:contract-box-list', args=[pk])
    if request.GET:
        columns = ['id', 'id', 'serial_number', 'order', 'plan', 'user.userprofile.nick_name', 'get_examiner()', 'id', 'tracing_number', 'id', 'get_failed()', 'get_failed_reason()', 'get_destroyed()']
        contract = Contract.objects.get(pk=pk)
        orders = Order.objects.filter(contract=contract)
        count = True
        for order in orders:
            if count:
                boxes = Box.objects.filter(order=order).order_by('-pk')
                count = False                
            else:
                boxes = boxes | Box.objects.filter(order=order).order_by('-pk')        
        DataTablesServer = utils.DataTablesServer(request, columns, boxes)
        DataTablesServer.getData = getBoxData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'contract/box_list.html', locals())

class FailedListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.view_failed'
    model = Failed

class FailedCreateView(PermissionRequiredMixin, CreateView_add_log):
    permission_required = 'contract.add_failed'
    model = Failed
    form_class = FailedCreateForm
    success_url = reverse_lazy('contract:failed-list')

class FailedUpdateView(PermissionRequiredMixin, UpdateView_add_log):
    permission_required = 'contract.change_failed'
    model = Failed
    fields = ('failed_reason',)
    template_name = 'contract/failed_change.html'
    success_url = reverse_lazy('contract:failed-list')

class FailedDeleteView(PermissionRequiredMixin, DeleteView_add_log):
    permission_required = 'contract.delete_failed'
    model = Failed
    success_url = reverse_lazy('contract:failed-list')

class DestroyedListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.view_deatroyed'
    model = Destroyed

class DestroyedDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.view_deatroyed'
    model = Destroyed

class DestroyedCreateView(PermissionRequiredMixin, CreateView_add_log):
    permission_required = 'contract.add_destroyed'
    model = Destroyed
    form_class = DestroyedCreateForm

class DestroyedUpdateView(PermissionRequiredMixin, UpdateView_add_log):
    permission_required = 'contract.change_destroyed'
    model = Destroyed
    form_class = DestroyedUpdateForm
    template_name = 'contract/destroyed_change.html'

class DestroyedDeleteView(PermissionRequiredMixin, DeleteView_add_log):
    permission_required = 'contract.delete_destroyed'
    model = Destroyed
    success_url = reverse_lazy('contract:destroyed-list')

class Failed_reasonDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.view_failed_reason'
    model = Failed_reason

class Failed_reasonListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.view_failed_reason'
    model = Failed_reason

class Failed_reasonCreateView(PermissionRequiredMixin, CreateView_add_log):
    permission_required = 'contract.add_failed_reason'
    model = Failed_reason
    fields = '__all__'

class Failed_reasonUpdateView(PermissionRequiredMixin, UpdateView_add_log):
    permission_required = 'contract.change_failed_reason'
    model = Failed_reason
    fields = '__all__'
    template_name = 'contract/failed_reason_change.html'
    success_url = reverse_lazy('contract:failed_reason-list')

class Failed_reasonDeleteView(PermissionRequiredMixin, DeleteView_add_log):
    permission_required = 'contract.delete_failed_reason'
    model = Failed_reason
    success_url = reverse_lazy('contract:failed_reason-list')

class ExaminerListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.view_examiner'
    model = Examiner

class ExaminerUpdateView(PermissionRequiredMixin, UpdateView_add_log):
    permission_required = 'contract.change_examiner'
    model = Examiner
    template_name = 'contract/examiner_change.html'
    success_url = reverse_lazy('contract:examiner-list')
    fields = ['customer']

class ExaminerCreateView(PermissionRequiredMixin, CreateView_add_log):
    permission_required = 'contract.add_examiner'
    model = Examiner
    form_class = ExaminerCreateForm
    success_url = reverse_lazy('contract:examiner-list')

class ExaminerDeleteView(PermissionRequiredMixin, DeleteView_add_log):
    permission_required = 'contract.delete_examiner'
    model = Examiner
    success_url = reverse_lazy('contract:examiner-list')

@permission_required('contract.change_box')
@csrf_protect
def BoxUpdateView(request, pk):
    Box = apps.get_model('contract', 'Box')
    box = Box.objects.get(pk=pk)
    proj = Project.objects.filter(product=box.plan.product).first()
    if proj:
        Proj = apps.get_model('project', proj.content_type.model)
        project = Proj.objects.filter(box=box).first()

    # 標記Box是否擁有這些關係
    exist_tag = {'failed':False, 'destroyed':False, 'examiner':False}
    sub_table_list = ['Failed', 'Examiner', 'Destroyed']
    sub_table = {}
    for Name in sub_table_list:
        Obj = apps.get_model('contract', Name)
        name = Name.lower()
        # 若是Box有這些關係則標記為True
        if Obj.objects.filter(box=box):
            obj = Obj.objects.get(box=box)
            exist_tag[name] = True
            sub_table[name] = obj

    if request.method == 'POST':
        form = BoxUpdateForm(request.POST)
        if form.is_valid():
            pre_dict = object_to_dict(box) # history
            box.plan = form.cleaned_data['plan']
            box.order = form.cleaned_data['order']
            box.tracing_number = form.cleaned_data['tracing_number']
            box.save()
            dict = object_to_dict(box) # history
            log_addition(request.user, 'contract', 'box', box.id, '2', dict, pre_dict) # history

            if exist_tag['failed']:
                failed = sub_table['failed']
                pre_dict = object_to_dict(failed) # history
                failed.failed_reason = form.cleaned_data['failed_reason']
                failed.save()
                dict = object_to_dict(failed) # history
                log_addition(request.user, 'contract', 'failed', failed.id, '2', dict, pre_dict) # history

            if exist_tag['destroyed']:
                destroyed = sub_table['destroyed']
                pre_dict = object_to_dict(destroyed) # history
                destroyed.is_sample_destroyed = form.cleaned_data['is_sample_destroyed']
                destroyed.sample_destroyed_date = form.cleaned_data['sample_destroyed_date']
                destroyed.return_date = form.cleaned_data['return_date']
                destroyed.save()
                dict = object_to_dict(destroyed) # history
                log_addition(request.user, 'contract', 'destroyed', destroyed.id, '2', dict, pre_dict) # history

            if exist_tag['examiner']:
                examiner = sub_table['examiner']
                pre_dict = object_to_dict(examiner) # history
                examiner.customer = form.cleaned_data['examiner']
                examiner.save()
                dict = object_to_dict(examiner) # history
                log_addition(request.user, 'contract', 'examiner', examiner.id, '2', dict, pre_dict) # history

            return HttpResponseRedirect('/contract/box')
    else:
        default_data={
            'serial_number':box.serial_number,
            'order':box.order,
            'plan':box.plan,
            'tracing_number':box.tracing_number,
        }
        if exist_tag['failed']:
            default_data['failed_reason'] = sub_table['failed'].failed_reason
        if exist_tag['destroyed']:
            default_data['is_sample_destroyed'] = sub_table['destroyed'].is_sample_destroyed
            default_data['sample_destroyed_date'] = sub_table['destroyed'].sample_destroyed_date
            default_data['return_date'] = sub_table['destroyed'].return_date
        if exist_tag['examiner']:
            default_data['examiner'] = sub_table['examiner'].customer
        form = BoxUpdateForm(default_data)

    context = {
        'form': form,
        'box':box,
        'failed_exist': exist_tag['failed'],
        'destroyed_exist': exist_tag['destroyed'],
        'examiner_exist': exist_tag['examiner'],
        'proj': proj,
        'project': project
    }
    return render(request, 'contract/box_change.html', context)

# 新增資料以固定的BOX
@permission_required('contract.add_failed')
@csrf_protect
def AddSpecifyBoxtoFailed(request, pk):
    Box = apps.get_model('contract', 'Box')
    Failed = apps.get_model('contract', 'Failed')
    box = Box.objects.get(pk=pk)
    failed = Failed()
    specify_box = True
    if request.method == 'POST':
        form = SpecifyFailedCreateForm(request.POST)
        if form.is_valid():
            failed.box = box
            failed.failed_reason = form.cleaned_data['failed_reason']
            failed.save()
            # --------- history --------
            dict = object_to_dict(failed) # history
            log_addition(request.user, 'contract', 'failed', failed.id, '1', dict, {}) # history
            # --------- history --------
            return redirect(reverse('contract:failed-list'))
    else:
        form = SpecifyFailedCreateForm()

    context = {'box':box,'form':form, 'specify_box':specify_box}
    return render(request, 'contract/failed_form.html', context)

# 新增資料以固定的BOX
@permission_required('contract.add_destroyed')
@csrf_protect
def AddSpecifyBoxtoDestroyed(request, pk):
    Box = apps.get_model('contract', 'Box')
    Destroyed = apps.get_model('contract', 'Destroyed')
    box = Box.objects.get(pk=pk)
    destroyed = Destroyed()
    specify_box = True
    if request.method == 'POST':
        form = SpecifyDestroyedCreateForm(request.POST)
        if form.is_valid():
            destroyed.box = box
            destroyed.is_sample_destroyed = form.cleaned_data['is_sample_destroyed']
            destroyed.sample_destroyed_date = form.cleaned_data['sample_destroyed_date']
            destroyed.return_date = form.cleaned_data['return_date']
            destroyed.save()
            # --------- history --------
            dict = object_to_dict(destroyed) # history
            log_addition(request.user, 'contract', 'destroyed', destroyed.id, '1', dict, {}) # history
            # --------- history --------
            return redirect(reverse('contract:destroyed-list'))
    else:
        form = SpecifyDestroyedCreateForm()

    context = {'box':box,'form':form, 'specify_box':specify_box}
    return render(request, 'contract/destroyed_form.html', context)

# 新增資料以固定的BOX
@permission_required('contract.add_examiner')
@csrf_protect
def AddSpecifyBoxtoExaminer(request, pk):
    Box = apps.get_model('contract', 'Box')
    Examiner = apps.get_model('contract', 'Examiner')
    box = Box.objects.get(pk=pk)
    examiner = Examiner()
    specify_box = True
    if request.method == 'POST':
        form = SpecifyExaminerCreateForm(request.POST)
        if form.is_valid():
            examiner.box = box
            examiner.customer = form.cleaned_data['customer']
            examiner.save()
            # --------- history --------
            dict = object_to_dict(examiner) # history
            log_addition(request.user, 'contract', 'examiner', examiner.id, '1', dict, {}) # history
            # --------- history --------
            return redirect(reverse('contract:examiner-list'))
    else:
        form = SpecifyExaminerCreateForm()

    context = {'box':box,'form':form, 'specify_box':specify_box}
    return render(request, 'contract/examiner_form.html', context)

# 新增機構
@permission_required('customer.add_organization')
@csrf_protect
def add_organization(request):
    if request.method == 'POST':
        Organization = apps.get_model('customer', 'Organization')
        # (name, department)必為unique
        exist_organization = Organization.objects.filter(name=request.POST['name'], department=request.POST['department'])
        if exist_organization:
            messages.error(request, '此機構已存在..')
            return HttpResponseRedirect('/contract/add_organization')
        organization = Organization()
        # 機構資料
        organization.name = request.POST['name']
        organization.department = request.POST['department']
        organization.save()
        messages.info(request, '已成功新增機構')
        # --------- history --------
        dict = object_to_dict(organization) # history
        log_addition(request.user, 'customer', 'organization', organization.id, '1', dict, {}) # history
        # --------- history --------
        return redirect(reverse('contract:contract_create'))
    return render(request, 'contract/add_organization.html', locals())

# 新增資料以固定的Contract
@permission_required('contract.add_receipt')
@csrf_protect
def AddSpecifyContracttoReceipt(request, pk):
    Contract = apps.get_model('contract', 'Contract')
    Receipt = apps.get_model('contract', 'Receipt')
    contract = Contract.objects.get(pk=pk)
    receipt = Receipt()
    specify_contract = True
    if request.method == 'POST':
        form = SpecifyReceiptCreateForm(request.POST)
        if form.is_valid():
            receipt.contract = contract
            receipt.receipt_date = form.cleaned_data['receipt_date']
            receipt.receipt_number = form.cleaned_data['receipt_number']
            receipt.receipt_amount = form.cleaned_data['receipt_amount']
            receipt.receipt_date = form.cleaned_data['receipt_date']
            receipt.payment_method = form.cleaned_data['payment_method']
            receipt.memo = form.cleaned_data['memo']
            receipt.save()
            # --------- history --------
            dict = object_to_dict(receipt) # history
            log_addition(request.user, 'contract', 'receipt', receipt.id, '1', dict, {}) # history
            # --------- history --------
            # 連續新增
            return redirect(reverse('contract:add_specify_receipt', args=[contract.id]))
    else:
        form = SpecifyReceiptCreateForm()

    context = {'contract':contract,'form':form, 'specify_contract':specify_contract}
    return render(request, 'contract/receipt_form.html', context)

# 新增資料以固定的Contract
@permission_required('contract.add_order')
@csrf_protect
def AddSpecifyContracttoOrder(request, pk):
    Contract = apps.get_model('contract', 'Contract')
    Order = apps.get_model('contract', 'Order')
    contract = Contract.objects.get(pk=pk)
    order = Order()
    specify_contract = True
    if request.method == 'POST':
        form = SpecifyOrderCreateForm(request.POST)
        if form.is_valid():
            Order2 = apps.get_model('contract', 'order')
            try:
                num = Order2.objects.filter(contract=contract).count()
            except:
                num = 0
            contract_name = contract.contract_name
            order.order_name = contract_name + '-訂單 '+str(num+1)
            order.contract = contract
            order.order_date = form.cleaned_data['order_date']
            order.memo = form.cleaned_data['memo']
            order.save()
            # plan 是複數所以以迴圈處理
            for plan in form.cleaned_data['plan']:
                order.plan.add(plan.id)
            order.save()
            # --------- history --------
            dict = object_to_dict(order) # history
            log_addition(request.user, 'contract', 'order', order.id, '1', dict, {}) # history
            # --------- history --------
            # 連續新增
            return redirect(reverse('contract:add_specify_order', args=[contract.id]))
    else:
        form = SpecifyOrderCreateForm()

    context = {'contract':contract,'form':form, 'specify_contract':specify_contract}
    return render(request, 'contract/order_form.html', context)

# 新增資料以固定的Order
@permission_required('contract.add_box')
@csrf_protect
def AddSpecifyOrdertoBox(request, pk):
    Order = apps.get_model('contract', 'Order')
    Box = apps.get_model('contract', 'Box')
    order = Order.objects.get(pk=pk)
    specify_order = True
    if request.method == 'POST':
        form = SpecifyBoxCreateForm(request.POST)
        if form.is_valid():
            new_serial_number_list = []
            plan = form.cleaned_data['plan']
            prefix = plan.product.prefix
            num = len(prefix)
            max_number = 0
            quantity = form.cleaned_data['quantity'] # 判斷需要新增幾個box
            box_serial_number_list = Box.objects.filter(serial_number__icontains=prefix).values_list('serial_number').order_by('-serial_number') # 根據serial number大到小排列
            # 上述為找出含有目標prefix的serial number，並由大至小排列，但是今若有MRT、MRTF，兩種prefix
            # 在搜尋含有MRT的serial number時也會將含有MRTF的serial number一並納入
            if box_serial_number_list:
                for box_serial_number in box_serial_number_list:
                    total_length = len(box_serial_number[0])
                    if (total_length - num) == 6:
                        temp_number = int(box_serial_number[0][num:])
                        if temp_number > max_number:
                            max_number = temp_number
                        else:
                            max_number = max_number
                    else:
                        pass
                        # 編號格式有誤
            else:
                max_number = 0

            for i in range(quantity):
                new_serial_number_list.append(prefix + str(max_number+i+1).zfill(6))
            for list in new_serial_number_list:
                Box.objects.create(
                    serial_number = list,
                    plan = form.cleaned_data['plan'],
                    order = order,
                    tracing_number = form.cleaned_data['tracing_number'],
                )
                # --------- history --------
                box =  Box.objects.all().order_by('-id').first()
                dict = object_to_dict(box)
                log_addition(request.user, 'contract', 'box', box.id, '1', dict, {}) # history
                # --------- history --------
            # 回到本頁面以進行連續新增            
            return redirect(reverse('contract:add_specify_box', args=[order.id]))
    else:
        form = SpecifyBoxCreateForm()
    
    context = {'order':order,'form':form, 'specify_order':specify_order}
    return render(request, 'contract/box_form.html', context)

class Payment_methodCreateView(PermissionRequiredMixin, CreateView_add_log):
    permission_required = 'contract.add_payment_method'
    model = Payment_method
    fields = '__all__'
    success_url = reverse_lazy('contract:add_payment_method')

class Payment_methodUpdateView(PermissionRequiredMixin, UpdateView_add_log):
    permission_required = 'contract.change_payment_method'
    model = Payment_method
    template_name = 'contract/payment_method_change.html'
    fields = '__all__'
    success_url = reverse_lazy('contract:payment_method-list')

class Payment_methodDeleteView(PermissionRequiredMixin, DeleteView_add_log):
    permission_required = 'contract.delete_payment_method'
    model = Payment_method
    fields = '__all__'
    success_url = reverse_lazy('contract:payment_method-list')

class Payment_methodListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.view_payment_method'
    model = Payment_method

def Search(request):
    model_list = apps.get_app_config('contract').get_models()
    models_list = []
    for model in model_list:
        models_list.append(model._meta.model_name)
    if request.method == "POST":
        return render(request, 'contract/search.html', locals())
    return render(request, 'contract/search.html', locals())

def Upload_image(request, pk):
    header = '上傳圖片'
    content_type = ContentType.objects.get(app_label='contract', model='receipt')
    if request.method == 'POST':
        img = request.FILES.get('sheet')
        if Upload_Image.objects.filter(content_type=content_type, object_id=pk):
            upload_image = Upload_Image.objects.get(content_type=content_type, object_id=pk)
        else:
            upload_image = Upload_Image()
        upload_image.content_type = content_type
        upload_image.object_id = pk
        upload_image.image = img
        upload_image.save()
        messages.info(request, '已成功新增資料')
        return render(request, 'contract/upload.html', locals())
    return render(request, 'contract/upload.html', locals())

def Upload_file(request, pk):
    header = '上傳PDF'
    content_type = ContentType.objects.get(app_label='contract', model='contract')
    if request.method == 'POST':
        file = request.FILES.get('sheet')
        if Upload_File.objects.filter(content_type=content_type, object_id=pk):
            upload_file = Upload_File.objects.get(content_type=content_type, object_id=pk)
        else:
            upload_file = Upload_File()
        upload_file.content_type = content_type
        upload_file.object_id = pk
        upload_file.file_upload = file
        upload_file.save()
        messages.info(request, '已成功新增資料')
        return render(request, 'contract/upload.html', locals())
    return render(request, 'contract/upload.html', locals())

def receipt_upload_image(request, pk):
    if request.FILES.get('sheet'):
        content_type = ContentType.objects.get(app_label='contract', model='receipt')
        img = request.FILES.get('sheet')
        if Upload_Image.objects.filter(content_type=content_type, object_id=pk):
            upload_image = Upload_Image.objects.get(content_type=content_type, object_id=pk)
            upload_image.image = img
            upload_image.save()
        else:
            upload_image = Upload_Image()
            upload_image.content_type = content_type
            upload_image.object_id = pk
            upload_image.image = img
            upload_image.save()

def contract_upload_file(request, pk):
    if request.FILES.get('sheet'):
        content_type = ContentType.objects.get(app_label='contract', model='contract')
        file = request.FILES.get('sheet')
        if Upload_File.objects.filter(content_type=content_type, object_id=pk):
            upload_file = Upload_File.objects.get(content_type=content_type, object_id=pk)
        else:
            upload_file = Upload_File()
        upload_file.content_type = content_type
        upload_file.object_id = pk
        upload_file.file_upload = file
        upload_file.save()

@login_required
def update_element(reuqest, model, pk):
    if model == 'box':
        app = 'contract'
        try:
            Model = apps.get_model(app, model)
            id_model = apps.get_model(app, 'order')
            order = id_model.objects.get(pk=pk)
            objects = [[obj.id, obj.get_absolute_url(), str(obj)] for obj in Model.objects.filter(order=order)]
        except LookupError:
            objects = []
    elif model == 'experiment':
        app = 'experiment'
        try:
            distinct = []
            obj_distinct_list = []
            Model = apps.get_model(app, model)
            id_model = apps.get_model('contract', 'order')
            Box = apps.get_model('contract', 'box')
            order = id_model.objects.get(pk=pk)
            box = Box.objects.filter(order=order)
            obj_list = Model.objects.filter(box__in=box)
            for obj_distinct in obj_list:
                if obj_distinct.box.serial_number in distinct:
                    continue
                else:
                    obj_distinct_list.append(obj_distinct)
                    distinct.append(obj_distinct.box.serial_number)
            print(obj_distinct_list)
            objects = [[obj.id, obj.get_absolute_url(), str(obj.box)] for obj in obj_distinct_list]
        except LookupError:
            objects = []
    return JsonResponse({'objects': objects})

def add_multi_tracing_number(request):
    form = TracingNumberMultiUpdateForm(auto_id='%s')
    AddMultiple = utils.AddMultiple(request=request, form=form)
    AddMultipleView = AddMultiple.AddMultipleView(header='新增多筆採樣盒宅配單號', view_url=reverse('contract:box-list'), add_multiple_url=reverse('contract:add_multiple_number'))
    if request.method == 'POST':
        response = {'response': False, 'messages': list()}
        if request.POST.get('table_content'):
            label_dict = utils.getlabels('contract', 'box')
            contents = json.loads(request.POST.get('table_content'), parse_float=Decimal)
            # Plan = apps.get_model('product', 'plan')
            data_list = list()
            errors = list()
            for idx, content in enumerate(contents):
                if all(x is None or str(x).strip() == '' for x in content):
                    # check if all elements of the content is None
                    continue
                else:
                    content_dict = dict(zip(AddMultiple.field_names, content))
                    try:
                        box = Box.objects.get(serial_number = content_dict['serial_number'])
                        exist_box = Box.objects.get(serial_number = box.serial_number)
                        box.serial_number = content_dict['serial_number']
                        box.tracing_number = content_dict['tracing_number']
                        try:
                            box.full_clean()
                        except ValidationError as err:
                            for key in err.message_dict:
                                errors.append('%s: %s (第%d行)' % (label_dict[key], ';'.join(err.message_dict[key]), idx+1))
                        data_list.append(box)
                    except Box.DoesNotExist:
                        errors.append('%s: 此欄位 (第%d行) 編號不存在' % (label_dict['serial_number'], idx+1))
                    except StopIteration:
                        if not content_dict['serial_number']:
                            errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['serial_number'], idx+1))
                        if not content_dict['tracing_number']:
                            errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['serial_number'], idx+1))
            if not errors:
                # 全對才存
                for box in data_list:
                    action_flag = '2'
                    pre_dict = object_to_dict(exist_box)
                    box.save()
                    log_addition(request.user, 'contract', 'box', box.id, action_flag, object_to_dict(box), pre_dict)
                    response['response'] = True
                    response['messages'].append('已成功新增/更新資料')
            else:
                response['messages'].extend(errors)
        return JsonResponse(response)
    return AddMultipleView
