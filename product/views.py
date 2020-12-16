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
    form = ProductCreateForm(auto_id='%s')
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, auto_id='%s')
        if form.is_valid():
            product = form.save()
            log_addition(request.user, 'product', 'product', product.id, '1', object_to_dict(product), {})
            if form.cleaned_data['project']:
                project = Project(product=product, content_type=form.cleaned_data['project'])
                project.save()
                log_addition(request.user, 'product', 'project', project.id, '1', object_to_dict(project), {})
            messages.info(request, '已成功新增產品')
            return redirect(reverse('product:add_product'))
        else:
            field_tags = utils.getlabels('product', 'product')
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (field_tags[key], error))
                    except KeyError:
                        messages.error(request, '此產品已存在')
    return render(request, 'product/add_product.html', locals())

@login_required
@permission_required('product.view_product', raise_exception=True)
@csrf_protect
def view_product(request):
    products = Product.objects.all().order_by('-pk')
    return render(request, 'product/view_product.html', locals())

@login_required
@permission_required('product.change_product', raise_exception=True)
@csrf_protect
def change_product(request, pk):
    product = Product.objects.get(id=pk)
    initial_dict = {'status': int(product.status == True)}
    project = Project.objects.filter(product=product).first()
    if project:
        initial_dict['project'] = project.content_type
    form = ProductCreateForm(instance=product, initial=initial_dict, auto_id='%s')
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, instance=product, auto_id='%s')
        if form.is_valid():
            pre_dict = object_to_dict(product)
            product = form.save(commit=False)
            product.id = pk
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
            elif not project and form.cleaned_data['project']:
                project = Project(product=product, content_type=form.cleaned_data['project'])
                project.save()
                log_addition(request.user, 'product', 'project', project.id, '1', object_to_dict(project), {})
            messages.info(request, '已成功更新產品')
            return redirect(reverse('product:view_product'))
        else:
            field_tags = utils.getlabels('product', 'product')
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (field_tags[key], error))
                    except KeyError:
                        messages.error(request, '此產品已存在')
    return render(request, 'product/change_product.html', locals())

@login_required
@permission_required('product.add_plan', raise_exception=True)
@csrf_protect
def add_plan(request):
    form = PlanCreateForm(auto_id='%s')
    if request.method == 'POST':
        form = PlanCreateForm(request.POST)
        if form.is_valid():
            plan = form.save()
            log_addition(request.user, 'product', 'plan', plan.id, '1', object_to_dict(plan), {})
            messages.info(request, '已成功新增方案')
            return redirect(reverse('product:add_plan'))
        else:
            field_tags = utils.getlabels('product', 'plan')
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (field_tags[key], error))
                    except KeyError:
                        messages.error(request, '此方案已存在')
    return render(request, 'product/add_plan.html', locals())

@login_required
@permission_required('product.view_plan', raise_exception=True)
@csrf_protect
def view_plan(request):
    plans = Plan.objects.all().order_by('-pk')
    return render(request, 'product/view_plan.html', locals())

@login_required
@permission_required('product.view_plan', raise_exception=True)
def view_product_plan(request, pk):
    plans = Plan.objects.filter(product__id=pk)
    return render(request, 'product/view_plan.html', locals())

@login_required
@permission_required('product.change_plan', raise_exception=True)
@csrf_protect
def change_plan(request, pk):
    plan = Plan.objects.get(id=pk)
    form = PlanCreateForm(instance=plan, auto_id='%s', initial={'status': int(plan.status == True)})
    if request.method == 'POST':
        form = PlanCreateForm(request.POST, instance=plan, auto_id='%s')
        if form.is_valid():
            pre_dict = object_to_dict(plan)
            plan = form.save(commit=False)
            plan.id = pk
            plan.save()
            log_addition(request.user, 'product', 'plan', plan.id, '2', object_to_dict(plan), pre_dict)
            messages.info(request, '已成功更新方案')
            return redirect(reverse('product:view_plan'))
        else:
            field_tags = utils.getlabels('product', 'plan')
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (field_tags[key], error))
                    except KeyError:
                        messages.error(request, '此方案已存在')
    form.fields['product'].widget.attrs['disabled'] = True
    return render(request, 'product/change_plan.html', locals())

@login_required
@permission_required('product.view_plan', raise_exception=True)
def view_specific_plan(request, pk):
    plan = Plan.objects.get(id=pk)
    field_names = [field.name for field in Plan._meta.fields if field.name != 'id']
    field_tags = utils.getlabels('product', 'plan')
    boxes = Box.objects.filter(plan=plan).order_by('-pk')
    return render(request, 'product/view_specific_plan.html', locals())
