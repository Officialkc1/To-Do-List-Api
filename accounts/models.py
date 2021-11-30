from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# Create your models here.

class CustomUser(AbstractUser):
    address = models.TextField(null=True, blank=True)
    id=models.UUIDField(primary_key=True, unique=True,editable=False, default=uuid.uuid4)
    def __str__(self):
        return self.username