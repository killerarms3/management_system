from django import forms
from django.forms import widgets
from accounts.models import Organization, Title
from django.forms import ModelChoiceField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class Profile_updateFrom(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=50, required = True)
    last_name = forms.CharField(label='Last Name', max_length=50, required=True)
    phone_number = forms.CharField(label='Phone Number', max_length=20, required=True)
    address = forms.CharField(label='Address', max_length=100, required=False)
    gender = forms.CharField(label='Gender', max_length=10, required=True)
    org= forms.ModelChoiceField(label='Organization', queryset=Organization.objects.all(), required=True)
    title = forms.ModelChoiceField(label='Title', queryset=Title.objects.all(), required=True)

class RegisterForm(UserCreationForm):
    username = forms.CharField(label='Account', widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Password Confirm', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2') 