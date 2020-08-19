from django.shortcuts import render, redirect
from .models import Contract, Payment_method, Order, Receipt, Failed_reason, Box, Failed, Destroyed, Examiner, Order_quantity
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from .forms import (DestroyedCreateForm, DestroyedUpdateForm, FailedCreateForm, BoxUpdateForm, SpecifyFailedCreateForm,
                    SpecifyDestroyedCreateForm, ExaminerCreateForm, SpecifyExaminerCreateForm, OrderUpdateForm, OrderCreateForm,
                    ContractCreateForm, ContractUpdateForm, ReceiptUpdateForm, SpecifyReceiptCreateForm, SpecifyOrderCreateForm, 
                    SpecifyBoxCreateForm, ReceiptCreateForm, MultipleBoxCreateForm, MultipleSerialNumberCreateForm)
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
# @login_required
# @permission_required()
class ContractListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.can_add_contract'
    model = Contract

class ContractCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.can_add_contract'
    model = Contract
    form_class = ContractCreateForm
    success_url = reverse_lazy('contract:view_contract')

class ContractUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'contract.can_change_contract'
    model = Contract
    form_class = ContractUpdateForm
    template_name = 'contract/contract_change.html'
    success_url = reverse_lazy('contract:view_contract')
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
    permission_required = 'contract.can_delete_contract'
    model = Contract
    success_url = reverse_lazy('contract:view_contract')


class OrderDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.can_view_order'
    model = Order
    # 傳入Box以取得屬於本Order的Box
    def get_context_data(self, **kwargs):
        all_order_quantity = apps.get_model('contract', 'Order_quantity')
        all_box = apps.get_model('contract', 'Box')
        order = Order.objects.get(pk=self.kwargs.get('pk'))
        order_quantity = all_order_quantity.objects.filter(order=order)
        box = all_box.objects.filter(order=order)
        context = super().get_context_data(**kwargs)
        context['order_quantity'] = order_quantity
        context['box'] = box
        return context

class OrderListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.can_view_order'
    model = Order
    template_name = 'contract/order_list.html'
    # # 傳入Box以取得對應Order的Box
    def get_context_data(self, **kwargs):
        order_quantity = apps.get_model('contract', 'Order_quantity')
        box = apps.get_model('contract', 'Box')
        context = super().get_context_data(**kwargs)
        context['order_quantity'] = order_quantity
        context['box'] = box
        return context

class OrderUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'contract.can_change_order'
    model = Order
    form_class = OrderUpdateForm
    template_name = 'contract/order_change.html'

    def get_context_data(self, **kwargs):
        Box = apps.get_model('contract', 'Box')        
        order = Order.objects.get(pk=self.kwargs.get('pk'))
        box_list = Box.objects.filter(order=order).order_by('serial_number')
        context = super().get_context_data(**kwargs)
        # box_list 用以顯示Order中的Box
        context['box_list'] = box_list
        return context

class OrderCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.can_add_order'
    model = Order
    form_class = OrderCreateForm
    template_name = 'contract/order_form.html'
    success_url = reverse_lazy('contract:order-list')
    
    # 處理box新增
    def post(self, request):
        form = self.form_class(request.POST)
        order = Order()
        if form.is_valid():
            
            order.order_date=form.cleaned_data['order_date']
            order.contract=form.cleaned_data['contract']            
            order.memo=form.cleaned_data['memo']
            order.save()
            for plan in form.cleaned_data['plan']:
                order.plan.add(plan.id)
            order.save()
            
            order_new = Order.objects.all().order_by('-id').first()            

            for plan in form.cleaned_data['plan']:
                quantity_tag = plan.name+'_quantity'
                tracing_number_tag = plan.name+'_tracing_number'
                quantity = request.POST[quantity_tag]
                tracing_number = request.POST[tracing_number_tag]
                new_serial_number_list = []
                box_serial_number_list = Box.objects.filter(plan=plan).values_list('serial_number').order_by('-serial_number')
                max_serial_number = box_serial_number_list[0][0]
                perfix = max_serial_number[:3]
                max_number = int(max_serial_number[3:])
                for i in range(int(quantity)):
                    new_serial_number_list.append(perfix + str(max_number+i+1).zfill(6))
                for list in new_serial_number_list:
                    Box.objects.create(
                    serial_number = list,
                    plan = plan,
                    order = order_new,
                    tracing_number = tracing_number
                    )
            return HttpResponseRedirect('/contract/order/order_list')
        return render(request, self.template_name, {'form':form})

class OrderDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.can_delete_order'
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

class ReceiptListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.can_view_receipt'
    model = Receipt

class ReceiptbyContract(ReceiptListView):
    def get_queryset(self):
        contracts = apps.get_model('contract', 'Contract')
        contract = contracts.objects.get(pk=self.kwargs.get('pk'))
        receipt = Receipt.objects.filter(contract=contract)
        return receipt

class ReceiptDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.can_view_receipt'
    model = Receipt

class ReceiptCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.can_add_receipt'
    model = Receipt    
    form_class = ReceiptCreateForm

class ReceiptUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'contract.can_change_receipt'
    model = Receipt
    template_name = 'contract/receipt_change.html'
    form_class = ReceiptUpdateForm

class ReceiptDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.can_delete_receipt'
    model = Receipt
    success_url = reverse_lazy('contract:view_contract')

class BoxDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.can_view_box'
    model = Box

    def get_context_data(self, **kwargs):
        faileds = apps.get_model('contract', 'Failed')
        examiners = apps.get_model('contract', 'Examiner')
        destroyeds = apps.get_model('contract', 'Destroyed')
        all_box = apps.get_model('contract', 'Box')
        box = all_box.objects.get(pk=self.kwargs.get('pk'))
        context = super().get_context_data(**kwargs)
        # 若不存在則不輸出
        if faileds.objects.filter(box=box):
            failed = faileds.objects.get(box=box)
            context['failed'] = failed
        else:
            context['failed'] = False

        if examiners.objects.filter(box=box):
            examiner = examiners.objects.get(box=box)
            context['examiner'] = examiner
        else:
            context['examiner'] = False

        if destroyeds.objects.filter(box=box):
            destroyed = destroyeds.objects.get(box=box)
            context['destroyed'] = destroyed
        else:
            context['destroyed'] = False

        return context

class BoxListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.can_view_box'
    model = Box
    # 為了輸出與Box有關的資料
    def get_context_data(self, **kwargs):
        failed = apps.get_model('contract', 'Failed')
        examiner = apps.get_model('contract', 'Examiner')
        destroyed = apps.get_model('contract', 'Destroyed')
        context = super().get_context_data(**kwargs)
        context['failed'] = failed
        context['examiner'] = examiner
        context['destroyed'] = destroyed
        return context

class BoxDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.can_delete_box'
    model = Box
    success_url = reverse_lazy('contract:box-list')

class BoxCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.can_add_box'
    model = Box
    form_class = MultipleBoxCreateForm
    success_url = reverse_lazy('contract:box-list')

    # def get_context_data(self, **kwargs):       
    #     box_serial_number_list = Box.objects.all().values_list('serial_number').order_by('-serial_number')
    #     max_serial_number = box_serial_number_list[0][0]
    #     perfix = max_serial_number[:3]
    #     max_number = int(max_serial_number[3:])
    #     context = super().get_context_data(**kwargs)
    #     context['perfix'] = perfix
    #     context['max_number'] = max_number
    #     context['max_serial_number'] = max_serial_number
    #     return context

    def form_valid(self, form):
        new_serial_number_list = []
        plan = form.cleaned_data['plan']
        quantity = form.cleaned_data['quantity']
        box_serial_number_list = Box.objects.filter(plan=plan).values_list('serial_number').order_by('-serial_number')
        max_serial_number = box_serial_number_list[0][0]
        perfix = max_serial_number[:3]
        max_number = int(max_serial_number[3:])
        for i in range(quantity):
            new_serial_number_list.append(perfix + str(max_number+i+1).zfill(6))
        for list in new_serial_number_list:
            Box.objects.create(
                serial_number = list,
                plan = form.cleaned_data['plan'],
                order = form.cleaned_data['order'],
                tracing_number = form.cleaned_data['tracing_number'],
            )
        return HttpResponseRedirect('/contract/box/box_list')

class BoxbyOrderListView(BoxListView):
    model = Box
    # 觀看特定Order的Box
    def get_queryset(self):
        orders = apps.get_model('contract', 'Order')
        order = orders.objects.get(pk=self.kwargs.get('pk'))
        box = Box.objects.filter(order=order)
        return box

class FailedListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.can_view_failed'
    model = Failed

class FailedCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.can_add_failed'
    model = Failed    
    form_class = FailedCreateForm
    success_url = reverse_lazy('contract:failed-list')

class FailedUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'contract.can_change_failed'
    model = Failed
    fields = ('failed_reason',)
    template_name = 'contract/failed_change.html'
    success_url = reverse_lazy('contract:failed-list')

class FailedDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.can_delete_failed'
    model = Failed
    success_url = reverse_lazy('contract:failed-list')

class DestroyedListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.can_view_deatroyed'
    model = Destroyed

class DestroyedDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.can_view_deatroyed'
    model = Destroyed

class DestroyedCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.can_add_destroyed'
    model = Destroyed
    form_class = DestroyedCreateForm

class DestroyedUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'contract.can_change_destroyed'
    model = Destroyed
    form_class = DestroyedUpdateForm
    template_name = 'contract/destroyed_change.html'

class DestroyedDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.can_delete_destroyed'
    model = Destroyed
    success_url = reverse_lazy('contract:destroyed-list')

class Failed_reasonDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'contract.can_view_failed_reason'
    model = Failed_reason

class Failed_reasonListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.can_view_failed_reason'
    model = Failed_reason

class Failed_reasonCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.can_add_failed_reason'
    model = Failed_reason
    fields = '__all__'

class Failed_reasonUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'contract.can_change_failed_reason'
    model = Failed_reason
    fields = '__all__'
    template_name = 'contract/failed_reason_change.html'
    success_url = reverse_lazy('contract:failed_reason-list')

class Failed_reasonDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.can_delete_failed_reason'
    model = Failed_reason

class ExaminerListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.can_view_examiner'
    model = Examiner

class ExaminerUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'contract.can_change_examiner'
    model = Examiner
    template_name = 'contract/examiner_change.html'
    success_url = reverse_lazy('contract:examiner-list')
    fields = {'customer',}

class ExaminerCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.can_add_examiner'
    model = Examiner
    form_class = ExaminerCreateForm
    success_url = reverse_lazy('contract:examiner-list')

class ExaminerDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.can_delete_examiner'
    model = Examiner
    success_url = reverse_lazy('contract:examiner-list')

@permission_required('contract.can_change_box')
@csrf_protect
def BoxUpdateView(request, pk):
    Box = apps.get_model('contract', 'Box')
    Failed = apps.get_model('contract', 'Failed')
    Destroyed = apps.get_model('contract', 'Destroyed')    
    Examiner = apps.get_model('contract', 'Examiner')    
    box = Box.objects.get(pk=pk)
    # 標記Box是否擁有這些關係
    failed_exist = False
    destroyed_exist = False
    examiner_exist = False
    # 若是Box有這些關係則標記為True
    if Failed.objects.filter(box=box): # filter 存在與否會回傳boolean, get 會回傳DoesNotExist
        failed = Failed.objects.get(box=box)
        failed_exist = True
    if Destroyed.objects.filter(box=box):
        destroyed = Destroyed.objects.get(box=box)
        destroyed_exist = True
    if Examiner.objects.filter(box=box):
        examiner = Examiner.objects.get(box=box)
        examiner_exist = True
    
    if request.method == 'POST':
        form = BoxUpdateForm(request.POST)
        if form.is_valid():
            box.serial_number = form.cleaned_data['serial_number']
            box.plan = form.cleaned_data['plan']
            box.order = form.cleaned_data['order']
            box.tracing_number = form.cleaned_data['tracing_number']
            box.save()

            if failed_exist:
                failed.failed_reason = form.cleaned_data['failed_reason']
                failed.save()

            if destroyed_exist:
                destroyed.is_sample_destroyed = form.cleaned_data['is_sample_destroyed']
                destroyed.sample_destroyed_date = form.cleaned_data['sample_destroyed_date']
                destroyed.return_date = form.cleaned_data['return_date']
                destroyed.save()

            if examiner_exist:
                examiner.customer = form.cleaned_data['examiner']
                examiner.save()

            return HttpResponseRedirect('/contract/box/box_list')
    else:
        default_data={
            'serial_number':box.serial_number,
            'order':box.order,
            'plan':box.plan,
            'tracing_number':box.tracing_number,
        }
        if failed_exist:
            default_data['failed_reason'] = failed.failed_reason
        if destroyed_exist:
            default_data['is_sample_destroyed'] = destroyed.is_sample_destroyed
            default_data['sample_destroyed_date'] = destroyed.sample_destroyed_date
            default_data['return_date'] = destroyed.return_date
        if examiner_exist:
            default_data['examiner'] = examiner.customer
        form = BoxUpdateForm(default_data)

    context = {
        'form': form,
        'box':box,
        'failed_exist': failed_exist,
        'destroyed_exist': destroyed_exist,
        'examiner_exist': examiner_exist,
    }
    return render(request, 'contract/box_change.html', context)

