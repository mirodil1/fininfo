from rest_framework import serializers

from fininfo.ads.models import Ad
from fininfo.ads.models import AdType


class AdSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(read_only=True, source="resized_image")

    class Meta:
        model = Ad
        fields = ["id", "name", "image", "link"]


class AdTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdType
        fields = ["name", "slug"]
