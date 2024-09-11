from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework.viewsets import ModelViewSet

from app_splitting_access.models import Adv
from app_splitting_access.permissions import IsOwnerOrReadOnly
from app_splitting_access.serializers import AdvSerializer


# Create your views here.
class AdvViewSet(ModelViewSet):
    queryset = Adv.objects.all()
    serializer_class = AdvSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    throttle_classes = [AnonRateThrottle]

    def perform_create(self, serializer):
        user_name = self.request.user.username
        text = serializer.validated_data['text']
        text_with_user = text.replace('{{ user }}', user_name)
        serializer.save(user=self.request.user, text=text_with_user)
