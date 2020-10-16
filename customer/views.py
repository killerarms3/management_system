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
from customer.models import Organization, Customer, Customer_Organization, Title, Job, Customer_Type, Customer_Introducer, Relationship
from django.template.defaulttags import register
from history.models import History
from history.function import log_addition, object_to_dict, Update_log_dict, Create_log_dict
from customer.forms import CustomerCreateForm
from lib import utils
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
        else:
            messages.info(request, '已成功新增機構')
            log_addition(request.user, 'customer', 'organization', organization.id, '1', object_to_dict(organization), {})
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
    organizations = Organization.objects.all().order_by('-pk')
    return render(request, 'customer/view_organization.html', locals())

@login_required
@permission_required('customer.add_customer', raise_exception=True)
@csrf_protect
def add_customer(request):
    field_tags = utils.getlabels('customer', 'customer')
    form = CustomerCreateForm(auto_id='%s')
    if request.method == 'POST':
        # (last_name, first_name, mobile, tel)必為unique
        form = CustomerCreateForm(request.POST, auto_id='%s')
        if form.is_valid():
            is_exist = False
            for exist_customer in Customer.objects.filter(last_name=form.cleaned_data['last_name'], first_name=form.cleaned_data['first_name']):
                if {exist_customer.mobile, exist_customer.tel}.intersection({form.cleaned_data['mobile'], form.cleaned_data['tel']}) - {None, ''}:
                    messages.error(request, '此客戶已存在')
                    is_exist = True
                    break
            if not is_exist:
                customer = form.save()
                log_addition(request.user, 'customer', 'customer', customer.id, '1', object_to_dict(customer), {})
                if form.cleaned_data['organization']:
                    for organization in form.cleaned_data['organization']:
                        customer_organization = Customer_Organization(customer=customer, organization=organization)
                        customer_organization.save()
                        log_addition(request.user, 'customer', 'customer_organization', customer_organization.id, '1', object_to_dict(customer_organization), {})
                if form.cleaned_data['introducer']:
                    customer_introducer = Customer_Introducer(customer=customer, introducer=form.cleaned_data['introducer'], relationship=form.cleaned_data['relationship'])
                    customer_introducer.save()
                    log_addition(request.user, 'customer', 'customer_introducer', customer_introducer.id, '1', object_to_dict(customer_introducer), {})
                messages.info(request, '已成功新增客戶')
                return redirect(reverse('customer:add_customer'))
        else:
            messages.error(request, '資料格式錯誤')
            if 'mobile' in form.errors:
                messages.error(request, '%s: %s' % (field_tags['mobile'], form.errors['mobile'][0]))
            if 'tel' in form.errors:
                messages.error(request, '%s: %s' % (field_tags['tel'], form.errors['tel'][0]))
    return render(request, 'customer/add_customer.html', locals())

