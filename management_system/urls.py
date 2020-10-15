"""management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from lib.multi_add import download 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customer/',include('customer.urls', namespace='customer')),
    path('product/',include('product.urls', namespace='product')),
    path('experiment/',include('experiment.urls', namespace='experiment')),
    path('project/',include('project.urls', namespace='project')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('customer/', include('django.contrib.auth.urls')),
    path('contract/', include('contract.urls', namespace = 'contract')),
    path('contract/', include('django.contrib.auth.urls')),
    path('', RedirectView.as_view(url = 'accounts/', permanent = True)),
    path('history/',include('history.urls', namespace='history')),
    path('download/<filename>/', download, name='download'),
    path('language/',include('language.urls', namespace='language')),
]

urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
