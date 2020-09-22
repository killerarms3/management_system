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

# Create your views here.
@login_required
@permission_required('language.view_code', raise_exception=True)
@csrf_protect
def view_language(request):
    languages = Language.objects.all()
    return render(request, 'language/view_language.html', locals())
