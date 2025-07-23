from django.urls import path

from fininfo.news.views import NewsViewSet
from fininfo.news.views import PopularNewsViewSet
from fininfo.news.views import RelatedNewsViewSet
from fininfo.news.views import CommentCreateViewSet

app_name = "news"

urlpatterns = [
    path(
        "all/",
        NewsViewSet.as_view({"get": "list"}),
        name="list",
    ),
    path(
        "popular/",
        PopularNewsViewSet.as_view({"get": "list"}),
        name="popular",
    ),
    path(
        "<str:slug>/",
        NewsViewSet.as_view({"get": "retrieve"}),
        name="detail",
    ),
    path(
        "short_slug/<str:short_slug>/",
        NewsViewSet.as_view({"get": "retrieve"}),
        name="detail",
    ),
    path(
        "similar/<int:news_id>",
        RelatedNewsViewSet.as_view({"get": "list"}),
        name="related",
    ),
    path(
        "comment/publish/",
        CommentCreateViewSet.as_view({"post": "create"}),
        name="comment",
    ),
]
