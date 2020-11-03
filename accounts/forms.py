from django import forms
from django.forms import widgets
from accounts.models import Organization, Title
from django.forms import ModelChoiceField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class Profile_updateFrom(forms.Form):
    first_name = forms.CharField(label='名', max_length=50, required = True)
    last_name = forms.CharField(label='姓', max_length=50, required=True)
    nick_name = forms.CharField(label='暱稱', max_length=10, widget=forms.TextInput(attrs={'class':'form-control'}))
    phone_number = forms.CharField(label='連絡電話', max_length=20, required=False)
    address = forms.CharField(label='聯絡地址', max_length=100, required=False)
    gender = forms.CharField(label='性別', max_length=10, required=False)
    org= forms.ModelChoiceField(label='機構/部門', queryset=Organization.objects.all(), required=False)
    title = forms.ModelChoiceField(label='職稱', queryset=Title.objects.all(), required=False)

class RegisterForm(UserCreationForm):
    username = forms.CharField(label='* 帳號', max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    nick_name = forms.CharField(label='* 暱稱', max_length=10, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(label='* 姓', max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(label='* 名', max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(label='* E-mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='* 密碼', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='* 密碼確認', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'nick_name', 'last_name', 'first_name', 'email', 'password1', 'password2')

class Email_resetFrom(forms.Form):
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))
