from django.urls import path
import experiment.views as experiment_views

app_name = 'experiment'
urlpatterns=[
    path('add_experiment', experiment_views.add_experiment, name='add_experiment'),
    path('add_experiments', experiment_views.add_experiments, name='add_experiments'),
    path('add_experiments/<int:order_id>/', experiment_views.add_order_experiments, name='add_order_experiments'),
    path('add_multiple', experiment_views.add_multiple, name='add_multiple'),
    path('view_experiment', experiment_views.view_experiment, name='view_experiment'),
    path('view_experiment/<serial_number>', experiment_views.view_specific_experiment, name='view_specific_experiment'),
    path('view_experiment/<int:order_id>/', experiment_views.view_experiment_list, name='view_experiment_list'),
    path('change_experiment/<int:id>/', experiment_views.change_experiment, name='change_experiment'),
    ]



