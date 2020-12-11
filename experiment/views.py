from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from contract.models import Box, Failed, Order
from accounts.models import Organization
from experiment.models import Experiment
from lib.multi_add import AddMultiData
from lib.Validator import ValidateOrganization
from django.core.exceptions import ValidationError
import datetime
from history.models import History
from history.function import log_addition, object_to_dict, Update_log_dict, Create_log_dict
from experiment.forms import ExperimentCreateForm
from lib import utils
import json
from decimal import Decimal

# Create your views here.
@login_required
@permission_required('experiment.add_experiment', raise_exception=True)
@csrf_protect
def add_experiment(request):
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    form = ExperimentCreateForm(auto_id='%s', initial={'receiving_date': now})
    if request.method == 'POST':
        # 假設同個單位，不會再同一天收到多次同個採樣盒的檢體
        # (box, organization, receiving_date)必為unique
        form = ExperimentCreateForm(request.POST, auto_id='%s')
        if form.is_valid():
            exist_experiment = Experiment.objects.filter(box=form.cleaned_data['box'], organization=form.cleaned_data['organization'], receiving_date=form.cleaned_data['receiving_date'])
            if exist_experiment:
                messages.error(request, '此紀錄已存在')
            else:
                experiment = form.save()
                log_addition(request.user, 'experiment', 'experiment', experiment.id, '1', object_to_dict(experiment), {})
                messages.info(request, '已成功新增紀錄')
                return redirect(reverse('experiment:add_experiment'))
        else:
            messages.error(request, '資料格式錯誤')
            for key in form.errors:
                for error in form.errors[key]:
                    messages.error(request, '%s: %s' % (key, error))
    return render(request, 'experiment/add_experiment.html', locals())

@login_required
@permission_required('experiment.add_experiment', raise_exception=True)
@csrf_protect
def add_experiments(request):
    add_data = AddMultiData(field_number=6)
    if request.method == 'POST':
        column_codes, column_dict, data = add_data.read_upload(file_contents=request.FILES['sheet'].read())
        is_failed = False
        experiments = list()
        for idx, experiment_data in enumerate(data):
            # 之後改寫
            status, mess, organization = ValidateOrganization(Organization, 'organization', experiment_data['organization'])
            if mess:
                data[idx]['messages'].extend(mess)
            status, mess, transfer_organization = ValidateOrganization(Organization, 'transfer_organization', experiment_data['transfer_organization'])
            if mess:
                data[idx]['messages'].extend(mess)
            boxs = Box.objects.filter(serial_number=experiment_data['serial_number'])
            if not boxs:
                data[idx]['messages'].append('serial_number: 找不到此流水號')
            elif organization and transfer_organization:
                # experiment
                experiment = Experiment()
                experiment.__dict__.update(**experiment_data)
                experiment.box = boxs[0]
                experiment.organization = organization
                experiment.transfer_organization = transfer_organization
                experiments.append(experiment)
                try:
                    experiment.full_clean()
                except ValidationError as err:
                    data[idx]['status'] = 'Failed'
                    data[idx]['messages'].extend(['%s: %s' % (key, ';'.join(err.message_dict[key])) for key in err.message_dict])
            if data[idx]['messages']:
                data[idx]['status'] = 'Falied'
                is_failed = True
        if is_failed:
            messages.error(request, '表格資料內容錯誤，請修正後重新上傳!')
        else:
            for idx, experiment in enumerate(experiments):
                exist_experiments = Experiment.objects.filter(box=experiment.box, organization=experiment.organization, receiving_date=experiment.receiving_date)
                if exist_experiments:
                    pre_dict = object_to_dict(exist_experiments[0])
                    experiment.id = exist_experiments[0].id
                    experiment.save()
                    log_addition(request.user, 'experiment', 'experiment', experiment.id, '2', object_to_dict(experiment), pre_dict)
                else:
                    experiment.save()
                    log_addition(request.user, 'experiment', 'experiment', experiment.id, '1', object_to_dict(experiment), {})
                data[idx]['status'] = 'success'
            messages.info(request, '已成功新增資料')
        action_url = reverse('experiment:view_experiment')
        back_url = reverse('experiment:add_experiments')
        return render(request, 'add_data_status.html', locals())
    return add_data.view_upload(request, header='新增多筆記錄', sheet_template='add_experiments_template.xlsx', action_url=reverse('experiment:add_experiments'))

