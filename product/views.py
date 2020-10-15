from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from product.models import Product, Project, Plan
from contract.models import Box
from history.models import History
from history.function import log_addition, object_to_dict, Update_log_dict, Create_log_dict
from product.forms import PlanCreateForm, ProductCreateForm
from lib import utils

# Create your views here.
@login_required
@permission_required('product.add_product', raise_exception=True)
@csrf_protect
def add_product(request):
    form = ProductCreateForm()
    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            if Product.objects.filter(name=form.cleaned_data['name']):
                messages.error(request, '此產品已存在')
            else:
                product = form.save()
                if form.cleaned_data['project']:
                    project = Project(product=product, content_type=form.cleaned_data['project'])
                    project.save()
                    log_addition(request.user, 'product', 'project', project.id, '1', object_to_dict(project), {})
                messages.info(request, '已成功新增產品')
                log_addition(request.user, 'product', 'product', product.id, '1', object_to_dict(product), {})
        else:
            messages.error(request, '資料格式錯誤')
        return redirect(reverse('product:add_product'))
    return render(request, 'product/add_product.html', locals())

@login_required
@permission_required('product.view_product', raise_exception=True)
@csrf_protect
def view_product(request):
    products = Product.objects.all()
    for product in products:
        has_project = Project.objects.filter(product=product)
        if has_project:
            product.project = has_project[0].content_type.model
        else:
            product.project = ''
    return render(request, 'product/view_product.html', locals())

@login_required
@permission_required('product.change_product', raise_exception=True)
@csrf_protect
def change_product(request, id):
    product = Product.objects.get(id=id)
    project = Project.objects.filter(product=product).first()
    initial_dict = {'status': int(product.status == True)}
    if project:
        initial_dict['project'] = project.content_type
    form = ProductCreateForm(instance=product, initial=initial_dict)
    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            products = Product.objects.filter(name=form.cleaned_data['name'])
            if products and products[0].id != id:
                messages.error(request, '此產品已存在')
            else:
                pre_dict = object_to_dict(product)
                product.__dict__.update(**form.cleaned_data)
                product.status = request.POST['status']
                product.save()
                log_addition(request.user, 'product', 'product', product.id, '2', object_to_dict(product), pre_dict)
                if project and project.content_type != form.cleaned_data['project']:
                    if form.cleaned_data['project']:
                        pre_dict = object_to_dict(project)
                        project.content_type = form.cleaned_data['project']
                        project.save()
                        log_addition(request.user, 'product', 'project', project.id, '2', object_to_dict(project), pre_dict)
                    else:
                        log_addition(request.user, 'product', 'project', project.id, '3', {}, object_to_dict(project))
                        project.delete()
                elif form.cleaned_data['project']:
                    project = Project(product=product, content_type=form.cleaned_data['project'])
                    project.save()
                    log_addition(request.user, 'product', 'project', project.id, '1', object_to_dict(project), {})
                messages.info(request, '已成功更新產品')
        else:
            messages.error(request, '資料格式錯誤')
        return HttpResponseRedirect('/product/view_product')
    return render(request, 'product/change_product.html', locals())

@login_required
@permission_required('product.add_plan', raise_exception=True)
@csrf_protect
def add_plan(request):
    form = PlanCreateForm()
    if request.method == 'POST':
        form = PlanCreateForm(request.POST)
        if form.is_valid():
            if Plan.objects.filter(product=form.cleaned_data['product'], name=form.cleaned_data['name']):
                messages.error(request, '此方案已存在')
            else:
                plan = form.save()
                messages.info(request, '已成功新增方案')
                log_addition(request.user, 'product', 'plan', plan.id, '1', object_to_dict(plan), {})
        else:
            messages.error(request, '資料格式錯誤')
        return redirect(reverse('product:add_plan'))
    return render(request, 'product/add_plan.html', locals())

@login_required
@permission_required('product.view_plan', raise_exception=True)
@csrf_protect
def view_plan(request):
    plans = Plan.objects.all()
    return render(request, 'product/view_plan.html', locals())

@login_required
@permission_required('product.view_plan', raise_exception=True)
def view_product_plan(request, id):
    plans = Plan.objects.filter(product__id=id)
    return render(request, 'product/view_plan.html', locals())

@login_required
@permission_required('product.change_plan', raise_exception=True)
@csrf_protect
def change_plan(request, id):
    plan = Plan.objects.get(id=id)
    form = PlanCreateForm(instance=plan, initial={'status': int(plan.status == True)})
    if request.method == 'POST':
        form = PlanCreateForm(request.POST)
        if form.is_valid():
            plans = Plan.objects.filter(product=form.cleaned_data['product'], name=form.cleaned_data['name'])
            if plans and plans[0].id != id:
                messages.error(request, '此方案已存在')
            else:
                pre_dict = object_to_dict(plan)
                plan.__dict__.update(**form.cleaned_data)
                plan.product = form.cleaned_data['product']
                plan.status = request.POST['status']
                plan.save()
                messages.info(request, '已成功更新方案')
                log_addition(request.user, 'product', 'plan', plan.id, '2', object_to_dict(plan), pre_dict)
        return HttpResponseRedirect('/product/view_plan')
    return render(request, 'product/change_plan.html', locals())

@login_required
@permission_required('product.view_plan', raise_exception=True)
def view_specific_plan(request, id):
    plan = Plan.objects.get(id=id)
    field_names = [field.name for field in Plan._meta.fields if field.name != 'id']
    field_tags = utils.getlabels('product', 'plan')
    boxes = Box.objects.filter(plan=plan)
    return render(request, 'product/view_specific_plan.html', locals())
