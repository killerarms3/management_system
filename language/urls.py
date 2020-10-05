from django.urls import path
import language.views as language_views

app_name = 'language'
urlpatterns=[
    path('change_code/<app_label>/<model>', language_views.change_code, name='change_code'),
    path('view_code', language_views.view_code, name='view_code'),
    ]



