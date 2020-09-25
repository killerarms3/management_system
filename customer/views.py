# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import datetime
from lib.multi_add import AddMultiData
from lib.Validator import ValidateOrganization
from django.core.exceptions import ValidationError
from customer.models import Organization, Customer, Customer_Organization, Title, Job, Customer_Type
from django.template.defaulttags import register
from history.models import History
from history.function import log_addition, object_to_dict, Update_log_dict, Create_log_dict

# import customer.models as customer_models

# Create your views here.
@login_required
@permission_required('customer.add_organization', raise_exception=True)
@csrf_protect
def add_organization(request):
    if request.method == 'POST':
        # (name, department)必為unique
        organization, created = Organization.objects.get_or_create(name=request.POST['name'], department=request.POST['department'])
        if not created:
            messages.error(request, '此機構已存在')
            return redirect(reverse('customer:add_organization'))
        else:
            messages.info(request, '已成功新增機構')
            log_addition(request.user, 'customer', 'organization', organization.id, '1', object_to_dict(organization), {})
            return redirect(reverse('customer:add_customer'))
    return render(request, 'customer/add_organization.html', locals())

@login_required
@permission_required('customer.change_organization', raise_exception=True)
@csrf_protect
def change_organization(request, id):
    organization = Organization.objects.get(id=id)
    if request.method == 'POST':
        # (name, department)必為unique
        # 確認更改後，是否會有重複機構
        exist_organization = Organization.objects.filter(name=request.POST['name'], department=request.POST['department'])
        if exist_organization and exist_organization[0].id != id:
            messages.error(request, '此機構已存在')
            return redirect(reverse('customer:view_organization'))
        pre_dict = object_to_dict(organization)
        organization.name = request.POST['name']
        organization.department = request.POST['department']
        organization.is_other = request.POST['is_other']
        organization.save()
        log_addition(request.user, 'customer', 'organization', organization.id, '2', object_to_dict(organization), pre_dict)
        return redirect(reverse('customer:view_organization'))
    return render(request, 'customer/change_organization.html', locals())

@login_required
@permission_required('customer.view_organization', raise_exception=True)
def view_organization(request):
    organizations = Organization.objects.all()
    return render(request, 'customer/view_organization.html', locals())

@login_required
@permission_required('customer.add_customer', raise_exception=True)
@csrf_protect
def add_customer(request):
    organizations = Organization.objects.all()
    titles = Title.objects.all()
    jobs = Job.objects.all()
    customer_types = Customer_Type.objects.all()
    if request.method == 'POST':
        # (last_name, first_name, mobile, tel)必為unique
        for exist_customer in Customer.objects.filter(last_name=request.POST['last_name'], first_name=request.POST['first_name']):
            if {exist_customer.mobile, exist_customer.tel}.intersection({request.POST['mobile'], request.POST['tel']}) - {None, ''}:
                messages.error(request, '此客戶已存在')
                return HttpResponseRedirect('/customer/add_customer')
        # 客戶資料
        customer = Customer()
        customer.__dict__.update(**request.POST.dict())
        if request.POST['birth_date']:
            customer.birth_date = request.POST['birth_date']
        else:
            customer.birth_date = None
        job = Job.objects.get(id=request.POST['job'])
        customer.job = job
        title = Title.objects.get(id=request.POST['title'])
        customer.title = title
        customer.customer_type = Customer_Type.objects.get(id=request.POST['customer_type'])
        customer.save()
        log_addition(request.user, 'customer', 'customer', customer.id, '1', object_to_dict(customer), {})
        if request.POST.getlist('organization'):
            for organization_id in request.POST.getlist('organization'):
                organization = Organization.objects.get(id=organization_id)
                customer_organization = Customer_Organization()
                customer_organization.customer = customer
                customer_organization.organization = organization
                customer_organization.save()
                log_addition(request.user, 'customer', 'customer_organization', customer_organization.id, '1', object_to_dict(customer_organization), {})
        messages.info(request, '已成功新增客戶')
    return render(request, 'customer/add_customer.html', locals())

