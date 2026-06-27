from django.db import models
from django.conf import settings
from django.utils import timezone


class Reward(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    TYPE_CHOICES   = [('product', 'Product'), ('cash', 'Cash')]

    user               = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rewards')
    reward_name        = models.CharField(max_length=200)
    reward_type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    reward_amount      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qualification_date = models.DateTimeField(default=timezone.now)
    status             = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    remarks            = models.TextField(blank=True)

    class Meta:
        db_table = 'rewards'
        ordering = ['-qualification_date']

    def __str__(self):
        return f"Reward: {self.user.member_id} - {self.reward_name}"
