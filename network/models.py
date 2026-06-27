from django.db import models
from django.conf import settings
from django.utils import timezone


class Referral(models.Model):
    POSITION_CHOICES = [('LEFT', 'Left'), ('RIGHT', 'Right')]

    sponsor     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sponsored_members')
    member      = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_info')
    parent      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    position    = models.CharField(max_length=5, choices=POSITION_CHOICES)
    joining_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'referrals'

    def __str__(self):
        return f"{self.member.member_id} under {self.sponsor.member_id} ({self.position})"
