from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, permissions
from rest_framework.response import Response


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )




