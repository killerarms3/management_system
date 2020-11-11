from django.urls import path
import product.views as product_views

app_name = 'product'
urlpatterns=[
    path('product/add', product_views.add_product, name='add_product'),
    path('product', product_views.view_product, name='view_product'),
    path('product/<int:id>', product_views.view_product_plan, name='view_product_plan'),
    path('product/edit/<int:id>/', product_views.change_product, name='change_product'),
    path('plan/add', product_views.add_plan, name='add_plan'),
    path('plan', product_views.view_plan, name='view_plan'),
    path('plan/edit/<int:id>/', product_views.change_plan, name='change_plan'),
    path('plan/<int:id>', product_views.view_specific_plan, name='view_specific_plan')
    ]



