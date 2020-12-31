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
from django.db.models import Count

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
            experiment = form.save()
            log_addition(request.user, 'experiment', 'experiment', experiment.id, '1', object_to_dict(experiment), {})
            messages.info(request, '已成功新增紀錄')
            return redirect(reverse('experiment:add_experiment'))
        else:
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (key, error))
                    except KeyError:
                        messages.error(request, '此紀錄已存在')
    return render(request, 'experiment/add_experiment.html', locals())

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
                                try:
                                    errors.append('%s: %s (第%d行)' % (label_dict[key], ';'.join(err.message_dict[key]), idx+1))
                                except KeyError:
                                    errors.append('此紀錄已存在 (第%d行)' % (idx+1))
                        experiment_list.append(experiment)
                    except Box.DoesNotExist:
                        errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['box'], idx+1))
                    except StopIteration:
                        if not content_dict['organization']:
                            errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['organization'], idx+1))
                        if not content_dict['transfer_organization']:
                            errors.append('%s: 此欄位必填 (第%d行)' % (label_dict['transfer_organization'], idx+1))
            if not errors:
                # 全部對才存，只新增不更新
                for experiment in experiment_list:
                    experiment.save()
                    log_addition(request.user, 'experiment', 'experiment', experiment.id, '1', object_to_dict(experiment), {})
                response['response'] = True
                response['messages'].append('已成功新增資料')
            else:
                response['messages'].extend(errors)
        return JsonResponse(response)
    return AddMultipleView

def getExperimentData(request, queryset):
    Data = dict()
    for experiment in queryset:
        Data[experiment.id] = [
            '',
            '<a href="%s"><i class="fas fa-edit"></i></a>' % (reverse('experiment:change_experiment', args=[experiment.id])) if request.user.has_perm('experiment.change_experiment') else '',
            str(experiment.box.serial_number),
            '%s %s' % (experiment.organization.name, experiment.organization.department),
            str(experiment.receiving_date) if experiment.receiving_date else '',
            str(experiment.complete_date) if experiment.complete_date else '',
            str(experiment.data_transfer_date) if experiment.data_transfer_date else '',
            '%s %s' % (experiment.transfer_organization.name, experiment.transfer_organization.department),
            utils.get_status(experiment.box.id),
            '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=800\', height=\'600\'); return false">%s</a>' % (reverse('contract:failed_edit', args=[experiment_records[experiment.box.serial_number]['record'][0]['failed_id']]),reverse('contract:failed_edit', args=[experiment_records[experiment.box.serial_number]['record'][0]['failed_id']]), experiment.box.get_failed()) if Failed.objects.filter(box=experiment.box) else '<a href="%s" target="popup" onclick="window.open(\'%s\', \'popup\', \'width=800\', height=\'600\'); return false"><i class="fas fa-plus"></i></a>' % (reverse('contract:add_specify_failed', args=[experiment.box.id]),reverse('contract:add_specify_failed', args=[experiment.box.id]))
        ]
    return Data


@login_required
@permission_required('experiment.view_experiment', raise_exception=True)
@csrf_protect
def view_experiment(request):
    ajax_url = reverse('experiment:view_experiment')
    experiment_ids = list()
    experiment_records = dict()
    for experiment in Experiment.objects.all().order_by('-box__id', '-receiving_date','-pk'):
        if experiment.box.serial_number not in experiment_records:
            experiment_records[experiment.box.serial_number] = []
            experiment_ids.append(experiment.id)
        record = {
            'change_experiment':reverse('experiment:change_experiment', args=[experiment.id]),
            'serial_number': experiment.box.serial_number,
            'organization': '%s %s' % (experiment.organization.name, experiment.organization.department),
            'receiving_date': str(experiment.receiving_date) if experiment.receiving_date else '',
            'complete_date': str(experiment.complete_date) if experiment.complete_date else '',
            'data_transfer_date': str(experiment.data_transfer_date) if experiment.data_transfer_date else '',
            'transfer_organization': '%s %s' % (experiment.transfer_organization.name, experiment.transfer_organization.department),
        }
        experiment_records[experiment.box.serial_number].append(record)
    if request.GET:
        columns = ['id', 'id', 'box.serial_number', 'organization', 'receiving_date', 'complete_date', 'data_transfer_date', 'transfer_organization', 'id', 'box.get_failed()']
        experiments = Experiment.objects.filter(pk__in=experiment_ids).order_by('-box__id', '-receiving_date','-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, experiments)
        DataTablesServer.getData = getExperimentData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'experiment/view_experiment.html', locals())

