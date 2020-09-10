from .function import log_addition, object_to_dict, Update_log_dict, Create_log_dict, message_transfer
from .models import History
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connection
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

# Create your views here.
class HistoryListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'history.view_history'
    model = History
    # 將結果以時間新道舊順序排列
    def get_queryset(self):
        Queryset = History.objects.all().order_by('-date')
        return Queryset
    
    def get_context_data(self, **kwargs):
        obj_message_dict = {}
        diff_dict_list = {}
        action_flag_dict = {'1': 'add', '2': 'change', '3': 'delete', '4': 'recovery'}
        ManytoManyList = ['organization', 'plan']
        Obj_list = self.get_queryset()

        for obj in Obj_list:
            temp_dict, diff_dict = message_transfer(obj.change_message)
            obj_message_dict[obj.id] = temp_dict
            diff_dict_list[obj.id] = diff_dict

        model_dict = {
            'user': apps.get_model('auth', 'user'),
            'plan': apps.get_model('product', 'Plan'),
            'customer': apps.get_model('customer', 'Customer'),
            'organization': apps.get_model('customer', 'Organization'),
            'contract': apps.get_model('contract', 'Contract'),
            'order': apps.get_model('contract', 'Order'),
            'receipt': apps.get_model('contract', 'Receipt'),
            'box': apps.get_model('contract', 'Box'),
            'failed': apps.get_model('contract', 'Failed'),
            'destroyed': apps.get_model('contract', 'Destroyed'),
            'examiner': apps.get_model('contract', 'Examiner'),
            'payment_method': apps.get_model('contract', 'Payment_method'),
            'failed_reason': apps.get_model('contract', 'Failed_reason')
        }
        
        context = super().get_context_data(**kwargs)
        context['model_dict'] = model_dict
        context['diff_dict_list'] = diff_dict_list
        context['dict'] = obj_message_dict
        context['action_flag'] = action_flag_dict
        context['ManytoManyList'] = ManytoManyList
        return context

class UserHistoryList(HistoryListView):
    permission_required = 'history.can_view_self_history'
    template_name = 'history_list.html'

    def get_queryset(self):
        user = User.objects.get(pk=self.request.user.id)
        Queryset = History.objects.filter(user=user).order_by('-date')
        return Queryset

def Recovery(request, pk):
    action_flag_dict = {'1': 'add', '2': 'change', '3': 'delete', '4': 'recovery'}
    ManytoManyList = ['organization', 'plan']
    target_dict = {}
    keys = []
    History = apps.get_model('history', 'History')
    history = History.objects.get(pk=pk)
    dict, diff_dict = message_transfer(history.change_message)
    if request.method == 'POST':
        Obj = apps.get_model(history.content_type.app_label, history.content_type.model)
        # 如果object已被刪除的例外處理
        try:
            obj = Obj.objects.get(pk=history.object_id)
        except:
            return HttpResponseRedirect(reverse('history:history-list'))
        # --------- log recorder --------
        pre_dict = object_to_dict(obj)
        # --------- log recorder --------
        for key in diff_dict.keys():
            if key not in ManytoManyList:
                if  dict[action_flag_dict[history.action_flag]]['previous'][key] == '':
                    if 'date' in key: # 復原回去的資料欄位型態是時間且空值時
                        target_dict[key] = None
                        continue                    
            target_dict[key] = dict[action_flag_dict[history.action_flag]]['previous'][key]
        # 判斷m2m，目前是寫死的，希望之後可以用變量代替
        for key in target_dict.keys():
            if key == 'plan':
                obj.plan.clear()
                obj.plan.add(*target_dict[key])
                keys.append(key)
            elif key == 'organization':
                obj.organization.clear()
                obj.organization.add(*target_dict[key])
                keys.append(key)
        for key in keys:
            target_dict.pop(key)
        obj.__dict__.update(**target_dict)
        obj.save()
        # --------- log recorder --------
        current_dict = object_to_dict(obj)
        log_addition(request.user, history.content_type.app_label, history.content_type.model, history.object_id, '4', current_dict, pre_dict)
        # --------- log recorder --------
        return HttpResponseRedirect(reverse('history:history-list'))
    context = {'history':history, 'dict':dict, 'diff_dict':diff_dict}
    return render(request, 'history/recover_confirm.html', context)

def Recovery_by_attribute(request, pk, attr):
    action_flag_dict = {'1': 'add', '2': 'change', '3': 'delete', '4': 'recovery'}
    ManytoManyList = ['organization', 'plan']
    target_dict = {}
    History = apps.get_model('history', 'History')
    history = History.objects.get(pk=pk)
    dict, diff_dict = message_transfer(history.change_message)
    if request.method == 'POST':
        Obj = apps.get_model(history.content_type.app_label, history.content_type.model)
        # 如果object已被刪除/不存在的例外處理
        try:
            obj = Obj.objects.get(pk=history.object_id)
        except:
            return HttpResponseRedirect(reverse('history:history-list'))
        # --------- log recorder --------
        pre_dict = object_to_dict(obj)
        # --------- log recorder --------
        if attr not in ManytoManyList:
            if  dict[action_flag_dict[history.action_flag]]['previous'][attr] == '':
                if 'date' in attr: # 復原回去的資料欄位型態是時間且空值時
                    target_dict[attr] = None
                else:
                    target_dict[attr] = dict[action_flag_dict[history.action_flag]]['previous'][attr]
            else:
                target_dict[attr] = dict[action_flag_dict[history.action_flag]]['previous'][attr]
            obj.__dict__.update(**target_dict)
        elif attr == 'plan':
            obj.plan.clear()
            obj.plan.add(*target_dict[attr])
        elif attr == 'organization':
            obj.organization.clear()
            obj.organization.add(*target_dict[attr])
        obj.save()
        # --------- log recorder --------
        current_dict = object_to_dict(obj)
        log_addition(request.user, history.content_type.app_label, history.content_type.model, history.object_id, '4', current_dict, pre_dict)
        # --------- log recorder --------
        return HttpResponseRedirect(reverse('history:history-list'))
    context = {'history':history, 'dict':dict, 'diff_dict':diff_dict}
    return render(request, 'history/recover_confirm.html', context)