# 新增資料以固定的BOX
@permission_required('contract.can_add_failed')
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
            return redirect(reverse('contract:failed-list'))
    else:        
        form = SpecifyFailedCreateForm()
        
    context = {'box':box,'form':form, 'specify_box':specify_box}
    return render(request, 'contract/failed_form.html', context)

# 新增資料以固定的BOX
@permission_required('contract.can_add_destroyed')
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
            return redirect(reverse('contract:destroyed-list'))
    else:        
        form = SpecifyDestroyedCreateForm()
        
    context = {'box':box,'form':form, 'specify_box':specify_box}
    return render(request, 'contract/destroyed_form.html', context)

# 新增資料以固定的BOX
@permission_required('contract.can_add_examiner')
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
            return redirect(reverse('contract:examiner-list'))
    else:        
        form = SpecifyExaminerCreateForm()
        
    context = {'box':box,'form':form, 'specify_box':specify_box}
    return render(request, 'contract/examiner_form.html', context)
# 新增機構
@permission_required('customer.can_add_organization')
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
        return redirect(reverse('contract:contract_create'))
    return render(request, 'contract/add_organization.html', locals())

# 新增資料以固定的Contract
@permission_required('contract.can_add_receipt')
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
            #連續新增
            return redirect(reverse('contract:add_specify_receipt', args=[contract.id]))
    else:        
        form = SpecifyReceiptCreateForm()
        
    context = {'contract':contract,'form':form, 'specify_contract':specify_contract}
    return render(request, 'contract/receipt_form.html', context)

# 新增資料以固定的Contract
@permission_required('contract.can_add_order')
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
            order.contract = contract
            order.order_date = form.cleaned_data['order_date']            
            order.memo = form.cleaned_data['memo']
            order.save()
            # plan 是複數所以以迴圈處理
            for plan in form.cleaned_data['plan']:
                order.plan.add(plan.id)
            order.save()
            # 連續新增
            return redirect(reverse('contract:add_specify_order', args=[contract.id]))
    else:        
        form = SpecifyOrderCreateForm()
        
    context = {'contract':contract,'form':form, 'specify_contract':specify_contract}
    return render(request, 'contract/order_form.html', context)

# 新增資料以固定的Order
@permission_required('contract.can_add_box')
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
            quantity = form.cleaned_data['quantity']
            box_serial_number_list = Box.objects.filter(plan=plan).values_list('serial_number').order_by('-serial_number')
            max_serial_number = box_serial_number_list[0][0]
            perfix = max_serial_number[:3]
            max_number = int(max_serial_number[3:])
            for i in range(quantity):
                new_serial_number_list.append(perfix + str(max_number+i+1).zfill(6))
            for list in new_serial_number_list:
                Box.objects.create(
                    serial_number = list,
                    plan = form.cleaned_data['plan'],
                    order = order,
                    tracing_number = form.cleaned_data['tracing_number'],
                )
            # 回到本頁面以進行連續新增
            return redirect(reverse('contract:add_specify_box', args=[order.id]))
    else:        
        form = SpecifyBoxCreateForm()
        
    context = {'order':order,'form':form, 'specify_order':specify_order}
    return render(request, 'contract/box_form.html', context)

class Payment_methodCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'contract.can_add_payment_method'
    model = Payment_method
    fields = '__all__'
    success_url = reverse_lazy('contract:add_payment_method')

class Payment_methodUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'contract.can_change_payment_method'
    model = Payment_method
    template_name = 'contract/payment_method_change.html'
    fields = '__all__'
    success_url = reverse_lazy('contract:payment_method-list')

class Payment_methodDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'contract.can_delete_payment_method'
    model = Payment_method
    fields = '__all__'
    success_url = reverse_lazy('contract:payment_method-list')

class Payment_methodListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'contract.can_view_payment_method'
    model = Payment_method