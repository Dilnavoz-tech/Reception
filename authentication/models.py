from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

ROLE_CHOICES = (
    (1, 'Admin'),
    (2, 'Doctor'),
    (3, 'Patient'),
)


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    role = models.IntegerField(choices=ROLE_CHOICES, default=1)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # after soft delete assigns unique token, preventing user exist error in register new user
        if self.is_deleted:
            self.username = f"{self.username}-{uuid.uuid4()}"
        super().save(*args, **kwargs)


class BlacklistedAccessToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

