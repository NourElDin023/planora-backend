from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['user']
