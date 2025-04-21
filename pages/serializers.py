from rest_framework import serializers
from .models import Collection


class CollectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "title", "description", "is_link_shareable", "shareable_permission"]


class CollectionShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"
        read_only_fields = ["owner", "shareable_link_token"]


class LinkShareSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["is_link_shareable", "shareable_permission"]
        extra_kwargs = {
            "shareable_permission": {"required": True},
            "is_link_shareable": {"required": True},
        }
