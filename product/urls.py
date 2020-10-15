from django.urls import path
import product.views as product_views

app_name = 'product'
urlpatterns=[
    path('add_product', product_views.add_product, name='add_product'),
    path('view_product', product_views.view_product, name='view_product'),
    path('view_product/<int:id>', product_views.view_product_plan, name='view_product_plan'),
    path('change_product/<int:id>/', product_views.change_product, name='change_product'),
    path('add_plan', product_views.add_plan, name='add_plan'),
    path('view_plan', product_views.view_plan, name='view_plan'),
    path('change_plan/<int:id>/', product_views.change_plan, name='change_plan'),
    path('view_plan/<int:id>', product_views.view_specific_plan, name='view_specific_plan')
    ]