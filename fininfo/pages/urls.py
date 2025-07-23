from django.urls import path

from fininfo.pages.views import PageRetrieveViewSet

app_name = "pages"

urlpatterns = [
    path(
        "<slug:slug>/",
        PageRetrieveViewSet.as_view({"get": "retrieve"}),
        name="retrieve",
    ),
]