@login_required
@permission_required('experiment.add_experiment', raise_exception=True)
@csrf_protect
def add_multiple(request):
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    form = ExperimentCreateForm(auto_id='%s', initial={'receiving_date': now})
    AddMultiple = utils.AddMultiple(request=request, form=form)
    AddMultipleView = AddMultiple.AddMultipleView(header='新增多筆紀錄', view_url=reverse('experiment:view_experiment'), add_multiple_url=reverse('experiment:add_multiple'))
    if request.method == 'POST':
        response = {'response': False, 'messages': list()}
        if request.POST.get('table_content'):
            label_dict = utils.getlabels('experiment', 'experiment')
            contents = json.loads(request.POST.get('table_content'), parse_float=Decimal)
            experiment_list = list()
            errors = list()
            for idx, content in enumerate(contents):
                if all(x is None or str(x).strip() == '' for x in content):
                    # check if all elements of the content is None
                    continue
                else:
                    content_dict = dict(zip(AddMultiple.field_names, content))
                    try:
                        experiment = Experiment()
                        experiment.__dict__.update(content_dict)
                        experiment.box = Box.objects.get(serial_number=content_dict['box'])
                        experiment.organization = next(o for o in Organization.objects.all() if str(o) == content_dict['organization'])
                        experiment.transfer_organization = next(o for o in Organization.objects.all() if str(o) == content_dict['transfer_organization'])
                        try:
                            experiment.full_clean()
                        except ValidationError as err:
                            for key in err.message_dict:
                                errors.append('%s: %s (第%d行)' % (label_dict[key], ';'.join(err.message_dict[key]), idx+1))
                        experiment_list.append(experiment)
                    except Box.DoesNotExist:
                        errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['box'], idx+1))
                    except StopIteration:
                        if not content_dict['organization']:
                            errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['organization'], idx+1))
                        if not content_dict['transfer_organization']:
                            errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['transfer_organization'], idx+1))
            if not errors:
                # 全部對才存
                for experiment in experiment_list:
                    exist_experiment = Experiment.objects.filter(box=experiment.box, organization=experiment.organization, receiving_date=experiment.receiving_date).first()
                    if not exist_experiment:
                        action_flag = '1'
                        pre_dict = {}
                    else:
                        action_flag = '2'
                        pre_dict = object_to_dict(exist_experiment)
                        experiment.id = exist_experiment.id
                    experiment.save()
                    log_addition(request.user, 'experiment', 'experiment', experiment.id, action_flag, object_to_dict(experiment), pre_dict)
                response['response'] = True
                response['messages'].append('已成功新增/更新資料')
            else:
                response['messages'].extend(errors)
        return JsonResponse(response)
    return AddMultipleView

@login_required
@permission_required('experiment.view_experiment', raise_exception=True)
@csrf_protect
def view_experiment(request):
    experiments = Experiment.objects.all().order_by('-box__id', '-receiving_date','-pk')
    experiment_records = dict()
    for experiment in experiments:
        if experiment.box.serial_number not in experiment_records:
            experiment_records[experiment.box.serial_number] = list()
        record = {
            'id': str(experiment.id),
            'box_id': str(experiment.box.id),
            'change_experiment':reverse('experiment:change_experiment', kwargs={'id': experiment.id}),
            'serial_number': experiment.box.serial_number,
            'organization': '%s %s' % (experiment.organization.name, experiment.organization.department),
            'receiving_date': str(experiment.receiving_date) if experiment.receiving_date else '',
            'complete_date': str(experiment.complete_date) if experiment.complete_date else '',
            'data_transfer_date': str(experiment.data_transfer_date) if experiment.data_transfer_date else '',
            'transfer_organization': '%s %s' % (experiment.transfer_organization.name, experiment.transfer_organization.department),
            'failed_id': str()
        }
        faileds = Failed.objects.filter(box=experiment.box)
        if faileds:
            record['failed_id'] = str(faileds[0].id)
        experiment_records[experiment.box.serial_number].append(record)
    return render(request, 'experiment/view_experiment.html', locals())

@login_required
@permission_required('experiment.view_experiment', raise_exception=True)
@csrf_protect
def view_specific_experiment(request, serial_number):
    try:
        box = Box.objects.get(serial_number=serial_number)
    except Box.DoesNotExist:
        return redirect(reverse('experiment:view_experiment'))
    experiments = Experiment.objects.filter(box=box).order_by('-box__id', '-receiving_date','-pk')
    experiment_records = dict()
    for experiment in experiments:
        if experiment.box.serial_number not in experiment_records:
            experiment_records[experiment.box.serial_number] = list()
        record = {
            'id': str(experiment.id),
            'box_id': str(experiment.box.id),
            'change_experiment':reverse('experiment:change_experiment', kwargs={'id': experiment.id}),
            'serial_number': experiment.box.serial_number,
            'organization': '%s %s' % (experiment.organization.name, experiment.organization.department),
            'receiving_date': str(experiment.receiving_date) if experiment.receiving_date else '',
            'complete_date': str(experiment.complete_date) if experiment.complete_date else '',
            'data_transfer_date': str(experiment.data_transfer_date) if experiment.data_transfer_date else '',
            'transfer_organization': '%s %s' % (experiment.transfer_organization.name, experiment.transfer_organization.department),
            'failed_id': str()
        }
        faileds = Failed.objects.filter(box=experiment.box)
        if faileds:
            record['failed_id'] = str(faileds[0].id)
        experiment_records[experiment.box.serial_number].append(record)
    return render(request, 'experiment/view_experiment.html', locals())

