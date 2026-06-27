from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',            views.login_view,            name='login'),
    path('logout/',           views.logout_view,           name='logout'),
    path('profile/',          views.profile_view,          name='profile'),
    path('profile/edit/',     views.edit_profile_view,     name='edit_profile'),
    path('password/change/',  views.change_password_view,  name='change_password'),
    path('associates/',                views.associate_list_view,  name='associate_list'),
    path('add-member/',                views.admin_add_member,     name='add_member'),
    path('associates/<int:pk>/toggle/', views.toggle_user_status,  name='toggle_user_status'),
    path('associates/<int:pk>/remove/',  views.remove_member,       name='remove_member'),
    path('associates/<int:pk>/delete/',  views.delete_member,       name='delete_member'),
    path('removed-members/',             views.removed_members_list, name='removed_members'),
    path('download/id-card/',         views.download_id_card,         name='download_id_card'),
    path('download/welcome-letter/',  views.download_welcome_letter, name='download_welcome_letter'),
    path('download/joining-letter/',  views.download_joining_letter, name='download_joining_letter'),
    path('preview/id-card/',          views.preview_id_card,         name='preview_id_card'),
    path('preview/welcome-letter/',   views.preview_welcome_letter,  name='preview_welcome_letter'),
    path('preview/joining-letter/',   views.preview_joining_letter,  name='preview_joining_letter'),
    path('api/register/',  views.RegisterAPIView.as_view(),      name='api_register'),
    path('api/login/',     views.LoginAPIView.as_view(),         name='api_login'),
    path('api/logout/',    views.LogoutAPIView.as_view(),        name='api_logout'),
    path('api/profile/',   views.ProfileAPIView.as_view(),       name='api_profile'),
    path('api/password/',  views.ChangePasswordAPIView.as_view(), name='api_password'),
]
