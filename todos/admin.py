from django.contrib import admin
from . models import Todo

# Registering our Todo Model
@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['id','title','body', 'date']
    search_field = ['title', 'id']