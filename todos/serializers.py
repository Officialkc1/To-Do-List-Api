from rest_framework import serializers
from . models import Todo

class TodoSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField()
    class Meta:
        model = Todo
        fields = ('id', 'user','user_name', 'title', 'body', 'date',)

class FutureSerializer(serializers.Serializer):
    date = serializers.DateField()