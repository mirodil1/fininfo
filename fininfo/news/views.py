from datetime import timedelta
from typing import Any

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from fininfo.news.filters import NewsFilter
from fininfo.news.models import News, Comment
from fininfo.news.serializers import NewsSerializer, CommentCreateSerializer


def view_incrementer(view_func):
    """A decorator which increments news views"""

    def _wrapped(*args, **kwargs):
        # kwargs will contain URL parameters
        slug = kwargs.get("slug") or kwargs.get("short_slug")
        News.objects.filter(Q(translations__slug=slug) | Q(short_slug=slug)).update(
            number_of_views=F("number_of_views") + 1,
        )
        return view_func(*args, **kwargs)

    return _wrapped


@extend_schema(tags=["news"])
class NewsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = (
        News.objects.all()
        .select_related("category")
        .prefetch_related(
            "translations",
            "tags",
            "translations__tags",
            "category__translations",
            "gallery",
        )
    )
    serializer_class = NewsSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = [
        "translations__title",
        "translations__short_content",
        "translations__content",
    ]
    filterset_class = NewsFilter
    ordering_fields = ["publish", "number_of_views"]

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        language_code = get_language()
        return (
            qs.filter(
                news_status=News.NewsStatus.PUBLISHED,
                publish__lte=timezone.now(),
                translations__language_code=language_code,
            )
            .order_by("-publish")
            .distinct()
        )

    @method_decorator(view_incrementer)
    @method_decorator(cache_page(60 * 60 * 24))
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data["languages"] = instance.get_available_languages()
        return Response(data)

    def get_object(self):
        queryset = self.get_queryset()
        slug = self.kwargs.get("slug")
        short_slug = self.kwargs.get("short_slug")
        language_code = get_language()

        # Filter queryset based on slug and language_code
        filters = {"translations__language_code": language_code}
        if slug:
            filters["translations__slug"] = slug
        elif short_slug:
            filters["short_slug"] = short_slug
        obj = get_object_or_404(queryset, **filters)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj


@extend_schema(tags=["news"])
class RelatedNewsViewSet(ListModelMixin, GenericViewSet):
    queryset = (
        News.objects.all()
        .select_related("category")
        .prefetch_related(
            "translations",
            "tags",
            "translations__tags",
            "category__translations",
            "gallery",
        )
    )
    serializer_class = NewsSerializer

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        language_code = get_language()
        return (
            qs.filter(
                news_status=News.NewsStatus.PUBLISHED,
                publish__lte=timezone.now(),
                translations__language_code=language_code,
            )
            .order_by("-publish")
            .distinct()
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.get_queryset()
        filtered_qs = queryset.annotate(
            tag_ids=ArrayAgg("translations__tags__id", distinct=True),
        ).values("publish", "tag_ids")

        news_pk = self.kwargs.get("news_id")
        news = get_object_or_404(filtered_qs, pk=news_pk)

        news_tags_ids = news["tag_ids"]

        similar_news = (
            queryset.filter(translations__tags__in=news_tags_ids)
            .select_related("category")
            .prefetch_related(
                "translations",
                "tags",
                "translations__tags",
                "category__translations",
                "gallery",
            )
            .exclude(pk=news_pk)
            .annotate(same_tags=Count("translations__tags"))
            .order_by("-same_tags", "-publish")
        )[:6]

        next_news = (
            queryset.filter(
                publish__gt=news["publish"],
            )
            .order_by("publish")
            .first()
        )

        prev_news = (
            queryset.filter(
                publish__lt=news["publish"],
            )
            .order_by("-publish")
            .first()
        )

        similar_news_serializer = self.get_serializer(
            similar_news,
            many=True,
            fields=["id", "title", "slug", "category", "image_medium", "image_large", "publish"],
        )
        next_news_serializer = (
            self.get_serializer(
                next_news,
                fields=["id", "title", "slug", "image_small", "publish"],
            ).data
            if next_news
            else None
        )
        prev_news_serializer = (
            self.get_serializer(
                prev_news,
                fields=["id", "title", "slug", "image_small", "publish"],
            ).data
            if prev_news
            else None
        )
        return Response(
            {
                "similar": similar_news_serializer.data,
                "next_news": next_news_serializer,
                "prev_news": prev_news_serializer,
            },
        )


class PopularNewsViewSet(ListModelMixin, GenericViewSet):
    queryset = (
        News.objects.all()
        .select_related("category")
        .prefetch_related(
            "translations",
            "tags",
            "translations__tags",
            "category__translations",
            "gallery",
        )
    )
    serializer_class = NewsSerializer

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        language_code = get_language()
        return (
            qs.filter(
                news_status=News.NewsStatus.PUBLISHED,
                publish__lte=timezone.now(),
                translations__language_code=language_code,
            )
            .order_by("-publish")
            .distinct()
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.get_queryset()

        d = timezone.now() - timedelta(days=7)
        news = queryset.filter(
            publish__gte=d,
            number_of_views__gte=1,
        ).order_by("-number_of_views")

        page = self.paginate_queryset(news)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                fields=[
                    "id",
                    "title",
                    "short_content",
                    "category",
                    "slug",
                    "image_small",
                    "image_large",
                    "publish",
                ],
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            news,
            many=True,
            fields=[
                "id",
                "title",
                "short_content",
                "category",
                "slug",
                "image_small",
                "publish",
            ],
        )

        return Response(serializer.data)


class CommentCreateViewSet(CreateModelMixin, GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]