# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import datetime
from lib.multi_add import AddMultiData
from lib.Validator import ValidateOrganization
from django.core.exceptions import ValidationError
from customer.models import Organization, Customer, Title, Job, Customer_Type, Relationship, Customer_Data
from contract.models import Box, Examiner
from django.template.defaulttags import register
from history.models import History
from history.function import log_addition, object_to_dict, Update_log_dict, Create_log_dict
from customer.forms import CustomerCreateForm, GetCreateForm
from lib import utils
import json
from decimal import Decimal
# import customer.models as customer_models

# Create your views here.
@login_required
@permission_required('customer.add_organization', raise_exception=True)
@csrf_protect
def add_organization(request):
    FormClass = GetCreateForm(Organization)
    form = FormClass(instance=Organization(), auto_id='%s')
    if request.method == 'POST':
        form = FormClass(request.POST, auto_id='%s')
        if form.is_valid():
            organization = form.save()
            log_addition(request.user, 'customer', 'organization', organization.id, '1', object_to_dict(organization), {})
            messages.info(request, '已成功新增機構')
            return redirect(reverse('customer:add_organization'))
        else:
            messages.error(request, '此機構已存在')
    return render(request, 'customer/add_organization.html', locals())

@login_required
@permission_required('customer.change_organization', raise_exception=True)
@csrf_protect
def change_organization(request, pk):
    FormClass = GetCreateForm(Organization)
    organization = Organization.objects.get(id=pk)
    form = FormClass(instance=organization, auto_id='%s')
    if request.method == 'POST':
        form = FormClass(request.POST, instance=organization, auto_id='%s')
        if form.is_valid():
            pre_dict = object_to_dict(organization)
            organization = form.save(commit=False)
            organization.id = pk
            organization.save()
            log_addition(request.user, 'customer', 'organization', organization.id, '2', object_to_dict(organization), pre_dict)
            messages.info(request, '已成功更新機構')
            return redirect(reverse('customer:view_organization'))
        else:
            messages.error(request, '此機構已存在')
    return render(request, 'customer/change_organization.html', locals())

@login_required
@permission_required('customer.view_organization', raise_exception=True)
def view_organization(request):
    organizations = Organization.objects.all().order_by('-pk')
    return render(request, 'customer/view_organization.html', locals())

@login_required
@permission_required('customer.add_customer', raise_exception=True)
@csrf_protect
def add_customer(request):
    field_tags = utils.getlabels('customer', 'customer')
    form = CustomerCreateForm(auto_id='%s')
    if request.method == 'POST':
        # (last_name, first_name, job)必為unique
        form = CustomerCreateForm(request.POST, auto_id='%s')
        if form.is_valid():
            customer = form.save()
            log_addition(request.user, 'customer', 'customer', customer.id, '1', object_to_dict(customer), {})
            messages.info(request, '已成功新增客戶')
            return redirect(reverse('customer:add_customer'))
        else:
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (field_tags[key], error))
                    except KeyError:
                        messages.error(request, '此客戶已存在')
    return render(request, 'customer/add_customer.html', locals())