@login_required
@permission_required('customer.add_customer', raise_exception=True)
@csrf_protect
def add_customers(request):
    add_data = AddMultiData(field_number=12)
    if request.method == 'POST':
        column_codes, column_dict, data = add_data.read_upload(file_contents=request.FILES['sheet'].read())
        is_failed = False
        customers = list()
        customer_organizations = dict()
        for idx, customer_data in enumerate(data):
            # 之後改寫
            # 若機構、職業、職稱不存在，則是否要直接創立，還是要只接受已有的機構?
            # 目前都給自動新增，但是會是在is_other會是true
            customer = Customer()
            customer.__dict__.update(**customer_data)
            if customer_data['birth_date']:
                customer.birth_date = customer_data['birth_date']
            else:
                customer.birth_date = None
            try:
                Job(name=customer_data['job']).full_clean()
                job, created = Job.objects.get_or_create(name=customer_data['job'])
                if created:
                    log_addition(request.user, 'customer', 'job', job.id, '1', object_to_dict(job), {})
                customer.job = job
            except ValidationError as err:
                data[idx]['status'] = 'Failed'
                data[idx]['messages'].extend(['%s: %s' % (key, ';'.join(err.message_dict[key])) for key in err.message_dict])
            try:
                Title(name=customer_data['title']).full_clean()
                title, created = Title.objects.get_or_create(name=customer_data['title'])
                if created:
                    log_addition(request.user, 'customer', 'title', title.id, '1', object_to_dict(title), {})
                customer.title = title
            except ValidationError as err:
                data[idx]['status'] = 'Failed'
                data[idx]['messages'].extend(['%s: %s' % (key, ';'.join(err.message_dict[key])) for key in err.message_dict])
            # customer_type
            try:
                customer_type = Customer_Type.objects.get(name=customer_data['customer_type'])
                customer.customer_type = customer_type
            except Customer_Type.DoesNotExist:
                data[idx]['status'] = 'Failed'
                data[idx]['messages'].append('customer_type: 不存在的客戶類別')
            try:
                customer.clean()
            except ValidationError as err:
                data[idx]['status'] = 'Failed'
                data[idx]['messages'].extend(['%s: %s' % (key, ';'.join(err.message_dict[key])) for key in err.message_dict])
            customers.append(customer)
            # organization非必填
            if customer_data['organization']:
                status, mess, organization, created = ValidateOrganization(Organization, 'organization', customer_data['organization'], True)
                if created:
                    log_addition(request.user, 'customer', 'organization', organization.id, '1', object_to_dict(organization), {})
                if mess:
                    data[idx]['status'] = status
                    data[idx]['messages'].extend(mess)
                if organization:
                    customer_organization = Customer_Organization(organization=organization, customer=customer)
                    customer_organizations[len(customers)-1] = customer_organization
            if data[idx]['messages']:
                is_failed = True
        if is_failed:
            messages.info(request, '表格資料內容錯誤，請修正後重新上傳!')
        else:
            for idx, customer in enumerate(customers):
                pre_dict = {}
                for exist_customer in Customer.objects.filter(last_name=customer.last_name, first_name=customer.first_name):
                    if {exist_customer.mobile, exist_customer.tel}.intersection({customer.mobile, customer.tel}) - {None, ''}:
                        pre_dict = object_to_dict(exist_customer)
                        customer.id = exist_customer.id
                        break
                customer.save()
                if pre_dict:
                    log_addition(request.user, 'customer', 'customer', customer.id, '2', object_to_dict(customer), pre_dict)
                else:
                    log_addition(request.user, 'customer', 'customer', customer.id, '1', object_to_dict(customer), pre_dict)
                # customer_organization
                if idx in customer_organizations:
                    customer_organization, created = Customer_Organization.objects.get_or_create(customer=customer, organization=customer_organizations[idx].organization)
                    if created:
                        log_addition(request.user, 'customer', 'customer_organization', customer_organization.id, '1', object_to_dict(customer_organization), {})
                data[idx]['status'] = 'success'
            messages.info(request, '已成功新增資料')
        action_url = reverse('customer:view_customer')
        back_url = reverse('customer:add_customers')
        return render(request, 'add_data_status.html', locals())
    return add_data.view_upload(request, header='新增多筆客戶', sheet_template='add_customers_template.xlsx', action_url=reverse('customer:add_customers'))

@login_required
@permission_required('customer.change_customer', raise_exception=True)
@csrf_protect
def change_customer(request, id):
    organizations = Organization.objects.all()
    titles = Title.objects.all()
    jobs = Job.objects.all()
    customer_types = Customer_Type.objects.all()
    customer = Customer.objects.get(id=id)
    has_organizations = Customer_Organization.objects.filter(customer=customer).values_list('organization__name', 'organization__department', 'organization__id')
    if has_organizations:
        customer.organization = ';'.join([organization[0] + ' ' + organization[1] for organization in has_organizations])
        organization_ids = set([int(organization[2]) for organization in has_organizations])
    else:
        customer.organization = ''
        organization_ids = set()
    if request.method == 'POST':
        # 客戶資料更新
        # (last_name, first_name, mobile, tel)必為unique
        # 確認更改後，是否會有重複客戶
        exist_customers = Customer.objects.filter(last_name=request.POST['last_name'], first_name=request.POST['first_name'])
        if exist_customers and exist_customers[0].id != id:
            if {exist_customers[0].mobile, exist_customers[0].tel}.intersection({request.POST['mobile'], request.POST['tel']}) - {None, ''}:
                messages.error(request, '此客戶已存在')
                return redirect(reverse('customer:view_customer'))
        pre_dict = object_to_dict(customer)
        customer.__dict__.update(**request.POST.dict())
        if request.POST['birth_date']:
            customer.birth_date = request.POST['birth_date']
        else:
            customer.birth_date = None
        customer.job = Job.objects.get(id=request.POST['job'])
        customer.title = Title.objects.get(id=request.POST['title'])
        customer.customer_type = Customer_Type.objects.get(id=request.POST['customer_type'])
        customer.save()
        log_addition(request.user, 'customer', 'customer', customer.id, '2', object_to_dict(customer), pre_dict)
        if request.POST.getlist('organization'):
            new_add = set(request.POST.getlist('organization')) - organization_ids
            need_remove = organization_ids - set(request.POST.getlist('organization'))
            for organization_id in need_remove:
                organization = Organization.objects.get(id=organization_id)
                customer_organization = Customer_Organization.objects.get(customer=customer, organization=organization)
                log_addition(request.user, 'customer', 'customer_organization', customer_organization.id, '3', {}, object_to_dict(customer_organization))
                customer_organization.delete()
            for organization_id in new_add:
                organization = Organization.objects.get(id=organization_id)
                customer_organization = Customer_Organization()
                customer_organization.customer = customer
                customer_organization.organization = organization
                customer_organization.save()
                log_addition(request.user, 'customer', 'customer_organization', customer_organization.id, '1', object_to_dict(customer_organization), {})
        messages.info(request, '已成功更新客戶')
        return HttpResponseRedirect('/customer/view_customer')
    return render(request, 'customer/change_customer.html', locals())

