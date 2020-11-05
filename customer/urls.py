from django.urls import path
import customer.views as customer_views

app_name = 'customer'
urlpatterns=[
    path('add_organization', customer_views.add_organization, name='add_organization'),
    path('view_organization', customer_views.view_organization, name='view_organization'),
    path('change_organization/<int:id>/', customer_views.change_organization, name='change_organization'),
    path('add_title', customer_views.add_title, name='add_title'),
    path('view_title', customer_views.view_title, name='view_title'),
    path('change_title/<int:id>/', customer_views.change_title, name='change_title'),
    path('add_job', customer_views.add_job, name='add_job'),
    path('view_job', customer_views.view_job, name='view_job'),
    path('change_job/<int:id>/', customer_views.change_job, name='change_job'),
    path('add_customer', customer_views.add_customer, name='add_customer'),
    path('add_customers', customer_views.add_customers, name='add_customers'),
    path('view_customer', customer_views.view_customer, name='view_customer'),
    path('change_customer/<int:id>/', customer_views.change_customer, name='change_customer'),
    path('update_options/<model>', customer_views.update_options, name='update_options'),
    ]