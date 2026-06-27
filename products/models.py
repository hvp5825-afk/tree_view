from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField


class Product(models.Model):
    title      = models.CharField(max_length=200)
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    color      = models.CharField(max_length=50, blank=True)
    size       = models.CharField(max_length=50, blank=True)
    image      = models.ImageField(upload_to='products/', blank=True, null=True)
    details    = RichTextField(blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"


class ProjectSetting(models.Model):
    title    = models.CharField(max_length=200)
    status   = models.BooleanField(default=True)
    amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mark     = models.CharField(max_length=100, blank=True)
    reward   = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'project_settings'

    def __str__(self):
        return self.title
