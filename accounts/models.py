from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import random, string


def generate_member_id():
    return 'UPN' + ''.join(random.choices(string.digits, k=4))


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra):
        if not email:
            raise ValueError('Email required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('is_active', True)
        return self.create_user(username, email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending')]

    member_id   = models.CharField(max_length=20, unique=True, default=generate_member_id)
    sponsor_id  = models.CharField(max_length=20, blank=True, null=True)
    username    = models.CharField(max_length=150, unique=True)
    email       = models.EmailField(unique=True)
    mobile      = models.CharField(max_length=15, blank=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    plain_password = models.CharField(max_length=128, blank=True)  # stored for admin view
    created_at  = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.member_id} - {self.username}"

    def get_full_name(self):
        profile = getattr(self, 'profile', None)
        if profile:
            return f"{profile.first_name} {profile.last_name}".strip()
        return self.username


class UserProfile(models.Model):
    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name   = models.CharField(max_length=100, blank=True)
    last_name    = models.CharField(max_length=100, blank=True)
    address      = models.TextField(blank=True)
    city         = models.CharField(max_length=100, blank=True)
    state        = models.CharField(max_length=100, blank=True)
    country      = models.CharField(max_length=100, blank=True, default='India')
    pincode      = models.CharField(max_length=10, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bank_name    = models.CharField(max_length=150, blank=True)
    account_holder = models.CharField(max_length=150, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    ifsc_code    = models.CharField(max_length=20, blank=True)
    gpay         = models.CharField(max_length=20, blank=True)
    phonepe      = models.CharField(max_length=20, blank=True)
    paytm        = models.CharField(max_length=20, blank=True)
    upi_id       = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"Profile: {self.user.member_id}"
