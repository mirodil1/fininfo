from rest_framework import serializers


class TelegramLoginSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    photo_url = serializers.URLField(required=False)
    auth_date = serializers.IntegerField()
    hash = serializers.CharField()
