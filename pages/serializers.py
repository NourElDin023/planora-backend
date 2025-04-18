from rest_framework import serializers
from .models import Page


class PageShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ["owner", "shareable_link_token"]


class LinkShareSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["is_link_shareable", "shareable_permission"]
        extra_kwargs = {
            "shareable_permission": {"required": True},
            "is_link_shareable": {"required": True},
        }
