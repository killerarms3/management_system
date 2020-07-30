from django.urls import path
import customer.views as customer_views

app_name = 'customer'
urlpatterns=[
    path('add_organization', customer_views.add_organization, name='add_organization'),
    path('view_organization', customer_views.view_organization, name='view_organization'),
    path('change_organization/<int:id>/', customer_views.change_organization, name='change_organization'),
    path('add_customer', customer_views.add_customer, name='add_customer'),
    path('view_customer', customer_views.view_customer, name='view_customer'),
    path('change_customer/<int:id>/', customer_views.change_customer, name='change_customer'),
    ]



