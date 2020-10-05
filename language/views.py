from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import models
from django.contrib.contenttypes.models import ContentType
from language.models import Code
from django.conf import settings
from lib import utils

# Create your views here.
@login_required
@permission_required('language.view_code', raise_exception=True)
@csrf_protect
def view_code(request):
    codes = Code.objects.all()
    code_tables = dict()
    # 濾掉django.contrib相關models
    app_labels = {app_label for app_label in settings.INSTALLED_APPS if 'django.contrib' not in app_label}
    for model in apps.get_models():
        if model._meta.app_label in app_labels:
            key = model._meta.app_label + '-' + model.__name__
            code_tables[key] = {
                'field_names': [field.name for field in model._meta.fields],
                'label': utils.getlabels(model._meta.app_label, model.__name__)
            }
    return render(request, 'language/view_code.html', locals())

def change_code(request, app_label, model):
    Model = apps.get_model(app_label, model)
    field_names = [field.name for field in Model._meta.fields]
    label_dict = utils.getlabels(app_label, model)
    if request.method == 'POST':
        contenttype = ContentType.objects.get(app_label=app_label, model=model)
        for field_name in field_names:
            code, created = Code.objects.get_or_create(content_type=contenttype, code=field_name)
            code.name = request.POST[field_name].strip()
            code.save()
        return redirect(reverse('language:view_code'))
    return render(request, 'language/change_code.html', locals())