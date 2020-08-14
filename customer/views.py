# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


# import customer.models as customer_models

# Create your views here.
# @login_required
# @permission_required('customer.add_organization', raise_exception=True)
@csrf_protect
def add_organization(request):
    if request.method == 'POST':
        Organization = apps.get_model('customer', 'Organization')
        # (name, department)必為unique
        exist_organization = Organization.objects.filter(name=request.POST['name'], department=request.POST['department'])
        if exist_organization:
            messages.error(request, '此機構已存在')
            return HttpResponseRedirect('/customer/add_organization')
        organization = Organization()
        # 機構資料
        organization.name = request.POST['name']
        organization.department = request.POST['department']
        organization.save()
        messages.info(request, '已成功新增機構')
        return redirect(reverse('customer:add_customer'))
    return render(request, 'customer/add_organization.html', locals())

# @login_required
# @permission_required('customer.change_organization', raise_exception=True)
@csrf_protect
def change_organization(request, id):
    Organization = apps.get_model('customer', 'Organization')
    organization = Organization.objects.get(id=id)
    if request.method == 'POST':
        # (name, department)必為unique
        # 確認更改後，是否會有重複機構
        exist_organization = Organization.objects.filter(name=request.POST['name'], department=request.POST['department'])
        if exist_organization and exist_organization[0].id != id:
            messages.error(request, '此機構已存在')
            return redirect(reverse('customer:view_organization'))
        organization.name = request.POST['name']
        organization.department = request.POST['department']
        organization.save()
        return redirect(reverse('customer:view_organization'))
    return render(request, 'customer/change_organization.html', locals())

# @login_required
# @permission_required('customer.view_organization', raise_exception=True)
def view_organization(request):
    Organization = apps.get_model('customer', 'Organization')
    organizations = Organization.objects.all()
    return render(request, 'customer/view_organization.html', locals())

# @login_required
# @permission_required('customer.add_customer', raise_exception=True)
@csrf_protect
def add_customer(request):
    Organization = apps.get_model('customer', 'Organization')
    organizations = Organization.objects.all()
    if request.method == 'POST':
        Customer = apps.get_model('customer', 'Customer')
        # (last_name, first_name, phone_number)必為unique
        exist_customers = Customer.objects.filter(last_name=request.POST['last_name'], first_name=request.POST['first_name'], phone_number=request.POST['phone_number'])
        if exist_customers:
            messages.error(request, '此客戶已存在')
            return HttpResponseRedirect('/customer/add_customer')
        customer = Customer()
        # 客戶資料
        customer.last_name = request.POST['last_name']
        customer.first_name = request.POST['first_name']
        if request.POST['birth_date']:
            customer.birth_date = request.POST['birth_date']
        customer.title = request.POST['title']
        customer.email = request.POST['email']
        customer.phone_number = request.POST['phone_number']
        customer.address = request.POST['address']
        customer.memo = request.POST['memo']
        customer.save()
        if request.POST.getlist('organization'):
            for organization_id in request.POST.getlist('organization'):
                organization = Organization.objects.get(id=organization_id)
                Customer_Organization = apps.get_model('customer', 'Customer_Organization')
                customer_organization = Customer_Organization()
                customer_organization.customer = customer
                customer_organization.organization = organization
                customer_organization.save()
        messages.info(request, '已成功新增客戶')
    return render(request, 'customer/add_customer.html', locals())

# @login_required
# @permission_required('customer.change_customer', raise_exception=True)
@csrf_protect
def change_customer(request, id):
    Organization = apps.get_model('customer', 'Organization')
    organizations = Organization.objects.all()
    Customer = apps.get_model('customer', 'Customer')
    Customer_Organization = apps.get_model('customer', 'Customer_Organization')
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
        # (last_name, first_name, phone_number)必為unique
        # 確認更改後，是否會有重複客戶
        exist_customers = Customer.objects.filter(last_name=request.POST['last_name'], first_name=request.POST['first_name'], phone_number=request.POST['phone_number'])
        if exist_customers and exist_customers[0].id != id:
            messages.error(request, '此客戶已存在')
            return redirect(reverse('customer:view_customer'))
        customer.last_name = request.POST['last_name']
        customer.first_name = request.POST['first_name']
        if request.POST['birth_date']:
            customer.birth_date = request.POST['birth_date']
        customer.title = request.POST['title']
        customer.email = request.POST['email']
        customer.phone_number = request.POST['phone_number']
        customer.address = request.POST['address']
        customer.memo = request.POST['memo']
        customer.save()
        if request.POST.getlist('organization'):
            new_add = set(request.POST.getlist('organization')) - organization_ids
            need_remove = organization_ids - set(request.POST.getlist('organization'))
            for organization_id in need_remove:
                organization = Organization.objects.get(id=organization_id)
                Customer_Organization.objects.filter(customer=customer, organization=organization).delete()
            for organization_id in new_add:
                organization = Organization.objects.get(id=organization_id)
                customer_organization = Customer_Organization()
                customer_organization.customer = customer
                customer_organization.organization = organization
                customer_organization.save()
        messages.info(request, '已成功更新客戶')
        return HttpResponseRedirect('/customer/view_customer')
    return render(request, 'customer/change_customer.html', locals())

# @login_required
# @permission_required('customer.view_customer', raise_exception=True)
def view_customer(request):
    # get models
    Customer = apps.get_model('customer', 'Customer')
    Customer_Organization = apps.get_model('customer', 'Customer_Organization')
    customers = Customer.objects.all()
    # 之後或許能用select_related或prefetch_related改善
    for customer in customers:
        has_organizations = Customer_Organization.objects.filter(customer=customer).values_list('organization__name', 'organization__department')
        if has_organizations:
            customer.organization = ';'.join([organization[0] + ' ' + organization[1] for organization in has_organizations])
        else:
            customer.organization = ''
    return render(request, 'customer/view_customer.html', locals())

