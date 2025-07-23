import ast

from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters.widgets import CSVWidget
from taggit.managers import TaggableManager

from fininfo.news.models import News


class NewsFilter(filters.FilterSet):
    categories = filters.CharFilter(
        widget=CSVWidget(),
        method="has_category_filter",
        label="Comma-separated values",
    )
    youtube = filters.BooleanFilter(
        label="youtube",
        method="has_youtube_filter",
    )
    tags = filters.CharFilter(
        field_name="translations__tags__name",
    )

    class Meta:
        model = News
        fields = ["is_pinned", "author_choice", "tags"]

        filter_overrides = {
            TaggableManager: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "in",
                },
            },
        }

    def has_youtube_filter(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(youtube_link__isnull=False),
                ~Q(youtube_link=""),
            )
        return queryset.filter(Q(youtube_link__isnull=True) | Q(youtube_link=""))

    def has_category_filter(self, queryset, name, value):
        if value:
            categories_list = ast.literal_eval(value)
            return (
                queryset.select_related("category")
                .prefetch_related(
                    "translations",
                    "tags",
                    "translations__tags",
                    "category__translations",
                    "gallery",
                )
                .filter(category__translations__slug__in=categories_list)
            )
        return queryset
