from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    telegram_id = models.CharField(
        max_length=255,
        verbose_name=_("Telegram ID"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Foydalanuvchi")
        verbose_name_plural = _("Foydalanuvchilar")