@login_required
@permission_required('customer.add_customer', raise_exception=True)
@csrf_protect
def add_multiple(request):
    form = CustomerCreateForm(auto_id='%s')
    AddMultiple = utils.AddMultiple(request=request, form=form)
    AddMultipleView = AddMultiple.AddMultipleView(header='新增多筆客戶', view_url=reverse('customer:view_customer'), add_multiple_url=reverse('customer:add_multiple'))
    if request.method == 'POST':
        response = {'response': False, 'messages': list()}
        if request.POST.get('table_content'):
            label_dict = utils.getlabels('customer', 'customer')
            contents = json.loads(request.POST.get('table_content'), parse_float=Decimal)
            customer_list = list()
            errors = list()
            for idx, content in enumerate(contents):
                if all(x is None or str(x).strip() == '' for x in content):
                    # check if all elements of the content is None
                    continue
                else:
                    content_dict = dict(zip(AddMultiple.field_names, content))
                    try:
                        customer = Customer()
                        customer.__dict__.update(content_dict)
                        customer.job = Job.objects.get(name=content_dict['job'])
                        customer.customer_type = Customer_Type.objects.get(name=content_dict['customer_type'])
                        if content_dict['organization']:
                            try:
                                customer.organization = next(o for o in Organization.objects.all() if str(o) == content_dict['organization'])
                            except StopIteration:
                                errors.append('%s: 找不到此機構 (第%d行)' % (label_dict['organization'], idx+1))
                        if content_dict['title']:
                            customer.title = Title.objects.get(name=content_dict['title'])
                        # introducter非必填
                        if content_dict['introducer']:
                            try:
                                customer.introducer = next(c for c in Customer.objects.all() if str(c) == content_dict['introducer'])
                            except StopIteration:
                                errors.append('%s: 找不到此推薦人 (第%d行)' % (label_dict['introducer'], idx+1))
                        if content_dict['relationship']:
                            customer.relationship = Relationship.objects.get(name=content_dict['relationship'])
                        try:
                            customer.full_clean()
                        except ValidationError as err:
                            for key in err.message_dict:
                                try:
                                    errors.append('%s: %s (第%d行)' % (label_dict[key], ';'.join(err.message_dict[key]), idx+1))
                                except KeyError:
                                    errors.append('此客戶已存在 (第%d行)' % (idx+1))
                        customer_list.append(customer)
                    except Job.DoesNotExist:
                        errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['job'], idx+1))
                    except Title.DoesNotExist:
                        errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['title'], idx+1))
                    except Customer_Type.DoesNotExist:
                        errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['customer_type'], idx+1))
                    except Relationship.DoesNotExist:
                        errors.append('%s: 找不到此關係 (第%d行)' % (label_dict['relationship'], idx+1))
            if not errors:
                # 全部對才存，只新增不更新
                for customer in customer_list:
                    customer.save()
                    log_addition(request.user, 'customer', 'customer', customer.id, '1', object_to_dict(customer), {})
                response['response'] = True
                response['messages'].append('已成功新增資料')
            else:
                response['messages'].extend(errors)
        return JsonResponse(response)
    return AddMultipleView

@login_required
@permission_required('customer.change_customer', raise_exception=True)
@csrf_protect
def change_customer(request, pk):
    field_tags = utils.getlabels('customer', 'customer')
    customer = Customer.objects.get(id=pk)
    form = CustomerCreateForm(instance=customer, auto_id='%s')
    if request.method == 'POST':
        form = CustomerCreateForm(request.POST, instance=customer, auto_id='%s')
        if form.is_valid():
            upload_customer_file(request, pk)
            pre_dict = object_to_dict(customer)
            customer = form.save(commit=False)
            customer.id = pk
            customer.save()
            log_addition(request.user, 'customer', 'customer', customer.id, '2', object_to_dict(customer), pre_dict)
            messages.info(request, '已成功更新客戶')
            return redirect(reverse('customer:view_customer'))
        else:
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (field_tags[key], error))
                    except KeyError:
                        messages.error(request, '此客戶已存在')
    return render(request, 'customer/change_customer.html', locals())

def getCustomerData(request, queryset):
    Data = dict()
    for customer in queryset:
        Data[customer.id] = [
            '<a href="%s"><i class="fas fa-edit"></i></a>' % (reverse('customer:change_customer', args=[customer.id])) if request.user.has_perm('customer.change_customer') else '',
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=700\', height=\'800\'); return false">%s</a>' % (customer.get_absolute_url(), customer.get_absolute_url(), customer),
            str(customer.organization),
            str(customer.job),
            str(customer.title),
            str(customer.email),
            str(customer.mobile),
            str(customer.tel),
            str(customer.address)
        ]
    return Data

@login_required
@permission_required('customer.view_customer', raise_exception=True)
def view_customer(request):
    if request.GET:
        columns = ['id', '__str__', 'organization', 'job', 'title', 'email', 'mobile', 'tel', 'address']
        customers = Customer.objects.all().order_by('-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, customers)
        DataTablesServer.getData = getCustomerData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'customer/view_customer.html', locals())

@login_required
@permission_required('customer.add_title', raise_exception=True)
@csrf_protect
def add_title(request):
    FormClass = GetCreateForm(Title)
    form = FormClass(instance=Title(), auto_id='%s')
    if request.method == 'POST':
        form = FormClass(request.POST, auto_id='%s')
        if form.is_valid():
            title = form.save()
            log_addition(request.user, 'customer', 'title', title.id, '1', object_to_dict(title), {})
            messages.info(request, '已成功新增職稱')
            return redirect(reverse('customer:add_title'))
        else:
            messages.error(request, '此職稱已存在')
    return render(request, 'customer/add_title.html', locals())

