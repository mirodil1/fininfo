from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel
from parler.models import TranslatedFields

from fininfo.core.models import TimeStampedModel
from fininfo.utils.transliterate import to_latin


class Category(TimeStampedModel, TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=64, verbose_name=_("Nomi")),
        slug=models.SlugField(max_length=64, db_index=True, verbose_name=_("Slug")),
        description=models.TextField(null=True, blank=True, verbose_name=_("Ta'rif")),
        meta={"unique_together": [("slug", "language_code")]},
    )
    is_menu = models.BooleanField(default=False, verbose_name=_("Menyu"))
    category_order = models.PositiveIntegerField(default=0, db_index=True)
    icon = models.FileField(
        upload_to='category/icons',
        blank=True,
        null=True,
        verbose_name=_("Ikonka"),
    )
    image = models.ImageField(
        upload_to='category/images',
        blank=True,
        null=True,
        verbose_name=_("Rasm")
    )

    class Meta:
        verbose_name = _("Bo'lim")
        verbose_name_plural = _("Bo'limlar")
        ordering = ["category_order"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(to_latin(self.name))
        return super().save(*args, **kwargs)
