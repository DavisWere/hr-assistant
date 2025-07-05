from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    first_name = models.CharField(max_length=40, null=False)
    last_name = models.CharField(max_length=40, null=False)
    department = models.CharField(max_length=255, null=False)
    role = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Sets when created
    updated_at = models.DateTimeField(auto_now=True)      # Updates on save

    def __str__(self):
        return self.username

#q