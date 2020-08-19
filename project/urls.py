from django.urls import path
import project.views as project_views

app_name = 'project'
urlpatterns=[
    path('add_project', project_views.add_project, name='add_project'),
    path('view_project', project_views.view_project, name='view_project'),
    path('view_project/<model>/', project_views.view_project_table, name='view_project_table'),
    path('change_project/<int:id>/', project_views.change_project, name='change_project'),
    ]


