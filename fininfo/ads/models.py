from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit import ImageSpec
from imagekit import register
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from imagekit.utils import get_field_info

from fininfo.core.models import TimeStampedModel


class AdType(TimeStampedModel):
    """
    Type for ads, act like category
    """

    name = models.CharField(max_length=256, verbose_name=_("Nomi"))
    width = models.SmallIntegerField(verbose_name=_("Rasm eni"))
    height = models.SmallIntegerField(verbose_name=_("Rasm balandligi"))
    slug = models.SlugField(max_length=256, verbose_name=_("Slug"))

    class Meta:
        verbose_name = _("Reklama turi")
        verbose_name_plural = _("Reklamalar turi")

    def __str__(self) -> str:
        return self.name


class CustomImageSpec(ImageSpec):
    format = "webp"
    options = {"quality": 90}

    @property
    def processors(self):
        model, field_name = get_field_info(self.source)
        width = model.ad_type.width
        height = model.ad_type.height
        return [ResizeToFill(width, height)]


register.generator("paradigma:ads:resized_image", CustomImageSpec)


class Ad(TimeStampedModel):
    ad_type = models.ForeignKey(
        to=AdType,
        on_delete=models.CASCADE,
        related_name="ad",
        verbose_name=_("Reklama turi"),
    )
    name = models.CharField(max_length=256, verbose_name=_("Nomi"))
    image = models.ImageField(upload_to="ads", verbose_name=_("Rasm"))
    resized_image = ImageSpecField(source="image", id="paradigma:ads:resized_image")
    link = models.URLField(max_length=512, verbose_name=_("Havola"))
    max_views = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Maksimal ko'rishlar soni"),
    )
    max_clicks = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Maksimak bosishlar soni"),
    )
    is_active = models.BooleanField(default=False, verbose_name=_("Holati"))

    class Meta:
        verbose_name = _("Reklama")
        verbose_name_plural = _("Reklamalar")

    def resize_processors(self):
        """Dynamic size lookup."""

        width = self.category.width
        height = self.category.height
        return [
            ResizeToFill(width=width, height=height),
        ]

    def __str__(self) -> str:
        return self.name


class AdStat(TimeStampedModel):
    """
    Statistics model for ads
    """

    class StatType(models.TextChoices):
        VIEWS = "views", _("Ko'rishlar")
        CLICKS = "clicks", _("Bosishlar")

    ad = models.ForeignKey(
        to=Ad,
        on_delete=models.CASCADE,
        related_name="ad_stat",
        verbose_name=_("Reklama"),
    )
    stat_type = models.CharField(
        max_length=10,
        choices=StatType.choices,
        verbose_name=_("Statistika turi"),
    )

    class Meta:
        verbose_name = _("Statistika")
        verbose_name_plural = _("Statistika")
