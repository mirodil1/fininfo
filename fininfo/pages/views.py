from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from fininfo.pages.models import Page
from fininfo.pages.serializers import PageSerializer


class PageRetrieveViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = PageSerializer
    queryset = Page.objects.filter(is_active=True)
    lookup_field = "slug"
