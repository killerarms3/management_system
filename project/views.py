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
    ProjectModel = apps.get_model('project', model)
    if not request.user.has_perm('project.add_' + ProjectModel._meta.model_name):
        return redirect(reverse('accounts:index'))
    FormClass = GetDataCreateForm(ProjectModel)
    form = FormClass(instance=ProjectModel())
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            data = form.save()
            log_addition(request.user, 'project', model, data.id, '1', object_to_dict(data), {})
            messages.info(request, '已成功新增資料')
            return redirect(reverse('project:add_data', kwargs={'model': model}))
        else:
            field_tags = utils.getlabels('project', model)
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (field_tags[key], error))
                    except KeyError:
                        messages.error(request, '此資料已存在')
    return render(request, 'project/add_data.html', locals())

@login_required
@csrf_protect
def change_data(request, model, pk):
    ProjectModel = apps.get_model('project', model)
    if not request.user.has_perm('project.change_' + ProjectModel._meta.model_name):
        return redirect(reverse('accounts:index'))
    FormClass = GetDataCreateForm(ProjectModel, False)
    data = ProjectModel.objects.get(id=pk)
    form = FormClass(instance=data, auto_id='%s')
    if request.method == 'POST':
        form = FormClass(request.POST, instance=data, auto_id='%s')
        if form.is_valid():
            pre_dict = object_to_dict(data)
            data = form.save(commit=False)
            data.id = pk
            data.save()
            log_addition(request.user, 'project', model, data.id, '2', object_to_dict(data), pre_dict)
            messages.info(request, '已成功更新資料')
            return redirect(reverse('project:view_project_table', kwargs={'model': model}))
        else:
            field_tags = utils.getlabels('project', model)
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (field_tags[key], error))
                    except KeyError:
                        messages.error(request, '此資料已存在')
    form.fields['box'].widget.attrs['disabled'] = True
    return render(request, 'project/change_data.html', locals())

@login_required
def view_specific_data(request, model, pk):
    ProjectModel = apps.get_model('project', model)
    if not request.user.has_perm('project.view_' + ProjectModel._meta.model_name):
        return redirect(reverse('accounts:index'))
    field_tags = utils.getlabels('project', model)
    field_names = [field.name for field in ProjectModel._meta.fields if field.name != 'id']
    data = ProjectModel.objects.filter(box_id=pk).first()
    if not data:
        FormClass = GetDataCreateForm(ProjectModel)
        form = FormClass(instance=ProjectModel(), initial={'box': Box.objects.get(id=pk)})
        return render(request, 'project/add_data.html', locals())
    return render(request, 'project/view_specific_data.html', locals())

@login_required
def add_multiple(request, model):
    ProjectModel = apps.get_model('project', model)
    if not request.user.has_perm('project.add_' + ProjectModel._meta.model_name):
        return redirect(reverse('accounts:index'))
    FormClass = GetDataCreateForm(ProjectModel)
    form = FormClass(auto_id='%s', instance=ProjectModel())
    # update box options (exclude false)
    AddMultiple = utils.AddMultiple(request=request, form=form)
    AddMultipleView = AddMultiple.AddMultipleView(header='新增多筆資料', view_url=reverse('project:view_project_table', args=[model]), add_multiple_url=reverse('project:add_multiple', args=[model]))
    if request.method == 'POST':
        response = {'response': False, 'messages': list()}
        if request.POST.get('table_content'):
            label_dict = utils.getlabels('project', model)
            contents = json.loads(request.POST.get('table_content'), parse_float=Decimal)
            data_list = list()
            errors = list()
            for idx, content in enumerate(contents):
                if all(x is None or str(x).strip() == '' for x in content):
                    # check if all elements of the content is None
                    continue
                else:
                    content_dict = dict(zip(AddMultiple.field_names, [None if not cont else cont for cont in content]))
                    try:
                        box = Box.objects.get(serial_number=content_dict['box'])
                        data = ProjectModel()
                        data.__dict__.update(content_dict)
                        data.box = box
                        try:
                            data.full_clean()
                        except ValidationError as err:
                            for key in err.message_dict:
                                try:
                                    errors.append('%s: %s (第%d行)' % (label_dict[key], ';'.join(err.message_dict[key]), idx+1))
                                except KeyError:
                                    errors.append('此資料已存在 (第%d行)' % (idx+1))
                        data_list.append(data)
                    except Box.DoesNotExist:
                        errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['box'], idx+1))
            if not errors:
                # 全部對才存
                for data in data_list:
                    data.save()
                    log_addition(request.user, 'project', model, data.id, '1', object_to_dict(data), {})
                response['response'] = True
                response['messages'].append('已成功新增資料')
            else:
                response['messages'].extend(errors)
        return JsonResponse(response)
    return AddMultipleView