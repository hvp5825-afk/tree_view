from django.db import models
from django.conf import settings
from django.utils import timezone


class SendHelpRequest(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    PAYMENT_CHOICES = [('gpay', 'GPay'), ('phonepe', 'PhonePe'), ('paytm', 'Paytm'), ('upi', 'UPI'), ('bank', 'Bank Transfer')]

    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='send_help_requests')
    request_to     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_help_payments')
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    transaction_no = models.CharField(max_length=100, blank=True)
    proof_file     = models.FileField(upload_to='helpdesk/send/', blank=True, null=True)
    remarks        = models.TextField(blank=True)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at     = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'send_help_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"SendHelp: {self.user.member_id} -> {self.request_to} [{self.status}]"


class ReceiveHelpRequest(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receive_help_requests')
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'receive_help_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"ReceiveHelp: {self.user.member_id} - {self.amount} [{self.status}]"
