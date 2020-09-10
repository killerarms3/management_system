from django.urls import path
from . import views
from django.contrib.auth.models import User
from django.contrib import auth
from django.views.generic import ListView
from django.views.generic import DetailView
from .views import register
import re
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('organization/', views.OrganizationListView.as_view(), name = 'organization'),
    path('profile/', views.profile, name = 'profile'),
    path('register/', views.register, name = 'register'),
    path('profile/<int:pk>/update', views.profile_update, name = 'profile-update'),
    path('active/<token>', views.active_user, name = 'active_user'),
    path('check_mail/<username>', views.email_send_again, name = 'send_again'),
]
