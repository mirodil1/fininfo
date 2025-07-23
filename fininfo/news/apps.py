import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fininfo.news"
    verbose_name = _("Yangiliklar")

    def ready(self):
        with contextlib.suppress(ImportError):
            import fininfo.news.signals  # noqa: F401
