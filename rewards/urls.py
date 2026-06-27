from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
    path('',                        views.rewards_view,        name='list'),
    path('admin/',                  views.admin_rewards_list,  name='admin_list'),
    path('admin/<int:pk>/action/',  views.admin_reward_action, name='admin_action'),
    path('api/list/',               views.RewardListAPIView.as_view(),       name='api_list'),
    path('api/admin/list/',         views.AdminRewardListAPIView.as_view(),  name='api_admin_list'),
]
