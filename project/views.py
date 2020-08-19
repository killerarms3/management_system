from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from contract.models import Box
# Create your views here.

# @login_required
# @permission_required('project.add_project', raise_exception=True)
@csrf_protect
def add_project(request):

    return render(request, 'project/add_project.html', locals())

# @login_required
# @permission_required('project.view_project', raise_exception=True)
@csrf_protect
def view_project(request):
    return render(request, 'project/view_project.html', locals())

# @login_required
# @permission_required('project.view_project', raise_exception=True)
@csrf_protect
def view_project_table(request, model):
    available_models = ContentType.objects.filter(app_label='project').values_list('model', flat=True)
    if model not in available_models:
        return HttpResponseRedirect('/project/view_project')
    Project_table = apps.get_model('project', model)
    table_data = list()
    # 不顯示ID
    field_names = [field.name for field in Project_table._meta.fields if field.name != 'id']
    for data in Project_table.objects.all().values():
        record = dict()
        for field_name in field_names:
            # 一定會有box
            if field_name == 'box':
                box = Box.objects.get(id=data['box_id'])
                record[field_name] = box.serial_number
            else:
                record[field_name] = data[field_name]
        table_data.append(record)
    return render(request, 'project/view_project_table.html', locals())

# @login_required
# @permission_required('project.change_project', raise_exception=True)
@csrf_protect
def change_project(request, id):
    return render(request, 'product/change_project.html', locals())
