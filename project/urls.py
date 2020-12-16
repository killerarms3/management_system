from django.urls import path
import project.views as project_views

app_name = 'project'
urlpatterns=[
    path('project', project_views.view_project, name='view_project'),
    path('<model>', project_views.view_project_table, name='view_project_table'),
    path('<model>/contract/box/<int:pk>', project_views.view_specific_data, name='view_specific_data'),
    path('<model>/add', project_views.add_data, name='add_data'),
    path('<model>/add/sheet', project_views.add_multiple, name='add_multiple'),
    path('<model>/edit/<int:pk>', project_views.change_data, name='change_data'),
    ]


