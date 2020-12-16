from django.urls import path
import experiment.views as experiment_views

app_name = 'experiment'
urlpatterns=[
    path('experiment/add', experiment_views.add_experiment, name='add_experiment'),
    path('contract/order/<int:pk>/experiment/add', experiment_views.add_order_experiments, name='add_order_experiments'),
    path('experiment/add/sheet', experiment_views.add_multiple, name='add_multiple'),
    path('experiment', experiment_views.view_experiment, name='view_experiment'),
    path('contract/box/<int:pk>/experiment', experiment_views.view_specific_experiment, name='view_specific_experiment'),
    path('contract/order/<int:pk>/experiment', experiment_views.view_experiment_list, name='view_experiment_list'),
    path('experiment/edit/<int:pk>', experiment_views.change_experiment, name='change_experiment'),
    ]


