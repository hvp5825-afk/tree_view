from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('add/',                  views.add_product,            name='add'),
    path('manage/',               views.manage_products,        name='manage'),
    path('edit/<int:pk>/',        views.edit_product,           name='edit'),
    path('toggle/<int:pk>/',      views.toggle_product_status,  name='toggle'),
    path('settings/',             views.project_settings,       name='settings'),
]
