from django.urls import path
import language.views as language_views

app_name = 'language'
urlpatterns=[
    path('code/edit/<app_label>/<model>', language_views.change_code, name='change_code'),
    path('code', language_views.view_code, name='view_code'),
    ]



