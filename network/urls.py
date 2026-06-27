from django.urls import path
from . import views

app_name = 'network'

urlpatterns = [
    path('tree/',      views.tree_view,     name='tree'),
    path('referrals/', views.referrals_view, name='referrals'),
    path('api/tree/',  views.TreeAPIView.as_view(), name='api_tree'),
]
