from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "updated_at", "task", "user"]
        read_only_fields = ["id", "created_at", "updated_at", "user"]

    def get_user(self, obj):
        return obj.user.username
