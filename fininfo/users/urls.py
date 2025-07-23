from django.urls import path

from fininfo.users.views import TelegramAuthView

app_name = "users"

urlpatterns = [
    path(
        "auth/",
        TelegramAuthView.as_view(),
        name="create",
    ),
]