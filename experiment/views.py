from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from contract.models import Box
from accounts.models import Organization
from experiment.models import Experiment
from lib.multi_add import AddMultiData

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
        # for idx, experiment_data in enumerate(data):
        #     # experiment
        #     experiment = Experiment()


    return add_data.view_upload(request, header='新增多筆記錄', sheet_template='/experiment/add_experiments_template.xlsx', action_url=reverse('experiment:add_experiments'))



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
            'change_experiment':reverse('experiment:change_experiment', kwargs={'id': experiment.id}),
            'serial_number': experiment.box.serial_number,
            'organization': '%s %s' % (experiment.organization.name, experiment.organization.department),
            'receiving_date': str(experiment.receiving_date) if experiment.receiving_date else '',
            'complete_date': str(experiment.complete_date) if experiment.complete_date else '',
            'data_transfer_date': str(experiment.data_transfer_date) if experiment.data_transfer_date else '',
            'transfer_organization': '%s %s' % (experiment.transfer_organization.name, experiment.transfer_organization.department)
        }
        experiment_records[experiment.box.serial_number].append(record)

    return render(request, 'experiment/view_experiment.html', locals())

# @login_required
# @permission_required('experiment.change_experiment', raise_exception=True)
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