@login_required
@permission_required('experiment.view_experiment', raise_exception=True)
@csrf_protect
def view_experiment_list(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect(reverse('contract:order-list'))
    boxes = Box.objects.filter(order=order)
    experiments = Experiment.objects.filter(box_id__in=list(boxes.values_list(flat=True))).order_by('-box__id', '-receiving_date','-pk')
    experiment_records = dict()
    for experiment in experiments:
        if experiment.box.serial_number not in experiment_records:
            experiment_records[experiment.box.serial_number] = list()
        record = {
            'id': str(experiment.id),
            'box_id': str(experiment.box.id),
            'change_experiment':reverse('experiment:change_experiment', kwargs={'id': experiment.id}),
            'serial_number': experiment.box.serial_number,
            'organization': '%s %s' % (experiment.organization.name, experiment.organization.department),
            'receiving_date': str(experiment.receiving_date) if experiment.receiving_date else '',
            'complete_date': str(experiment.complete_date) if experiment.complete_date else '',
            'data_transfer_date': str(experiment.data_transfer_date) if experiment.data_transfer_date else '',
            'transfer_organization': '%s %s' % (experiment.transfer_organization.name, experiment.transfer_organization.department),
            'failed_id': str()
        }
        faileds = Failed.objects.filter(box=experiment.box)
        if faileds:
            record['failed_id'] = str(faileds[0].id)
        experiment_records[experiment.box.serial_number].append(record)
    return render(request, 'experiment/view_experiment.html', locals())

@login_required
@permission_required('experiment.change_experiment', raise_exception=True)
@csrf_protect
def change_experiment(request, id):
    experiment = Experiment.objects.get(id=id)
    form = ExperimentCreateForm(instance=experiment, auto_id='%s',)
    if request.method == 'POST':
        form = ExperimentCreateForm(request.POST, auto_id='%s')
        if form.is_valid():
            exist_experiment = Experiment.objects.filter(box=form.cleaned_data['box'], organization=form.cleaned_data['organization'], receiving_date=form.cleaned_data['receiving_date'])
            if exist_experiment:
                messages.error(request, '此紀錄已存在')
            else:
                pre_dict = object_to_dict(experiment)
                experiment = form.save(commit=False)
                experiment.id = id
                experiment.save()
                log_addition(request.user, 'experiment', 'experiment', experiment.id, '2', object_to_dict(experiment), pre_dict)
                messages.info(request, '已成功更新紀錄')
                return redirect(reverse('experiment:view_experiment'))
        else:
            messages.error(request, '資料格式錯誤')
            for key in form.errors:
                for error in form.errors[key]:
                    messages.error(request, '%s: %s' % (key, error))
    return render(request, 'experiment/change_experiment.html', locals())

@login_required
@permission_required('experiment.add_experiment', raise_exception=True)
@csrf_protect
def add_order_experiments(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect(reverse('contract:order-list'))
    organizations = Organization.objects.filter(is_active=True)
    boxes = Box.objects.filter(order_id=order_id)
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        keys = [key for key in request.POST.keys() if 'serial_number' in key]
        experiments = list()
        is_failed = False
        for key in keys:
            idx = key.replace('serial_number', '')
            organization = Organization.objects.get(id=request.POST['organization'+idx])
            transfer_organization = Organization.objects.get(id=request.POST['transfer_organization'+idx])
            for serial_number in request.POST[key].split(','):
                box = Box.objects.get(serial_number=serial_number)
                exist_experiment = Experiment.objects.filter(box=box, organization=organization, receiving_date=request.POST['receiving_date'+idx])
                if exist_experiment:
                    messages.error(request, '%s: 紀錄已存在' % (serial_number))
                    # return redirect(reverse('experiment:add_order_experiments', kwargs={'order_id': order_id}))
                else:
                    experiment = Experiment()
                    experiment.box = box
                    experiment.organization = organization
                    experiment.transfer_organization = transfer_organization
                    experiment.receiving_date = request.POST['receiving_date'+idx]
                    if request.POST['complete_date'+idx]:
                        experiment.complete_date = request.POST['complete_date'+idx]
                    if request.POST['data_transfer_date'+idx]:
                        experiment.data_transfer_date = request.POST['data_transfer_date'+idx]
                    try:
                        experiment.full_clean()
                    except ValidationError as err:
                        is_failed = True
                        for k in err.message_dict:
                            messages.error(request, '%s: %s (%s)' % (k, ';'.join(err.message_dict[k]), serial_number))
                    experiments.append(experiment)
        if is_failed:
            return render(request, 'experiment/add_order_experiments_failed.html', locals())
        else:
            # 都沒問題，才存
            for experiment in experiments:
                experiment.save()
                log_addition(request.user, 'experiment', 'experiment', experiment.id, '1', object_to_dict(experiment), {})
            messages.info(request, '已成功更新紀錄')
            return redirect(reverse('experiment:view_experiment_list', args=[order_id]))
    return render(request, 'experiment/add_order_experiments.html', locals())