from django.db import models
from django.conf import settings
from django.utils import timezone


class KYCRequest(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]

    user           = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kyc')
    aadhaar_number = models.CharField(max_length=12, blank=True)
    pan_number     = models.CharField(max_length=10, blank=True)
    aadhaar_file   = models.FileField(upload_to='kyc/aadhaar/', blank=True, null=True)
    pan_file       = models.FileField(upload_to='kyc/pan/', blank=True, null=True)
    bank_file      = models.FileField(upload_to='kyc/bank/', blank=True, null=True)
    photo_file     = models.ImageField(upload_to='kyc/photos/', blank=True, null=True)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    remarks        = models.TextField(blank=True)
    submitted_at   = models.DateTimeField(default=timezone.now)
    reviewed_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'kyc_requests'

    def __str__(self):
        return f"KYC: {self.user.member_id} [{self.status}]"
