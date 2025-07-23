from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from parler.models import TranslatableModel
from parler.models import TranslatedFields

from fininfo.core.models import TimeStampedModel


class Page(TimeStampedModel, TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(
            max_length=255,
            db_index=True,
            verbose_name=_("Sarlavha"),
        ),
        short_content=CKEditor5Field(verbose_name=_("Qisqa matn (Lid)")),
        content=CKEditor5Field(
            config_name="extends",
            verbose_name=_("Kontent"),
        ),
    )
    slug = models.SlugField(max_length=255, db_index=True)
    image = ProcessedImageField(
        upload_to="pages/",
        format="webp",
        processors=[ResizeToFit(804)],
        options={"quality": 90},
        null=True,
        blank=True,
    )
    video = models.FileField(
        upload_to="video/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                [
                    "mp4",
                    "mov",
                    "gif",
                ],
            ),
        ],
        verbose_name=_("Video"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Holati"))

    class Meta:
        verbose_name = _("Sahifa")
        verbose_name_plural = _("Sahifalar")

    def __str__(self) -> str:
        return self.name
