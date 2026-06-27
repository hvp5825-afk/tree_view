from django.db import models
from django.conf import settings
from django.utils import timezone


class PMFRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('product_accepted', 'Product Accepted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('dispatched', 'Dispatched'),
    ]

    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pmf_requests')
    amount        = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_no = models.CharField(max_length=100, blank=True)
    payment_proof = models.FileField(upload_to='pmf/proofs/', blank=True, null=True)
    level         = models.PositiveIntegerField(default=1)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks       = models.TextField(blank=True)
    created_at    = models.DateTimeField(default=timezone.now)
    reply_date    = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pmf_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"PMF: {self.user.member_id} - {self.amount} [{self.status}]"
