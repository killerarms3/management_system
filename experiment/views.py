from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from contract.models import Box, Failed, Order
from accounts.models import Organization
from experiment.models import Experiment
from lib.multi_add import AddMultiData
from lib.Validator import ValidateOrganization
from django.core.exceptions import ValidationError
import datetime

# Create your views here.
@login_required
@permission_required('experiment.add_experiment', raise_exception=True)
@csrf_protect
def add_experiment(request):
    boxes = Box.objects.all()
    organizations = Organization.objects.filter(is_active=True)
    if request.method == 'POST':
        # 假設同個單位，不會再同一天收到多次同個採樣盒的檢體
        # (box_id, organization_id, receiving_date)必為unique
        box = Box.objects.get(id=request.POST['box'])
        organization = Organization.objects.get(id=request.POST['organization'])
        transfer_organization = Organization.objects.get(id=request.POST['transfer_organization'])
        exist_experiment = Experiment.objects.filter(box=box, organization=organization, receiving_date=request.POST['receiving_date'])
        if exist_experiment:
            messages.error(request, '此紀錄已存在')
            return HttpResponseRedirect('/experiment/view_experiment')
        experiment = Experiment()
        experiment.box = box
        experiment.organization = organization
        experiment.receiving_date = request.POST['receiving_date']
        if request.POST['complete_date']:
            experiment.complete_date = request.POST['complete_date']
        if request.POST['data_transfer_date']:
            experiment.data_transfer_date = request.POST['data_transfer_date']
        experiment.transfer_organization = transfer_organization
        experiment.save()
        messages.info(request, '已成功新增紀錄')
        return redirect(reverse('experiment:view_experiment'))
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
                data[idx]['status'] = status
                data[idx]['messages'].extend(mess)
            status, mess, transfer_organization = ValidateOrganization(Organization, 'transfer_organization', experiment_data['transfer_organization'])
            if mess:
                data[idx]['status'] = status
                data[idx]['messages'].extend(mess)
            boxs = Box.objects.filter(serial_number=experiment_data['serial_number'])
            if not boxs:
                data[idx]['status'] = 'Falied'
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
                is_failed = True
        if is_failed:
            messages.info(request, '表格資料內容錯誤，請修正後重新上傳!')
        else:
            for idx, experiment in enumerate(experiments):
                exist_experiments = Experiment.objects.filter(box=experiment.box, organization=experiment.organization, receiving_date=experiment.receiving_date)
                if exist_experiments:
                    experiment.id = exist_experiments[0].id
                else:
                    experiment.save()
                data[idx]['status'] = 'success'
            messages.info(request, '已成功新增資料')
        action_url = reverse('experiment:view_experiment')
        back_url = reverse('experiment:add_experiments')
        return render(request, 'add_data_status.html', locals())
    return add_data.view_upload(request, header='新增多筆記錄', sheet_template='add_experiments_template.xlsx', action_url=reverse('experiment:add_experiments'))

@login_required
@permission_required('experiment.view_experiment', raise_exception=True)
@csrf_protect
def view_experiment(request):
    experiments = Experiment.objects.all().order_by('box__id', '-receiving_date','-pk')
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
    experiments = Experiment.objects.filter(box=box).order_by('box__id', '-receiving_date','-pk')
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
    experiments = Experiment.objects.filter(box_id__in=list(boxes.values_list(flat=True))).order_by('box__id', '-receiving_date','-pk')
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
    boxes = Box.objects.all()
    organizations = Organization.objects.filter(is_active=True)
    experiment = Experiment.objects.get(id=id)
    if request.method == 'POST':
        # 假設同個單位，不會再同一天收到多次同個採樣盒的檢體
        # (box_id, organization_id, receiving_date)必為unique
        box = Box.objects.get(id=request.POST['box'])
        organization = Organization.objects.get(id=request.POST['organization'])
        transfer_organization = Organization.objects.get(id=request.POST['transfer_organization'])
        exist_experiment = Experiment.objects.filter(box=box, organization=organization, receiving_date=request.POST['receiving_date'])
        if exist_experiment and exist_experiment[0].id != id:
            messages.error(request, '此紀錄已存在')
            return HttpResponseRedirect('/experiment/view_experiment')
        experiment.box = box
        experiment.organization = organization
        experiment.receiving_date = request.POST['receiving_date']
        if request.POST['complete_date']:
            experiment.complete_date = request.POST['complete_date']
        if request.POST['data_transfer_date']:
            experiment.data_transfer_date = request.POST['data_transfer_date']
        experiment.transfer_organization = transfer_organization
        experiment.save()
        messages.info(request, '已成功更新紀錄')
        return redirect(reverse('experiment:view_experiment'))
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
        for key in keys:
            idx = key.replace('serial_number', '')
            organization = Organization.objects.get(id=request.POST['organization'+idx])
            transfer_organization = Organization.objects.get(id=request.POST['transfer_organization'+idx])
            for serial_number in request.POST[key].split(','):
                box = Box.objects.get(serial_number=serial_number)
                exist_experiment = Experiment.objects.filter(box=box, organization=organization, receiving_date=request.POST['receiving_date'+idx])
                if exist_experiment:
                    messages.error(request, '%s: 紀錄已存在' % (serial_number))
                    return redirect(reverse('experiment:add_order_experiments', kwargs={'order_id': order_id}))
                experiment = Experiment()
                experiment.box = box
                experiment.organization = organization
                experiment.transfer_organization = transfer_organization
                experiment.receiving_date = request.POST['receiving_date'+idx]
                if request.POST['complete_date'+idx]:
                    experiment.complete_date = request.POST['complete_date'+idx]
                if request.POST['data_transfer_date'+idx]:
                    experiment.data_transfer_date = request.POST['data_transfer_date'+idx]
                experiments.append(experiment)
        # 都沒問題，才存
        for experiment in experiments:
            experiment.save()
        messages.info(request, '已成功更新紀錄')
        return redirect(reverse('experiment:view_experiment'))
    return render(request, 'experiment/add_order_experiments.html', locals())