@login_required
@permission_required('customer.add_customer', raise_exception=True)
@csrf_protect
def add_customers(request):
    add_data = AddMultiData(field_number=14)
    if request.method == 'POST':
        column_codes, column_dict, data = add_data.read_upload(file_contents=request.FILES['sheet'].read())
        is_failed = False
        customers = list()
        customer_organizations = dict()
        customer_introducers = dict()
        for idx, customer_data in enumerate(data):
            # 之後改寫
            # 若機構、職業、職稱不存在，則是否要直接創立，還是要只接受已有的機構?
            # 改不直接創立，避免出現一堆簡稱
            customer = Customer()
            customer.__dict__.update(**customer_data)
            try:
                job = Job.objects.get(name=customer_data['job'])
                customer.job = job
            except Job.DoesNotExist:
                data[idx]['messages'].append('job: 不存在的職業')
            try:
                title = Title.objects.get(name=customer_data['title'])
                customer.title = title
            except Title.DoesNotExist:
                data[idx]['messages'].append('title: 不存在的職稱')
            try:
                customer_type = Customer_Type.objects.get(name=customer_data['customer_type'])
                customer.customer_type = customer_type
            except Customer_Type.DoesNotExist:
                data[idx]['messages'].append('customer_type: 不存在的客戶類別')
            try:
                customer.clean()
            except ValidationError as err:
                data[idx]['messages'].extend(['%s: %s' % (key, ';'.join(err.message_dict[key])) for key in err.message_dict])
            customers.append(customer)
            # organization非必填
            if customer_data['organization']:
                status, mess, organization = ValidateOrganization(Organization, 'organization', customer_data['organization'])
                if mess:
                    data[idx]['messages'].extend(mess)
                if organization:
                    customer_organizations[len(customers)-1] = Customer_Organization(organization=organization)
            # introducter非必填
            if (customer_data['introducer'] and not customer_data['relationship']) or (not customer_data['introducer'] and customer_data['relationship']):
                data[idx]['messages'].extend(['introducer: 推薦人與關係必須兩個都填或都不填', 'relationship: 推薦人與關係必須兩個都填或都不填'])
            if customer_data['introducer'] and customer_data['relationship']:
                try:
                    relationship = Relationship.objects.get(name=customer_data['relationship'])
                    introducers = [customer for customer in Customer.objects.all() if str(customer) == customer_data['introducer']]
                    if not introducers:
                        data[idx]['messages'].append('introducer: 不存在的推薦人')
                    elif len(introducers) > 1:
                        data[idx]['messages'].append('introducer: 有多個同名客戶，請使用【新增客戶】新增此客戶')
                    else:
                        customer_introducers[len(customers)-1] = Customer_Introducer(introducer=introducers[0], relationship=relationship)
                except Relationship.DoesNotExist:
                    data[idx]['messages'].append('relationship: 不存在的關係')

            if data[idx]['messages']:
                data[idx]['status'] = 'Failed'
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
                if idx in customer_introducers:
                    # 只新增、更新、不刪除
                    # 如果表格留空，暫時不刪除原本的關聯
                    customer_introducer = Customer_Introducer.objects.filter(customer=customer).first()
                    if not customer_introducer:
                        action_flag = '1'
                        pre_dict = dict()
                        customer_introducer = Customer_Introducer(customer=customer)
                    else:
                        action_flag = '2'
                        pre_dict = object_to_dict(customer_introducer)
                    customer_introducer.introducer = customer_introducers[idx].introducer
                    customer_introducer.relationship = customer_introducers[idx].relationship
                    customer_introducer.save()
                    log_addition(request.user, 'customer', 'customer_introducer', customer_introducer.id, action_flag, object_to_dict(customer_introducer), pre_dict)
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
    field_tags = utils.getlabels('customer', 'customer')
    customer = Customer.objects.get(id=id)
    organizations = Organization.objects.filter(id__in=Customer_Organization.objects.filter(customer=customer).values_list('organization', flat=True).distinct())
    customer_introducer = Customer_Introducer.objects.filter(customer=customer).first()
    initial_dict = dict()
    if organizations:
        initial_dict['organization'] = organizations
    if customer_introducer:
        initial_dict['introducer'] = customer_introducer.introducer
        initial_dict['relationship'] = customer_introducer.relationship
    form = CustomerCreateForm(instance=customer, initial=initial_dict, auto_id='%s')
    if request.method == 'POST':
        form = CustomerCreateForm(request.POST, auto_id='%s')
        if form.is_valid():
            # 客戶資料更新
            # (last_name, first_name, mobile, tel)必為unique
            # 確認更改後，是否會有重複客戶
            is_exist = False
            for exist_customer in Customer.objects.filter(last_name=form.cleaned_data['last_name'], first_name=form.cleaned_data['first_name']):
                if exist_customer.id != id and {exist_customer.mobile, exist_customer.tel}.intersection({form.cleaned_data['mobile'], form.cleaned_data['tel']}) - {None, ''}:
                    messages.error(request, '此客戶已存在')
                    is_exist = True
                    break
            if not is_exist:
                pre_dict = object_to_dict(customer)
                customer.__dict__.update(**form.cleaned_data)
                customer.save()
                log_addition(request.user, 'customer', 'customer', customer.id, '2', object_to_dict(customer), pre_dict)
                new_add = set(form.cleaned_data['organization']) - set(organizations)
                need_remove = set(organizations) - set(form.cleaned_data['organization'])
                for organization in need_remove:
                    customer_organization = Customer_Organization.objects.get(customer=customer, organization=organization)
                    log_addition(request.user, 'customer', 'customer_organization', customer_organization.id, '3', {}, object_to_dict(customer_organization))
                    customer_organization.delete()
                for organization in new_add:
                    customer_organization = Customer_Organization(customer=customer, organization=organization)
                    customer_organization.save()
                    log_addition(request.user, 'customer', 'customer_organization', customer_organization.id, '1', object_to_dict(customer_organization), {})
                if form.cleaned_data['introducer']:
                    if not customer_introducer:
                        action_flag = '1'
                        pre_dict = dict()
                        customer_introducer = Customer_Introducer(customer=customer)
                    else:
                        action_flag = '2'
                        pre_dict = object_to_dict(customer_introducer)
                    customer_introducer.introducer = form.cleaned_data['introducer']
                    customer_introducer.relationship = form.cleaned_data['relationship']
                    customer_introducer.save()
                    log_addition(request.user, 'customer', 'customer_introducer', customer_introducer.id, action_flag, object_to_dict(customer_introducer), pre_dict)
                elif customer_introducer:
                    log_addition(request.user, 'customer', 'customer_introducer', customer_introducer.id, '3', {}, object_to_dict(customer_introducer))
                    customer_introducer.delete()

            messages.info(request, '已成功更新客戶')
            return redirect(reverse('customer:view_customer'))
        else:
            messages.error(request, '資料格式錯誤')
            if 'mobile' in form.errors:
                messages.error(request, '%s: %s' % (field_tags['mobile'], form.errors['mobile'][0]))
            if 'tel' in form.errors:
                messages.error(request, '%s: %s' % (field_tags['tel'], form.errors['tel'][0]))
    return render(request, 'customer/change_customer.html', locals())

