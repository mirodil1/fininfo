from django.db.models.query import QuerySet
from django.utils.translation import get_language
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from fininfo.categories.models import Category
from fininfo.categories.serializers import CategorySerializer


@extend_schema(tags=["categories"])
class CategoryView(ListModelMixin, GenericAPIView):
    queryset = Category.objects.filter(is_menu=True).prefetch_related("translations")
    serializer_class = CategorySerializer

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        language = get_language()
        return qs.filter(translations__language_code=language)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