@login_required
@permission_required('experiment.view_experiment', raise_exception=True)
def view_specific_experiment(request, pk):
    try:
        box = Box.objects.get(id=pk)
    except Box.DoesNotExist:
        return redirect(reverse('experiment:view_experiment'))
    ajax_url = reverse('experiment:view_specific_experiment', args=[pk])
    experiment_ids = list()
    experiment_records = dict()
    for experiment in Experiment.objects.filter(box=box).order_by('-box__id', '-receiving_date','-pk'):
        if experiment.box.serial_number not in experiment_records:
            experiment_records[experiment.box.serial_number] = []
            experiment_ids.append(experiment.id)
        record = {
            'change_experiment':reverse('experiment:change_experiment', args=[experiment.id]),
            'serial_number': experiment.box.serial_number,
            'organization': '%s %s' % (experiment.organization.name, experiment.organization.department),
            'receiving_date': str(experiment.receiving_date) if experiment.receiving_date else '',
            'complete_date': str(experiment.complete_date) if experiment.complete_date else '',
            'data_transfer_date': str(experiment.data_transfer_date) if experiment.data_transfer_date else '',
            'transfer_organization': '%s %s' % (experiment.transfer_organization.name, experiment.transfer_organization.department),
        }
        experiment_records[experiment.box.serial_number].append(record)
    if request.GET:
        columns = ['id', 'id', 'box.serial_number', 'organization', 'receiving_date', 'complete_date', 'data_transfer_date', 'transfer_organization', 'id', 'box.get_failed()']
        experiments = Experiment.objects.filter(pk__in=experiment_ids).order_by('-box__id', '-receiving_date','-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, experiments)
        DataTablesServer.getData = getExperimentData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'experiment/view_experiment.html', locals())

@login_required
@permission_required('experiment.view_experiment', raise_exception=True)
def view_experiment_list(request, pk):
    try:
        order = Order.objects.get(id=pk)
    except Order.DoesNotExist:
        return redirect(reverse('contract:order-list'))
    ajax_url = reverse('experiment:view_experiment_list', args=[pk])
    experiment_ids = list()
    experiment_records = dict()
    boxes = Box.objects.filter(order=order)
    for experiment in Experiment.objects.filter(box_id__in=list(boxes.values_list(flat=True))).order_by('-box__id', '-receiving_date','-pk'):
        if experiment.box.serial_number not in experiment_records:
            experiment_records[experiment.box.serial_number] = []
            experiment_ids.append(experiment.id)
        record = {
            'change_experiment':reverse('experiment:change_experiment', args=[experiment.id]),
            'serial_number': experiment.box.serial_number,
            'organization': '%s %s' % (experiment.organization.name, experiment.organization.department),
            'receiving_date': str(experiment.receiving_date) if experiment.receiving_date else '',
            'complete_date': str(experiment.complete_date) if experiment.complete_date else '',
            'data_transfer_date': str(experiment.data_transfer_date) if experiment.data_transfer_date else '',
            'transfer_organization': '%s %s' % (experiment.transfer_organization.name, experiment.transfer_organization.department),
        }
        experiment_records[experiment.box.serial_number].append(record)
    if request.GET:
        columns = ['id', 'id', 'box.serial_number', 'organization', 'receiving_date', 'complete_date', 'data_transfer_date', 'transfer_organization', 'id', 'box.get_failed()']
        experiments = Experiment.objects.filter(pk__in=experiment_ids).order_by('-box__id', '-receiving_date','-pk')
        DataTablesServer = utils.DataTablesServer(request, columns, experiments)
        DataTablesServer.getData = getExperimentData
        DataTablesServer.runQueries()
        outputResult = DataTablesServer.outputResult()
        return JsonResponse(outputResult)
    return render(request, 'experiment/view_experiment.html', locals())

@login_required
@permission_required('experiment.change_experiment', raise_exception=True)
@csrf_protect
def change_experiment(request, pk):
    experiment = Experiment.objects.get(id=pk)
    form = ExperimentCreateForm(instance=experiment, auto_id='%s',)
    if request.method == 'POST':
        form = ExperimentCreateForm(request.POST, instance=experiment, auto_id='%s')
        if form.is_valid():
            pre_dict = object_to_dict(experiment)
            experiment = form.save(commit=False)
            experiment.id = pk
            experiment.save()
            log_addition(request.user, 'experiment', 'experiment', experiment.id, '2', object_to_dict(experiment), pre_dict)
            messages.info(request, '已成功更新紀錄')
            return redirect(reverse('experiment:view_experiment'))
        else:
            field_tags = utils.getlabels('experiment', 'experiment')
            for key in form.errors:
                for error in form.errors[key]:
                    try:
                        messages.error(request, '%s: %s' % (field_tags[key], error))
                    except KeyError:
                        messages.error(request, '此紀錄已存在')
    form.fields['box'].widget.attrs['disabled'] = True
    return render(request, 'experiment/change_experiment.html', locals())

@login_required
@permission_required('experiment.add_experiment', raise_exception=True)
@csrf_protect
def add_order_experiments(request, pk):
    try:
        order = Order.objects.get(id=pk)
    except Order.DoesNotExist:
        return redirect(reverse('contract:order-list'))
    organizations = Organization.objects.filter(is_active=True)
    boxes = Box.objects.filter(order_id=pk)
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
            messages.info(request, '已成功新增紀錄')
            return redirect(reverse('experiment:view_experiment_list', args=[order.id]))
    return render(request, 'experiment/add_order_experiments.html', locals())