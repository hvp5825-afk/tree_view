from django.urls import path
from . import views

app_name = 'helpdesk'

urlpatterns = [
    path('send/',               views.send_help_view,       name='send'),
    path('send/history/',       views.send_help_history,    name='send_history'),
    path('receive/',            views.receive_help_view,    name='receive'),
    path('receive/history/',    views.receive_help_history, name='receive_history'),
    path('admin/',              views.admin_help_list,      name='admin_list'),
    path('admin/<int:pk>/action/', views.admin_help_action, name='admin_action'),
    path('api/send/',           views.SendHelpCreateAPIView.as_view(),  name='api_send'),
    path('api/send/list/',      views.SendHelpListAPIView.as_view(),    name='api_send_list'),
    path('api/receive/',        views.ReceiveHelpCreateAPIView.as_view(), name='api_receive'),
    path('api/admin/<int:pk>/action/', views.AdminHelpActionAPIView.as_view(), name='api_admin_action'),
]
