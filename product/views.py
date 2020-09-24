from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from product.models import Product, Prefix, Product_Prefix, Project, Plan

# Create your views here.
# @login_required
# @permission_required('product.add_product', raise_exception=True)
@csrf_protect
def add_product(request):
    project_contents = ContentType.objects.filter(app_label='project')
    if request.method == 'POST':
        # (name)必為unique
        exist_product = Product.objects.filter(name=request.POST['name'])
        if exist_product:
            messages.error(request, '此產品名稱已存在')
            return HttpResponseRedirect('/product/add_product')
        product = Product()
        # 產品
        product.name = request.POST['name']
        product.save()
        # 產品前綴
        if request.POST['prefix']:
            exist_prefix = Prefix.objects.filter(name=request.POST['prefix'])
            if exist_prefix:
                prefix = exist_prefix[0]
            else:
                prefix = Prefix()
                prefix.name = request.POST['prefix']
                prefix.save()
            product_prefix = Product_Prefix()
            product_prefix.product = product
            product_prefix.prefix = prefix
            product_prefix.save()
        if request.POST['project_content']:
            content_type = ContentType.objects.get(id=request.POST['project_content'])
            project = Project()
            project.product = product
            project.content_type = content_type
            project.save()
        messages.info(request, '已成功新增產品')
        return redirect(reverse('product:add_product'))
    return render(request, 'product/add_product.html', locals())

# @login_required
# @permission_required('product.view_product', raise_exception=True)
@csrf_protect
def view_product(request):
    products = Product.objects.all()
    for product in products:
        has_prefix = Product_Prefix.objects.filter(product=product)
        if has_prefix:
            product.prefix = has_prefix[0].prefix.name
        else:
            product.prefix = ''
        has_project = Project.objects.filter(product=product)
        if has_project:
            product.project = has_project[0].content_type.model
        else:
            product.project = ''
    return render(request, 'product/view_product.html', locals())

# @login_required
# @permission_required('product.change_product', raise_exception=True)
@csrf_protect
def change_product(request, id):
    project_contents = ContentType.objects.filter(app_label='project')
    product = Product.objects.get(id=id)
    has_prefix = Product_Prefix.objects.filter(product=product)
    if has_prefix:
        product.prefix = has_prefix[0].prefix.name
    else:
        product.prefix = ''
    has_project = Project.objects.filter(product=product)
    if has_project:
        content_id = has_project[0].content_type.id
    else:
        content_id = ''
    if request.method == 'POST':
        # 產品資料更新
        # (name)必為unique
        exist_products = Product.objects.filter(name=request.POST['name'])
        if exist_products and exist_products[0].id != id:
            messages.error(request, '此產品已存在')
            return redirect(reverse('product:view_product'))
        product.name = request.POST['name']
        product.status = request.POST['status']
        product.save()
        if product.prefix != request.POST['prefix']:
            if request.POST['prefix']:
                exist_prefix = Prefix.objects.filter(name=request.POST['prefix'])
                if exist_prefix:
                    prefix = exist_prefix[0]
                else:
                    prefix = Prefix()
                    prefix.name = request.POST['prefix']
                    prefix.save()
                if has_prefix:
                    product_prefix = has_prefix[0]
                    product_prefix.prefix = prefix
                else:
                    product_prefix = Product_Prefix()
                    product_prefix.product = product
                    product_prefix.prefix = prefix
                product_prefix.save()
            else:
                has_prefix[0].delete()
        if content_id != request.POST['project_content']:
            if request.POST['project_content']:
                content_type = ContentType.objects.get(id=request.POST['project_content'])
                if has_project:
                    project = has_project[0]
                    project.content_type = content_type
                else:
                    project = Project()
                    project.product = product
                    project.content_type = content_type
                project.save()
            else:
                has_project[0].delete()
        messages.info(request, '已成功更新產品')
        return HttpResponseRedirect('/product/view_product')
    return render(request, 'product/change_product.html', locals())

# @login_required
# @permission_required('product.add_plan', raise_exception=True)
@csrf_protect
def add_plan(request):
    products = Product.objects.all()
    if request.method == 'POST':
        # (product.id, name)必為unique
        product = Product.objects.get(id=request.POST['product'])
        exist_plan = Plan.objects.filter(product=product, name=request.POST['name'])
        if exist_plan:
            messages.error(request, '此方案已存在')
            return HttpResponseRedirect('/product/add_plan')
        plan = Plan()
        product = Product.objects.get(id=request.POST['product'])
        plan.product = product
        plan.name = request.POST['name']
        plan.price = request.POST['price']
        plan.description = request.POST['description']
        plan.save()
        messages.info(request, '已成功新增方案')
        return redirect(reverse('product:add_plan'))
    return render(request, 'product/add_plan.html', locals())

# @login_required
# @permission_required('product.view_plan', raise_exception=True)
@csrf_protect
def view_plan(request):
    plans = Plan.objects.all()
    return render(request, 'product/view_plan.html', locals())

# @login_required
# @permission_required('product.change_plan', raise_exception=True)
@csrf_protect
def change_plan(request, id):
    products = Product.objects.all()
    plan = Plan.objects.get(id=id)
    if request.method == 'POST':
        # (product.id, name)必為unique
        product = Product.objects.get(id=request.POST['product'])
        exist_plan = Plan.objects.filter(product=product, name=request.POST['name'])
        if exist_plan and exist_plan[0].id != id:
            messages.error(request, '此方案已存在')
            return redirect(reverse('product:view_plan'))
        plan.product = product
        plan.name = request.POST['name']
        plan.price = request.POST['price']
        plan.description = request.POST['description']
        plan.status = request.POST['status']
        plan.save()
        messages.info(request, '已成功更新方案')
        return HttpResponseRedirect('/product/view_plan')
    return render(request, 'product/change_plan.html', locals())
