from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratildi"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("O'zgartirildi"))

    class Meta:
        abstract = True
