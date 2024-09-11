from django.contrib.auth.models import User
from rest_framework import serializers

from app_splitting_access.models import Adv

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
class AdvSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Adv
        fields = ['id', 'user', 'text', 'created_at', 'open']

        read_only_fields = ['user',]