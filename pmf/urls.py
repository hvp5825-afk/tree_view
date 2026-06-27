from django.urls import path
from . import views

app_name = 'pmf'

urlpatterns = [
    path('pay/',            views.pmf_pay_view,       name='pay'),
    path('history/',        views.pmf_history_view,   name='history'),
    path('admin/',          views.admin_pmf_list,     name='admin_list'),
    path('admin/<int:pk>/action/', views.admin_pmf_action, name='admin_action'),
    path('api/create/',     views.PMFCreateAPIView.as_view(),  name='api_create'),
    path('api/list/',       views.PMFListAPIView.as_view(),    name='api_list'),
    path('api/<int:pk>/action/', views.PMFActionAPIView.as_view(), name='api_action'),
]
