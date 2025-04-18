from rest_framework import serializers
from .models import SharedPage


class SharedPageSerializer(serializers.ModelSerializer):
    shared_with_username = serializers.CharField(source="shared_with.username", read_only=True)

    class Meta:
        model = SharedPage
        fields = ["page", "shared_with", "shared_with_username", "permission"]
