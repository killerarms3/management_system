from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from contract.models import Box
from language.models import Code
from project.forms import GetDataCreateForm, ProjectBox
from history.models import History
from history.function import log_addition, object_to_dict, Update_log_dict, Create_log_dict
# Create your views here.

@login_required
@permission_required('project.view_project', raise_exception=True)
@csrf_protect
def view_project(request):
    return HttpResponseRedirect('/product/view_product')

def getlabels(AppName, ModelName):
    field_tags = dict()
    Model = apps.get_model(AppName, ModelName)
    field_names = [field.name for field in Model._meta.fields]
    contenttype = ContentType.objects.get(app_label=AppName, model=ModelName)
    for field_name in field_names:
        field_tags[field_name] = field_name
        codes = Code.objects.filter(content_type=contenttype, code=field_name)
        if codes:
            field_tags[field_name] = codes[0].name
    return field_tags

@login_required
@csrf_protect
def view_project_table(request, model):
    available_models = ContentType.objects.filter(app_label='project').values_list('model', flat=True)
    if model not in available_models:
        return HttpResponseRedirect('/project/view_project')
    if not request.user.has_perm('project.view_' + model):
        return HttpResponseRedirect('/project/view_project')
    Project_table = apps.get_model('project', model)
    table_data = list()
    # 不顯示ID
    field_names = [field.name for field in Project_table._meta.fields if field.name != 'id']
    # 取得欄位名
    contenttype = ContentType.objects.get(app_label='project', model=model)
    codes = Code.objects.filter(content_type=contenttype)
    field_tags = getlabels('project', model)
    for data in Project_table.objects.all().values():
        record = {'id': data['id']}
        for field_name in field_names:
            # 一定會有box
            if field_name == 'box':
                box = Box.objects.get(id=data['box_id'])
                record[field_name] = box.serial_number
            else:
                record[field_name] = data[field_name]
        table_data.append(record)
    return render(request, 'project/view_project_table.html', locals())

@login_required
@csrf_protect
def add_data(request, model):
    # check if model is available
    try:
        contenttype = ContentType.objects.get(app_label='project', model=model)
    except ContentType.DoesNotExist:
        return HttpResponseRedirect('/project/view_project')
    if not request.user.has_perm('project.add_' + model):
        return HttpResponseRedirect('/project/view_project')
    ProjectModel = apps.get_model('project', model)
    field_tags = getlabels('project', model)
    FormClass = GetDataCreateForm(ProjectModel, field_tags)
    form = FormClass(instance=ProjectModel())
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            exist_data = ProjectModel.objects.filter(box=form.cleaned_data['box'])
            if exist_data:
                messages.error(request, '資料已存在')
                return redirect(reverse('project:add_data', kwargs={'model': model}))
            else:
                data = ProjectModel()
                data.__dict__.update(**form.cleaned_data)
                data.box = form.cleaned_data['box']
                data.save()
                log_addition(request.user, 'project', model, data.id, '1', object_to_dict(data), {})
                messages.info(request, '已成功新增資料')
                return redirect(reverse('project:add_data', kwargs={'model': model}))
        else:
            messages.error(request, '新增失敗，表格含無法辨認的資料')
            return redirect(reverse('project:add_data', kwargs={'model': model}))
    return render(request, 'project/add_data.html', locals())

@login_required
@csrf_protect
def change_data(request, model, id):
    try:
        contenttype = ContentType.objects.get(app_label='project', model=model)
    except ContentType.DoesNotExist:
        return HttpResponseRedirect('/project/view_project')
    if not request.user.has_perm('project.add_' + model):
        return HttpResponseRedirect('/project/view_project')
    ProjectModel = apps.get_model('project', model)
    field_tags = getlabels('project', model)
    FormClass = GetDataCreateForm(ProjectModel, field_tags)
    data = ProjectModel.objects.get(id=id)
    form = FormClass(instance=data)
    form.fields['box'].widget.attrs['disabled'] = True
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            pre_dict = object_to_dict(data)
            data.__dict__.update(**form.cleaned_data)
            data.box = form.cleaned_data['box']
            data.save()
            log_addition(request.user, 'project', model, data.id, '2', object_to_dict(data), pre_dict)
            messages.info(request, '已成功更新資料')
        else:
            messages.error(request, '更新失敗，表格含無法辨認的資料')
        return redirect(reverse('project:view_project_table', kwargs={'model': model}))
    return render(request, 'project/change_data.html', locals())

def view_specific_data(request, model, serial_number):
    try:
        contenttype = ContentType.objects.get(app_label='project', model=model)
    except ContentType.DoesNotExist:
        return HttpResponseRedirect('/project/view_project')
    if not request.user.has_perm('project.view_' + model):
        return HttpResponseRedirect('/project/view_project')
    Project_table = apps.get_model('project', model)
    available_boxes = ProjectBox(model).values_list('serial_number', flat=True)
    if serial_number not in available_boxes:
        return redirect(reverse('project:view_project_table', kwargs={'model': model}))
    # 不顯示ID
    field_names = [field.name for field in Project_table._meta.fields if field.name != 'id']
    codes = Code.objects.filter(content_type=contenttype)
    field_tags = getlabels('project', model)
    data_list = Project_table.objects.filter(box__serial_number=serial_number)
    if not data_list:
        FormClass = GetDataCreateForm(Project_table, field_tags)
        form = FormClass(instance=Project_table(), initial={'box': Box.objects.get(serial_number=serial_number)})
        return render(request, 'project/add_data.html', locals())
    else:
        data = data_list[0]
    return render(request, 'project/view_specific_data.html', locals())