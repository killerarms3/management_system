from django.urls import path
import experiment.views as experiment_views

app_name = 'experiment'
urlpatterns=[
    path('add_experiment', experiment_views.add_experiment, name='add_experiment'),
    path('add_experiments', experiment_views.add_experiments, name='add_experiments'),
    path('view_experiment', experiment_views.view_experiment, name='view_experiment'),
    path('change_experiment/<int:id>/', experiment_views.change_experiment, name='change_experiment'),
    ]



