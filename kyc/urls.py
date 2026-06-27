from django.urls import path
from . import views

app_name = 'kyc'

urlpatterns = [
    path('submit/',         views.kyc_submit_view,  name='submit'),
    path('status/',         views.kyc_status_view,  name='status'),
    path('admin/',          views.admin_kyc_list,   name='admin_list'),
    path('admin/<int:pk>/action/', views.admin_kyc_action, name='admin_action'),
    # API
    path('api/submit/',     views.KYCSubmitAPIView.as_view(),  name='api_submit'),
    path('api/list/',       views.KYCListAPIView.as_view(),    name='api_list'),
    path('api/<int:pk>/action/', views.KYCActionAPIView.as_view(), name='api_action'),
]
