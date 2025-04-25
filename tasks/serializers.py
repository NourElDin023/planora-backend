from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = [
            "owner",
            "created_at",
            "updated_at",
        ]

    def get_owner(self, obj):
        return obj.owner.username
