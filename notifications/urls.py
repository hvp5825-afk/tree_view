from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('add/',              views.add_notification,   name='add'),
    path('delete/<int:pk>/',  views.delete_notification, name='delete'),
    path('qrcode/',           views.add_qrcode,         name='qrcode'),
    path('qrcode/delete/<int:pk>/', views.delete_qrcode, name='delete_qrcode'),
    path('api/list/',         views.NotificationListAPIView.as_view(), name='api_list'),
    path('api/qrcodes/',      views.QRCodeListAPIView.as_view(),       name='api_qrcodes'),
]
