from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('USER', 'User'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=5, choices=ROLE_CHOICES, default='USER')

    def is_admin_user(self):
        return self.role == 'ADMIN' or self.is_superuser

# Create your models here.
