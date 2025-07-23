import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "fininfo.users"
    verbose_name = _("Foydalanuvchilar")

    def ready(self):
        with contextlib.suppress(ImportError):
            import fininfo.users.signals  # noqa: F401
