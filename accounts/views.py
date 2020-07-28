from accounts.models import Organization, Profile, UserProfile, Title
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.views.generic import ListView
from .forms import Profile_updateFrom, RegisterForm
from django.shortcuts import redirect
from django.views import generic
from django.urls import reverse
from django import forms
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from .token import Token

token_confirm = Token(settings.SECRET_KEY)

def index(request):
    return render(request, 'index.html')

class OrganizationListView(generic.ListView):
    model = Organization

def profile(request):
	return render(request, 'accounts/profile.html')

def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			email = form.cleaned_data['email']			
			form.save()
			user = User.objects.get(username=username)
			user.is_active = False
			user.save()
			token = token_confirm.generate_validate_token(username)
			message = '\n'.join([
				'{0}, Welcome to this system.'.format(username), 'Please access the following url to active your account.', 
				'/'.join(['127.0.0.1:8000', 'accounts/active', token])
			])
			send_mail('Test Email Title.', message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
			return HttpResponse('Please login your email and click the url to activate your account at one hour.')			
		else:
			return render(request, 'registration/register.html', {'form':form})
	else:
		form = RegisterForm()
		context = {'form': form}
		return render(request, 'registration/register.html', context)

@login_required
def profile_update(request, pk):
	user = get_object_or_404(User, pk=pk)
	try:
		user_profile = UserProfile.objects.get(user=user)
		profile = Profile.objects.get(user=user)
	except UserProfile.DoesNotExist:
		user_profile = UserProfile.objects.create(user=user, phone_number='', address='', gender='')
	except Profile.DoesNotExist:
		profile = Profile.objects.create(user=user, organization=Organization.objects.get(id=2), title=Title.objects.get(id=2))
	if request.method == 'POST':
		form = Profile_updateFrom(request.POST)
		if form.is_valid():
			user.first_name = form.cleaned_data['first_name']
			user.last_name = form.cleaned_data['last_name']
			user.save()

			user_profile.phone_number = form.cleaned_data['phone_number']
			user_profile.address = form.cleaned_data['address']
			user_profile.gender = form.cleaned_data['gender']
			user_profile.save()

			profile.organization = form.cleaned_data['org']
			profile.title = form.cleaned_data['title']
			profile.save()

			return HttpResponseRedirect(reverse('profile'))
	else:
		default_data = {
			'first_name':user.first_name,
			'last_name':user.last_name,
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
	 	return HttpResponse('The url is expired.')
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		return HttpResponse('The user is not exist.')
	user.is_active = True
	user.save()
	confirm = 'Verification is success, please login again.'
	return HttpResponseRedirect('/accounts/login', {'confirm': confirm})