from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"

class User(AbstractUser):
    role = models.CharField(max_length=20,
                            choices=UserRole.choices,
                            default=UserRole.USER)

    def __str__(self):
        return self.username