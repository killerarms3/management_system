from django.urls import path
import customer.views as customer_views

app_name = 'customer'
urlpatterns=[
    path('organization/add', customer_views.add_organization, name='add_organization'),
    path('organization', customer_views.view_organization, name='view_organization'),
    path('organization/edit/<int:pk>', customer_views.change_organization, name='change_organization'),
    path('title/add', customer_views.add_title, name='add_title'),
    path('title', customer_views.view_title, name='view_title'),
    path('title/edit/<int:pk>', customer_views.change_title, name='change_title'),
    path('job/add', customer_views.add_job, name='add_job'),
    path('job', customer_views.view_job, name='view_job'),
    path('job/edit/<int:pk>', customer_views.change_job, name='change_job'),
    path('customer/add', customer_views.add_customer, name='add_customer'),
    path('customer/add/sheet', customer_views.add_multiple, name='add_multiple'),
    path('customer', customer_views.view_customer, name='view_customer'),
    path('customer/<int:pk>', customer_views.view_specific_customer, name='view_specific_customer'),
    path('customer/edit/<int:pk>', customer_views.change_customer, name='change_customer'),
    path('get/<model>', customer_views.update_options, name='update_options'),
    path('get/<int:pk>/organization', customer_views.get_customer_organization, name='get_customer_organization'),
    ]