@login_required
@permission_required('customer.view_customer', raise_exception=True)
def view_customer(request):
    # get models
    customers = Customer.objects.all().order_by('-pk')
    # 之後或許能用select_related或prefetch_related改善
    for customer in customers:
        organizations = Organization.objects.filter(id__in=Customer_Organization.objects.filter(customer=customer).values_list('organization', flat=True).distinct())
        customer_introducer = Customer_Introducer.objects.filter(customer=customer).first()
        if organizations:
            customer.organization = ';'.join([str(organization) for organization in organizations])
        else:
            customer.organization = ''
        if customer_introducer:
            customer.customer_introducer = customer_introducer
        else:
            customer.customer_introducer = ''
    return render(request, 'customer/view_customer.html', locals())

@login_required
@permission_required('customer.add_title', raise_exception=True)
def add_title(request):
    if request.method == 'POST':
        title, created = Title.objects.get_or_create(name=request.POST['name'])
        if not created:
            messages.error(request, '此職稱已存在')
        else:
            messages.info(request, '已成功新增職稱')
            log_addition(request.user, 'customer', 'title', title.id, '1', object_to_dict(title), {})
    return render(request, 'customer/add_title.html', locals())

@login_required
@permission_required('customer.view_title', raise_exception=True)
def view_title(request):
    titles = Title.objects.all().order_by('-pk')
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
        job, created = Job.objects.get_or_create(name=request.POST['name'])
        if not created:
            messages.error(request, '此職業已存在')
        else:
            messages.info(request, '已成功新增職業')
            log_addition(request.user, 'customer', 'job', job.id, '1', object_to_dict(job), {})
    return render(request, 'customer/add_job.html', locals())

@login_required
@permission_required('customer.view_job', raise_exception=True)
def view_job(request):
    jobs = Job.objects.all().order_by('-pk')
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

@login_required
def update_options(reuqest, model):
    try:
        Model = apps.get_model('customer', model)
        objects = [[obj.id, str(obj)] for obj in Model.objects.all()]
    except LookupError:
        objects = []
    return JsonResponse({'objects': objects})