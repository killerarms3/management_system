from django.urls import path
import project.views as project_views

app_name = 'project'
urlpatterns=[
    path('view_project', project_views.view_project, name='view_project'),
    path('view_project/<model>/', project_views.view_project_table, name='view_project_table'),
    path('view_project/<model>/<serial_number>', project_views.view_specific_data, name='view_specific_data'),
    path('add_data/<model>/', project_views.add_data, name='add_data'),
    path('change_data/<model>/<int:id>/', project_views.change_data, name='change_data'),
    ]