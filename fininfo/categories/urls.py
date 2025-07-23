from django.urls import path

from fininfo.categories.views import CategoryView

app_name = "categories"

urlpatterns = [
    path("list/", CategoryView.as_view(), name="list"),
]
