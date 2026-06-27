from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['member_id', 'username', 'email', 'mobile', 'status', 'is_staff', 'created_at']
    list_filter   = ['status', 'is_staff']
    search_fields = ['member_id', 'username', 'email']
    ordering      = ['-created_at']
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('MLM Info', {'fields': ('member_id', 'sponsor_id', 'mobile', 'status', 'plain_password')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('MLM Info', {'fields': ('member_id', 'sponsor_id', 'mobile', 'status')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'city', 'state', 'country']
    search_fields = ['user__member_id', 'user__username']
