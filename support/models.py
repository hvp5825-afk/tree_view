from django.db import models
from django.conf import settings
from django.utils import timezone


class SupportTicket(models.Model):
    STATUS_CHOICES = [('open', 'Open'), ('replied', 'Replied'), ('closed', 'Closed')]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    subject    = models.CharField(max_length=255)
    message    = models.TextField()
    attachment = models.FileField(upload_to='support/', blank=True, null=True)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    reply      = models.TextField(blank=True)
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(default=timezone.now)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket: {self.user.member_id} - {self.subject}"
