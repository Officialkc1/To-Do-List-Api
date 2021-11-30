from django.contrib import admin
from django.contrib.auth import get_user_model
from . models import CustomUser
# Register your models here.

User = get_user_model()

# Registering Models.
admin.site.register(User)

