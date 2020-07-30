from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

# Create your views here.
# @login_required
# @permission_required('product.add_product', raise_exception=True)
@csrf_protect
def add_product(request):
    project = ContentType.objects.filter(app_label='project').values_list('organization__name')
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
    return render(request, 'product/add_product.html', locals())

# @login_required
# @permission_required('product.view_product', raise_exception=True)
@csrf_protect
def view_product(request):
    return render(request, 'product/view_product.html', locals())

# @login_required
# @permission_required('product.change_product', raise_exception=True)
@csrf_protect
def change_product(request):
    return render(request, 'product/change_product.html', locals())

# @login_required
# @permission_required('product.add_plan', raise_exception=True)
@csrf_protect
def add_plan(request):
    return render(request, 'product/add_plan.html', locals())

# @login_required
# @permission_required('product.view_product', raise_exception=True)
@csrf_protect
def view_plan(request):
    return render(request, 'product/view_product.html', locals())

# @login_required
# @permission_required('product.change_product', raise_exception=True)
@csrf_protect
def change_plan(request):
    return render(request, 'product/change_product.html', locals())