from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from contract.models import Box
from language.models import Code
from project.forms import GetDataCreateForm, ProjectBox
from history.models import History
from history.function import log_addition, object_to_dict, Update_log_dict, Create_log_dict
import json
from lib import utils
from django.core.exceptions import ValidationError
from decimal import Decimal
# Create your views here.

@login_required
@permission_required('project.view_project', raise_exception=True)
@csrf_protect
def view_project(request):
    return HttpResponseRedirect('/product/view_product')

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
    field_tags = utils.getlabels('project', model)
    for data in Project_table.objects.all().order_by('-pk').values():
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
    FormClass = GetDataCreateForm(ProjectModel)
    form = FormClass(instance=ProjectModel())
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            exist_data = ProjectModel.objects.filter(box=form.cleaned_data['box'])
            if exist_data:
                messages.error(request, '資料已存在')
            else:
                data = ProjectModel()
                data.__dict__.update(**form.cleaned_data)
                data.box = form.cleaned_data['box']
                data.save()
                log_addition(request.user, 'project', model, data.id, '1', object_to_dict(data), {})
                messages.info(request, '已成功新增資料')
                return redirect(reverse('project:add_data', kwargs={'model': model}))
        else:
            for key in form.errors:
                for error in form.errors[key]:
                    messages.error(request, '%s: %s' % (key, error))
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
    FormClass = GetDataCreateForm(ProjectModel)
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
            return redirect(reverse('project:view_project_table', kwargs={'model': model}))
        else:
            for key in form.errors:
                for error in form.errors[key]:
                    messages.error(request, '%s: %s' % (key, error))
    return render(request, 'project/change_data.html', locals())

@login_required
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
    data_list = Project_table.objects.filter(box__serial_number=serial_number)
    if not data_list:
        FormClass = GetDataCreateForm(Project_table)
        form = FormClass(instance=Project_table(), initial={'box': Box.objects.get(serial_number=serial_number)})
        return render(request, 'project/add_data.html', locals())
    else:
        data = data_list[0]
    return render(request, 'project/view_specific_data.html', locals())


@login_required
def add_multiple(request, model):
    # check if model is available
    try:
        contenttype = ContentType.objects.get(app_label='project', model=model)
    except ContentType.DoesNotExist:
        return HttpResponseRedirect('/project/view_project')
    if not request.user.has_perm('project.add_' + model):
        return HttpResponseRedirect('/project/view_project')
    ProjectModel = apps.get_model('project', model)
    FormClass = GetDataCreateForm(ProjectModel)
    form = FormClass(instance=ProjectModel())
    field_names, colHeaders, columns = utils.GetHandsontableColumns(form)
    # first row is box
    columns[0]['source'] = list(ProjectBox(model, exclude_exist=False).values_list('serial_number', flat=True))
    if request.method == 'POST':
        response = {'response': False, 'messages': list()}
        if request.POST.get('table_content'):
            contents = json.loads(request.POST.get('table_content'), parse_float=Decimal)
            data_list = list()
            errors = list()
            for idx, content in enumerate(contents):
                if all(x is None or str(x).strip() == '' for x in content):
                    # check if all elements of the content is None
                    continue
                else:
                    content_dict = dict(zip(field_names, content))
                    try:
                        box = Box.objects.get(serial_number=content_dict['box'])
                        data = ProjectModel()
                        data.__dict__.update(content_dict)
                        data.box = box
                        try:
                            data.full_clean()
                        except ValidationError as err:
                            for key in err.message_dict:
                                errors.append('%s: %s (第%d行)' % (key, ';'.join(err.message_dict[key]), idx+1))
                        data_list.append(data)
                    except Box.DoesNotExist:
                        errors.append('box: 此欄位必填 (第%d行)' % (idx+1))
            if not errors:
                # 全部對才存
                for data in data_list:
                    exist_data = ProjectModel.objects.filter(box=data.box).first()
                    if not exist_data:
                        action_flag = '1'
                        pre_dict = {}
                    else:
                        action_flag = '2'
                        pre_dict = object_to_dict(exist_data)
                        data.id = exist_data.id
                    data.save()
                    log_addition(request.user, 'project', model, data.id, action_flag, object_to_dict(data), pre_dict)
                response['response'] = True
                response['messages'].append('已成功新增/更新資料')
            else:
                response['messages'].extend(errors)
        return JsonResponse(response)
    return render(request, 'project/add_multiple.html', locals())
