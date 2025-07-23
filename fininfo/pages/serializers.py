from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers

from fininfo.core.serializers import TranslatedSerializerMixin
from fininfo.pages.models import Page


class PageSerializer(TranslatedSerializerMixin, TranslatableModelSerializer):
    translations = TranslatedFieldsField()
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Page
        fields = [
            "id",
            "translations",
            "slug",
            "image",
            "video",
        ]
