from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('create/',             views.ticket_create,    name='create'),
    path('inbox/',              views.inbox_view,       name='inbox'),
    path('admin/inbox/',        views.admin_inbox,      name='admin_inbox'),
    path('admin/outbox/',       views.admin_outbox,     name='admin_outbox'),
    path('admin/<int:pk>/reply/', views.admin_reply,    name='admin_reply'),
    path('api/create/',         views.TicketCreateAPIView.as_view(),    name='api_create'),
    path('api/list/',           views.TicketListAPIView.as_view(),      name='api_list'),
    path('api/admin/list/',     views.AdminTicketListAPIView.as_view(), name='api_admin_list'),
    path('api/admin/<int:pk>/reply/', views.AdminTicketReplyAPIView.as_view(), name='api_admin_reply'),
]
