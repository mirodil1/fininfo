from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers
from taggit.serializers import TaggitSerializer
from taggit.serializers import TagListSerializerField

from fininfo.categories.serializers import CategorySerializer
from fininfo.core.serializers import TranslatedSerializerMixin
from fininfo.news.models import News
from fininfo.news.models import NewsGallery
from fininfo.news.models import Comment


class NewsGallerySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = NewsGallery
        fields = [
            "image",
        ]


class CommentSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Comment
        fields = [
            "user",
            "body",
        ]


class NewsSerializer(
    TaggitSerializer,
    TranslatedSerializerMixin,
    TranslatableModelSerializer,
):
    translations = TranslatedFieldsField()
    category = CategorySerializer()
    tags = TagListSerializerField()
    image_large = serializers.ImageField(read_only=True)
    image_medium = serializers.ImageField(read_only=True)
    image_small = serializers.ImageField(read_only=True)
    gallery = NewsGallerySerializer(many=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = News
        fields = [
            "id",
            "translations",
            "category",
            "tags",
            "title",
            "short_content",
            "content",
            "slug",
            "news_status",
            "publish",
            "number_of_views",
            "comments",
            "is_pinned",
            "author_choice",
            "image_large",
            "image_medium",
            "image_small",
            "image_source",
            "image_name",
            "gallery",
            "short_slug",
        ]

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # if self.fields_arg:
        # Filter out the fields not specified
        data = {field: data[field] for field in self.fields if field in data}
        if data:
            if data == {}:
                del data
        return data


class CommentCreateSerializer(serializers.ModelSerializer):
    news = serializers.PrimaryKeyRelatedField(queryset=News.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Comment

        fields = [
            "news",
            "user",
            "body",
        ]
