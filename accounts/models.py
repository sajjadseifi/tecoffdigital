from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.db import models
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from .managers import UserManager
from django.conf import settings


class User(AbstractBaseUser, PermissionsMixin):
    active_catalog = models.ForeignKey(
        "catalog.Catalog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )
    phone = PhoneNumberField(unique=True)

    email = models.EmailField(unique=True, null=True, blank=True)

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    avatar = models.ImageField(upload_to="users/avatar/", null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    login_count = models.PositiveIntegerField(default=0)

    last_activity = models.DateTimeField(null=True, blank=True)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.display_name} [{self.phone}]"

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}".strip() or str(self.phone)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "مدیریت کاربران"


class OTP(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps",
        null=True,
        blank=True
    )

    phone = PhoneNumberField()
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "کد ورود"
        verbose_name_plural = "کد های ورود"