@login_required
@permission_required('customer.view_title', raise_exception=True)
def view_title(request):
    titles = Title.objects.all().order_by('-pk')
    return render(request, 'customer/view_title.html', locals())

@login_required
@permission_required('customer.change_title', raise_exception=True)
@csrf_protect
def change_title(request, pk):
    FormClass = GetCreateForm(Title)
    title = Title.objects.get(id=pk)
    form = FormClass(instance=title, auto_id='%s')
    if request.method == 'POST':
        form = FormClass(request.POST, instance=title, auto_id='%s')
        if form.is_valid():
            pre_dict = object_to_dict(title)
            title = form.save(commit=False)
            title.id = pk
            title.save()
            log_addition(request.user, 'customer', 'title', title.id, '2', object_to_dict(title), pre_dict)
            messages.info(request, '已成功更新職稱')
            return redirect(reverse('customer:view_title'))
        else:
            messages.error(request, '此職稱已存在')
    return render(request, 'customer/change_title.html', locals())

@login_required
@permission_required('customer.add_job', raise_exception=True)
@csrf_protect
def add_job(request):
    FormClass = GetCreateForm(Job)
    form = FormClass(instance=Job(), auto_id='%s')
    if request.method == 'POST':
        form = FormClass(request.POST, auto_id='%s')
        if form.is_valid():
            job = form.save()
            log_addition(request.user, 'customer', 'job', job.id, '1', object_to_dict(job), {})
            messages.info(request, '已成功新增職業')
            return redirect(reverse('customer:add_job'))
        else:
            messages.error(request, '此職業已存在')
    return render(request, 'customer/add_job.html', locals())

@login_required
@permission_required('customer.view_job', raise_exception=True)
def view_job(request):
    jobs = Job.objects.all().order_by('-pk')
    return render(request, 'customer/view_job.html', locals())

@login_required
@permission_required('customer.change_job', raise_exception=True)
@csrf_protect
def change_job(request, pk):
    FormClass = GetCreateForm(Job)
    job = Job.objects.get(id=pk)
    form = FormClass(instance=job, auto_id='%s')
    if request.method == 'POST':
        form = FormClass(request.POST, instance=job, auto_id='%s')
        if form.is_valid():
            pre_dict = object_to_dict(job)
            job = form.save(commit=False)
            job.id = pk
            job.save()
            log_addition(request.user, 'customer', 'job', job.id, '2', object_to_dict(job), pre_dict)
            messages.info(request, '已成功更新職業')
            return redirect(reverse('customer:view_job'))
        else:
            messages.error(request, '此職業已存在')
    return render(request, 'customer/change_job.html', locals())

@login_required
@permission_required('customer.view_customer', raise_exception=True)
def view_specific_customer(request, pk):
    form = CustomerCreateForm(auto_id='%s')
    customer = Customer.objects.get(id=pk)
    customer_data = Customer_Data.objects.filter(customer = customer)
    customers_data = {}
    for data in customer_data:
        customers_data[data] = data.file
    field_names = list(form.fields.keys())
    field_tags = utils.getlabels('customer', 'customer')
    boxes = Box.objects.filter(pk__in=list(Examiner.objects.filter(customer=customer).values_list('id', flat=True))).order_by('-pk')
    return render(request, 'customer/view_specific_customer.html', locals())

@login_required
def update_options(reuqest, model):
    try:
        Model = apps.get_model('customer', model)
        objects = [[obj.id, str(obj)] for obj in Model.objects.all()]
    except LookupError:
        objects = []
    return JsonResponse({'objects': objects})

@login_required
def get_customer_organization(request, pk):
    customer = Customer.objects.get(id=pk)
    return JsonResponse({'organization_id': customer.organization.id if customer.organization else ''})

@login_required
def upload_customer_file(request, pk):
    if request.FILES.get('sheet'):
        customer = Customer.objects.get(id=pk)
        file = request.FILES.get('sheet')
        Customer_Data.objects.create(
            customer = customer,
            file = file,
        )