from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    TYPE_CHOICES = [('global', 'Global'), ('individual', 'Individual')]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    notif_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='global')
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif [{self.notif_type}]: {self.message[:50]}"


class QRCode(models.Model):
    TYPE_CHOICES = [('gpay', 'GPay'), ('phonepe', 'PhonePe'), ('paytm', 'Paytm'), ('bank', 'Bank')]

    title        = models.CharField(max_length=100)
    bank_name    = models.CharField(max_length=150, blank=True)
    account_no   = models.CharField(max_length=50, blank=True)
    ifsc_code    = models.CharField(max_length=20, blank=True)
    account_holder = models.CharField(max_length=150, blank=True)
    qr_image     = models.ImageField(upload_to='qrcodes/')
    qr_type      = models.CharField(max_length=10, choices=TYPE_CHOICES, default='bank')
    created_at   = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'qr_codes'

    def __str__(self):
        return f"QR: {self.title}"
