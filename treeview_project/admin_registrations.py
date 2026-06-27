from django.contrib import admin
from network.models import Referral
from kyc.models import KYCRequest
from pmf.models import PMFRequest
from helpdesk.models import SendHelpRequest, ReceiveHelpRequest
from rewards.models import Reward
from support.models import SupportTicket
from notifications.models import Notification, QRCode
from products.models import Product, ProjectSetting


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display  = ['member', 'sponsor', 'parent', 'position', 'joining_date']
    search_fields = ['member__member_id', 'sponsor__member_id']
    list_filter   = ['position']


@admin.register(KYCRequest)
class KYCAdmin(admin.ModelAdmin):
    list_display  = ['user', 'pan_number', 'aadhaar_number', 'status', 'submitted_at']
    list_filter   = ['status']
    search_fields = ['user__member_id']


@admin.register(PMFRequest)
class PMFAdmin(admin.ModelAdmin):
    list_display  = ['user', 'amount', 'transaction_no', 'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['user__member_id']


@admin.register(SendHelpRequest)
class SendHelpAdmin(admin.ModelAdmin):
    list_display  = ['user', 'request_to', 'amount', 'status', 'created_at']
    list_filter   = ['status']


@admin.register(ReceiveHelpRequest)
class ReceiveHelpAdmin(admin.ModelAdmin):
    list_display  = ['user', 'amount', 'status', 'created_at']
    list_filter   = ['status']


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display  = ['user', 'reward_name', 'reward_type', 'reward_amount', 'status']
    list_filter   = ['status', 'reward_type']


@admin.register(SupportTicket)
class SupportAdmin(admin.ModelAdmin):
    list_display  = ['user', 'subject', 'status', 'created_at']
    list_filter   = ['status']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['notif_type', 'user', 'message', 'created_at']


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display  = ['title', 'qr_type', 'bank_name', 'created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['title', 'amount', 'color', 'size', 'is_active', 'created_at']
    list_filter   = ['is_active']


@admin.register(ProjectSetting)
class ProjectSettingAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'amount', 'mark', 'reward']
