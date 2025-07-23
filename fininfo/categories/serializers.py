from parler_rest.serializers import TranslatableModelSerializer

from fininfo.categories.models import Category
from fininfo.core.serializers import TranslatedSerializerMixin


class CategorySerializer(TranslatedSerializerMixin, TranslatableModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "image",
        ]