@login_required
@permission_required('customer.view_customer', raise_exception=True)
def view_customer(request):
    # get models
    customers = Customer.objects.all()
    # 之後或許能用select_related或prefetch_related改善
    for customer in customers:
        has_organizations = Customer_Organization.objects.filter(customer=customer).values_list('organization__name', 'organization__department')
        if has_organizations:
            customer.organization = ';'.join([organization[0] + '-' + organization[1] for organization in has_organizations])
        else:
            customer.organization = ''
    return render(request, 'customer/view_customer.html', locals())

@login_required
@permission_required('customer.add_title', raise_exception=True)
def add_title(request):
    if request.method == 'POST':
        # get models
        exist_title = Title.objects.filter(name=request.POST['name'])
        if exist_title:
            messages.error(request, '此職稱已存在')
            return HttpResponseRedirect('/customer/add_customer')
        title = Title()
        title.name = request.POST['name']
        title.save()
        log_addition(request.user, 'customer', 'title', title.id, '1', object_to_dict(title), {})
        messages.error(request, '已成功新增職稱')
        return redirect(reverse('customer:add_customer'))
    return render(request, 'customer/add_title.html', locals())

@login_required
@permission_required('customer.view_title', raise_exception=True)
def view_title(request):
    titles = Title.objects.all()
    return render(request, 'customer/view_title.html', locals())

@login_required
@permission_required('customer.change_title', raise_exception=True)
def change_title(request, id):
    title = Title.objects.get(id=id)
    if request.method == 'POST':
        # (name) should be unique
        exist_title = Title.objects.filter(name=request.POST['name'])
        if exist_title and exist_title[0].id != id:
            messages.error(request, '此職稱已存在')
            return redirect(reverse('customer:view_title'))
        pre_dict = object_to_dict(title)
        title.name = request.POST['name']
        title.is_other = request.POST['is_other']
        title.save()
        log_addition(request.user, 'customer', 'title', title.id, '2', object_to_dict(title), pre_dict)
        return redirect(reverse('customer:view_title'))
    return render(request, 'customer/change_title.html', locals())

@login_required
@permission_required('customer.add_job', raise_exception=True)
def add_job(request):
    if request.method == 'POST':
        # get models
        exist_job = Job.objects.filter(name=request.POST['name'])
        if exist_job:
            messages.error(request, '此職業已存在')
            return HttpResponseRedirect('/customer/add_customer')
        job = Job()
        job.name = request.POST['name']
        job.save()
        log_addition(request.user, 'customer', 'job', job.id, '1', object_to_dict(job), {})
        messages.error(request, '已成功新增職業')
        return redirect(reverse('customer:add_customer'))
    return render(request, 'customer/add_job.html', locals())

@login_required
@permission_required('customer.view_job', raise_exception=True)
def view_job(request):
    jobs = Job.objects.all()
    return render(request, 'customer/view_job.html', locals())

@login_required
@permission_required('customer.change_job', raise_exception=True)
def change_job(request, id):
    job = Job.objects.get(id=id)
    if request.method == 'POST':
        # (name) should be unique
        exist_job = Job.objects.filter(name=request.POST['name'])
        if exist_job and exist_job[0].id != id:
            messages.error(request, '此職業已存在')
            return redirect(reverse('customer:view_job'))
        pre_dict = object_to_dict(job)
        job.name = request.POST['name']
        job.is_other = request.POST['is_other']
        job.save()
        log_addition(request.user, 'customer', 'job', job.id, '2', object_to_dict(job), pre_dict)
        return redirect(reverse('customer:view_job'))
    return render(request, 'customer/change_job.html', locals())