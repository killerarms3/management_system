from accounts.models import Organization, Profile, UserProfile, Title
from .forms import Profile_updateFrom, RegisterForm, Email_resetFrom
from .token import Token
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views import generic
from django.urls import reverse
from django import forms
from django.conf import settings
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.apps import apps
from django.contrib import messages

token_confirm = Token(settings.SECRET_KEY)

def index(request):
    return render(request, 'index.html')

class OrganizationListView(generic.ListView):
    model = Organization

@login_required
def profile(request):
	return render(request, 'accounts/profile.html')

def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		userprofile = apps.get_model('accounts', 'UserProfile')
		if userprofile.objects.filter(nick_name = request.POST['nick_name']):
			messages.error(request, '一個相同的暱稱已存在。')			
			context = {'form': form, 'messages': messages}
			return render(request, 'registration/register.html', context)
		if form.is_valid():
			username = form.cleaned_data['username']
			form.save()
			nuck_name = form.cleaned_data['nick_name']
			last_name = form.cleaned_data['last_name']
			first_name = form.cleaned_data['first_name']
			user = User.objects.get(username=username)
			user.last_name = last_name
			user.first_name = first_name
			user.is_active = False
			user.save()
			user_profile = UserProfile()
			user_profile.user = user
			user_profile.nick_name = nuck_name
			user_profile.save()
			profile = Profile()
			profile.user = user
			profile.save()
			active_mail(request, username)
			context = {
				'user':user
			}
			return HttpResponseRedirect(reverse('send_again', args=[user.username]), context)
		else:
			return render(request, 'registration/register.html', {'form':form})
	else:
		form = RegisterForm()
		context = {'form': form}
		return render(request, 'registration/register.html', context)

def active_mail(request, username):
	user = User.objects.get(username=username)
	token = token_confirm.generate_validate_token(username)
	current_site = get_current_site(request)
	mail_subject = 'Welcome!'
	message = render_to_string(
		'registration/user_authenticate_mail.html', {
		'username': username,
		'domain': current_site.domain,
		'token': token
	})
	email_send = EmailMessage(
		mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]
	)
	email_send.send()

@login_required
def profile_update(request, pk):
	user = get_object_or_404(User, pk=pk)
	if user.username != request.user.username:
		return HttpResponseNotFound('NOT FOUND')
	try:
		user_profile = UserProfile.objects.get(user=user)
	except UserProfile.DoesNotExist:
		user_profile = UserProfile.objects.create(
			user=user,
			phone_number='',
			address='',
			gender=''
		)
	try:
		profile = Profile.objects.get(user=user)
	except Profile.DoesNotExist:
		profile = Profile.objects.create(
			user=user,
			organization=Organization.objects.get(id=2),
			title=Title.objects.get(id=2)
		)
	if request.method == 'POST':
		form = Profile_updateFrom(request.POST)

		if form.is_valid():
			user.first_name = form.cleaned_data['first_name']
			user.last_name = form.cleaned_data['last_name']
			user.save()

			user_profile.phone_number = form.cleaned_data['phone_number']
			user_profile.address = form.cleaned_data['address']
			user_profile.gender = form.cleaned_data['gender']
			user_profile.nick_name = form.cleaned_data['nick_name']
			user_profile.save()

			profile.organization = form.cleaned_data['org']
			profile.title = form.cleaned_data['title']
			profile.save()

			return HttpResponseRedirect(reverse('profile'))
	else:
		default_data = {
			'first_name':user.first_name,
			'last_name':user.last_name,
			'nick_name':user_profile.nick_name,
			'phone_number':user_profile.phone_number,
			'address':user_profile.address,
			'gender':user_profile.gender,
			'org':profile.organization,
			'title':profile.title
			}
		form = Profile_updateFrom(default_data)
	return render(request, 'accounts/profile_update.html', {'form':form, 'user':user})

def active_user(request, token):
	try:
		username = token_confirm.confirm_validate_token(token)
	except:
	 	return HttpResponse('連結已過期。')
	try:
		user = User.objects.get(username=username)
	except:
		return HttpResponse('使用者不存在。')
	user.is_active = True
	user.save()
	confirm = '驗證成功，請重新登入。'
	return HttpResponseRedirect('/accounts/login', {'confirm': confirm})

def email_send_again(request, username):
	user = User.objects.get(username=username)
	if user.is_active:
		return HttpResponseNotFound('該帳戶已激活。')
	if request.method == 'POST':
		mailForm = Email_resetFrom(request.POST)
		if mailForm.is_valid():
			user.email = mailForm.cleaned_data['email']
			user.save()
			active_mail(request, user.username)
			return HttpResponseRedirect(reverse('send_again', args=[user.username]),  {'mailForm':mailForm, 'user':user})
		else:
			return render(request, 'registration/mail_active_confirm.html', {'mailForm':mailForm, 'user':user})
	else:
		mailForm = Email_resetFrom()
		return render(request, 'registration/mail_active_confirm.html', {'mailForm':mailForm, 'user':user})